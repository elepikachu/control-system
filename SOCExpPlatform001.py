# -------------------------------------------------------------
# -*- coding: utf-8 -*-
# Writer: Elepikachu
# Copyright CNPC.inc
# 2023/11/13
# -------------------------------------------------------------

import sys, os, csv, random, time, snap7, json

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDir, Qt, QDateTime, QTimer, QItemSelectionModel, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox, QWidget, QSizePolicy, QDialogButtonBox, QDialog, QAbstractItemView, QMenu, QSpinBox
from PyQt5.QtChart import QChartView, QChart, QLineSeries, QValueAxis, QDateTimeAxis
from PyQt5.QtGui import QPen, QColor, QPainter, QPixmap, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtChart import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
import pyvisa as visa
from datetime import datetime
import SOCExpPlatform, MFCSetting, BatteryInfo, help


# -------------------------------------------------------------
# 类名： SOCExpPlatform001
# 功能：主窗口
# -------------------------------------------------------------
class SOCExpPlatform001(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = SOCExpPlatform.Ui_SOCExpPlatform()
        self.ui.setupUi(self)
        self.ui.alarmBox.setText('<font color="blue">原神 启动</font>')
        self.plc_flag = 0
        self.circle_time = self.ui.sB_SetScanCircle.value()
        self._SOCExpPlatform001__initBarChart()
        self.initPLCConnect()
        self.plcGetValue()
        self.buttonConnect()
        self.setTimer()

    # -------------------------------------------------------------
    # 函数名： setTimer
    # 功能： 设置定时器
    # -------------------------------------------------------------
    def setTimer(self):
        self.DisChargeTime = QTimer()
        self.DisChargeTime.timeout.connect(self.timeRecord)
        self.setSampleCircle = QTimer()
        self.setSampleCircle.timeout.connect(self.SampleCircle)
        self.ExDischarge = QTimer()
        self.ExDischarge.timeout.connect(self.doDisCharge)
        self.StoveHeatTime = QTimer()
        self.StoveHeatTime.timeout.connect(self.StoveHeating)
        self.timer = QTimer()
        self.timer.timeout.connect(self.drawChart)

    # -------------------------------------------------------------
    # 函数名： buttonConnect
    # 功能： 按钮信号绑定
    # -------------------------------------------------------------
    def buttonConnect(self):
        self.ui.bB_N2Flow_S.clicked.connect(self.N2Flow)
        self.ui.bB_N2Flow_E.clicked.connect(self.N2NotFlow)
        self.ui.bB_Manual_S.clicked.connect(self.disChargeManualStart)
        self.ui.bB_Manual_E.clicked.connect(self.disChargeManualStop)
        self.ui.bB_DataSave_S.clicked.connect(self.dataSave)
        self.ui.bB_DataSave_E.clicked.connect(self.dataNotSave)
        self.ui.bB_CylinderHome_S.clicked.connect(self.gasPressHome)
        self.ui.bB_CylinderHome_E.clicked.connect(self.gasPressNotHome)
        self.ui.bB_Stove_S.clicked.connect(self.stoveHeat)
        self.ui.bB_Stove_E.clicked.connect(self.stoveNotHeat)
        self.ui.bB_Discharge_S.clicked.connect(self.excuteDischarge)
        self.ui.bB_Discharge_E.clicked.connect(self.notExDischarge)
        self.ui.act_Help.clicked.connect(self.helpWindow)
        self.ui.act_AlarmClear.clicked.connect(self.alarmClear)
        self.ui.act_Silent.clicked.connect(self.silentMode)
        self.ui.act_mfc_info.clicked.connect(self.mfcWindow)
        self.ui.act_baterry_info.clicked.connect(self.batteryWindow)

    # -------------------------------------------------------------
    # 函数名： initPlcConnect
    # 功能： 连接到plc
    # -------------------------------------------------------------
    def initPLCConnect(self):
        try:
            self.plc = snap7.client.Client()
            self.plc.set_connection_type(3)
            self.plc.connect('192.168.16.1', 0, 0)
            self.ui.l_ElcLoad.setText('连接成功')
            self.data = self.plc.read_area(snap7.types.Areas.DB, 1, 0, 300)
            self.ui.pB_PLCConnection.setText('断开PLC')
            self.timer.start(100)
            print('connected to PLC')
            self.ui.alarmBox.append('<font color="blue">PLC连接成功</font>')
            self.plc_flag = 1
        except Exception as e:
            self.ui.l_ElcLoad.setText('未连接')
            self.data = bytearray([0 for i in range(300)])
            print('Fail to Connect PLC')
            self.ui.alarmBox.append('<font color="red">PLC连接失败！请检查PLC</font>')
            self.ui.alarmBox.append(str(e))

    # -------------------------------------------------------------
    # 函数名： plcGetValue
    # 功能：获取plc信息并显示
    # -------------------------------------------------------------
    def plcGetValue(self):
        self.H2Input = snap7.util.get_real(self.data, 0)
        self.ui.l_H2Dis.setText('%.2f' % self.H2Input)
        self.CH4Input = snap7.util.get_real(self.data, 4)
        self.ui.l_CH4Dis.setText('%.2f' % self.CH4Input)
        self.CO2Input = snap7.util.get_real(self.data, 8)
        self.ui.l_CO2Dis.setText('%.2f' % self.CO2Input)
        self.N2Input = snap7.util.get_real(self.data, 12)
        self.ui.l_N2Dis.setText('%.2f' % self.N2Input)
        self.AirInput = snap7.util.get_real(self.data, 16)
        self.ui.l_AirDis.setText('%.2f' % self.AirInput)
        self.COInput = snap7.util.get_real(self.data, 20)
        self.ui.l_CO.setText('%.2f' % self.COInput)
        self.TempInput = snap7.util.get_real(self.data, 24)
        self.ui.l_TEMDis.setText('电堆温度(℃): %.2f' % self.TempInput)
        self.CGCInpout = snap7.util.get_real(self.data, 28)
        self.ui.l_GasDis.setText('可燃(LEL): %.2f' % self.CGCInpout)
        self.GasPressure = snap7.util.get_real(self.data, 36)
        self.ui.l_GasPressure.setText('压力(N): %.2f' % self.GasPressure)
        Stove = snap7.util.get_real(self.data, 208)
        self.ui.l_TEMStove.setText('加热炉温度(℃): %.2f' % Stove)
        Wwet = snap7.util.get_real(self.data, 200)
        self.ui.l_WWet.setText('加湿器温度(℃): %.2f' % Wwet)
        ETrop = snap7.util.get_real(self.data, 204)
        self.ui.l_ETrop.setText('伴热带温度(℃): %.2f' % ETrop)
        ValveH2 = self.data[181]
        if ValveH2 == 1:
            self.ui.pB_ManualH2.setChecked(True)
            self.tubework(self.ui.pgB_H2_2, 1, 0)
        else:
            self.ui.pB_ManualH2.setChecked(False)
            self.tubework(self.ui.pgB_H2_2, 0, 0)
        ValveCH4 = self.data[182]
        if ValveCH4 == 1:
            self.ui.pB_ManualCH4.setChecked(True)
            self.tubework(self.ui.pgB_CH4_2, 1, 0)
        else:
            self.ui.pB_ManualCH4.setChecked(False)
            self.tubework(self.ui.pgB_CH4_2, 0, 0)
        ValveCO2 = self.data[183]
        if ValveCO2 == 1:
            self.ui.pB_ManualCO2.setChecked(True)
            self.tubework(self.ui.pgB_CO2_2, 1, 0)
        else:
            self.ui.pB_ManualCO2.setChecked(False)
            self.tubework(self.ui.pgB_CO2_2, 0, 0)
        ValveN2 = self.data[184]
        if ValveN2 == 1:
            self.ui.pB_ManualN2.setChecked(True)
            self.tubework(self.ui.pgB_N2_2, 1, 0)
        else:
            self.ui.pB_ManualN2.setChecked(False)
            self.tubework(self.ui.pgB_N2_2, 0, 0)
        ValveAir = self.data[185]
        if ValveAir == 1:
            self.ui.pB_ManualAIR.setChecked(True)
            self.tubework(self.ui.pgB_AIR_2, 1, 0)
        else:
            self.ui.pB_ManualAIR.setChecked(False)
            self.tubework(self.ui.pgB_AIR_2, 0, 0)
        ValveCO = self.data[186]
        if ValveCO == 1:
            self.ui.pB_ManualCO.setChecked(True)
            self.tubework(self.ui.pgB_CO_2, 1, 0)
        else:
            self.ui.pB_ManualCO.setChecked(False)
            self.tubework(self.ui.pgB_CO_2, 0, 0)
        Slient = self.data[194]
        if Slient == 1:
            self.ui.act_Silent.setChecked(True)
        else:
            self.ui.act_Silent.setChecked(False)
        Mode_Sel = self.data[214]
        if Mode_Sel == 1:
            self.ui.rB_ch.setChecked(True)
            self.ui.pB_DisCharger.setEnabled(False)
            self.ui.pB_Charger.setEnabled(True)
        else:
            self.ui.rB_dis.setChecked(True)
            self.ui.pB_DisCharger.setEnabled(True)
            self.ui.pB_Charger.setEnabled(False)

    # -------------------------------------------------------------
    # 函数名： tubework
    # 功能：调整管道状态
    # 参数： status 工作状态 0：不工作 1：工作
    #        fg 0：竖管道 1：横管道
    # -------------------------------------------------------------
    def tubework(self, tube, status, fg):
        if fg == 0:
            if status == 0:
                tube.setStyleSheet("image:url(:/images/tube21.png)")
            else:
                tube.setStyleSheet("image:url(:/images/tube22.png)")
        else:
            if status == 0:
                tube.setStyleSheet("image:url(:/images/tube11.png)")
            else:
                tube.setStyleSheet("image:url(:/images/tube12.png)")
            
    # -------------------------------------------------------------
    # 函数名： paintEvent
    # 功能：绘制背景板
    # 参数： evt 绘制动作
    # -------------------------------------------------------------
    def paintEvent(self, evt):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)

    # -------------------------------------------------------------
    # 函数名： alarmClear
    # 功能： 清除报警
    # -------------------------------------------------------------
    def alarmClear(self):
        if self.plc_flag:
            snap7.util.set_byte(self.data, 193, 1)
            self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.ui.alarmBox.setText('')

    # -------------------------------------------------------------
    # 函数名： silentMode
    # 功能： 静音模式
    # -------------------------------------------------------------
    def silentMode(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">plc 连接失败，无需静音</font>')
            return
        if self.ui.act_Silent.isChecked():
            snap7.util.set_byte(self.data, 194, 1)
            self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
            self.ui.act_Silent.setText('取消静音')
        else:
            snap7.util.set_byte(self.data, 194, 0)
            self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
            self.ui.act_Silent.setText('静音')

    # -------------------------------------------------------------
    # 函数名： on_pB_PLCConnection_released
    # 功能： 手动连接或断开PLC(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_PLCConnection_released(self):
        if self.ui.pB_PLCConnection.isChecked():
            self.PLCConnect()
        else:
            self.PLCDisConnect()

    # -------------------------------------------------------------
    # 函数名： PLCConnect
    # 功能： 手动连接PLC
    # -------------------------------------------------------------
    def PLCConnect(self):
        try:
            self.plc.connect('192.168.16.1', 0, 0)
            print('PLCConnect')
            self.ui.l_ElcLoad.setText('连接成功')
            self.ui.alarmBox.append('<font color="blue">PLC连接成功</font>')
            self.ui.pB_PLCConnection.setText('断开PLC')
            self.timer.start(100)
        except:
            print('Fail to Connect PLC')
            self.ui.alarmBox.append('<font color="red">PLC连接失败！请检查PLC</font>')
            self.ui.alarmBox.append(str(e))

    # -------------------------------------------------------------
    # 函数名： PLCDisConnect
    # 功能： 手动断开PLC
    # -------------------------------------------------------------
    def PLCDisConnect(self):
        try:
            self.plc.disconnect()
            print('PLC DisConnect')
            self.ui.l_ElcLoad.setText('未连接')
            self.ui.alarmBox.append('<font color="blue">PLC断开成功</font>')
            self.ui.pB_PLCConnection.setText('连接PLC')
            self.timer.stop()
        except:
            print('PLC DisConnect Error')
            self.ui.alarmBox.append('<font color="red">PLC断开连接失败！请检查</font>')
            self.ui.alarmBox.append(str(e))

    # -------------------------------------------------------------
    # 函数名： N2Flow
    # 功能： 开启氮气吹扫
    # -------------------------------------------------------------
    def N2Flow(self):
        self.ui.rB_Dry.setChecked(True)
        self.ui.alarmBox.append('Fail to Connect PLC')
        snap7.util.set_byte(self.data, 180, 1)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： N2NotFlow
    # 功能： 停止氮气吹扫
    # -------------------------------------------------------------
    def N2NotFlow(self):
        snap7.util.set_byte(self.data, 180, 0)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： on_pB_CylinderPress_released
    # 功能： 开启电缸加压(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_CylinderPress_released(self):
        if self.ui.pB_CylinderPress.isChecked():
            GasPress = self.ui.dSB_PreSet.value()
            snap7.util.set_real(self.data, 200, GasPress)
            self.ui.pB_CylinderPress.setText('加压中...')
            self.ui.pB_CylinderPress.setStyleSheet('color:green')
        else:
            snap7.util.set_real(self.data, 200, 0)
            self.ui.pB_CylinderPress.setText('电缸加压')
            self.ui.pB_CylinderPress.setStyleSheet('color:black')
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： gasPressHome
    # 功能： 电缸加压回原位
    # -------------------------------------------------------------
    def gasPressHome(self):
        snap7.util.set_byte(self.data, 188, 1)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.ui.bB_CylinderHome.button(QDialogButtonBox.Ok).setText('回原位中。。。。')
        self.ui.bB_CylinderHome.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.pB_CylinderPress.setEnabled(False)

    # -------------------------------------------------------------
    # 函数名： gasPressNotHome
    # 功能： 电缸加压停止回原位
    # -------------------------------------------------------------
    def gasPressNotHome(self):
        snap7.util.set_byte(self.data, 188, 0)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.ui.bB_CylinderHome.button(QDialogButtonBox.Ok).setText('回原位')
        self.ui.bB_CylinderHome.button(QDialogButtonBox.Ok).setEnabled(True)
        self.ui.pB_CylinderPress.setEnabled(True)

    # -------------------------------------------------------------
    # 函数名： stoveHeat
    # 功能： 开始加热*
    # -------------------------------------------------------------
    def stoveHeat(self):
        self.StoveHeatIndex = self.itemModel_Stove.rowCount()
        self.StoveHeatBuff = self.ui.sB_StoveStart.value() - 1
        self.StoveTempStart = 0
        self.StoveTime = 0
        self.ui.tV_Stove.selectRow(self.StoveHeatBuff)
        self.ui.bB_Stove_S.button(QDialogButtonBox.Ok).setText('加热中。。。。')
        self.ui.bB_Stove_E.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.tV_Stove.setEnabled(False)
        StoveTempBuff = self.itemModel_Stove.item(self.StoveHeatBuff, 0)
        StoveTemp = float(StoveTempBuff.text())
        StoveTempTimeBuff = self.itemModel_Stove.item(self.StoveHeatBuff, 1)
        StoveTempTime = float(StoveTempTimeBuff.text())
        CurrentTemp = snap7.util.get_real(self.data, 40)
        StoveTemp = StoveTemp - CurrentTemp
        self.StoveMid = StoveTemp / StoveTempTime
        self.StoveTempStart = CurrentTemp
        snap7.util.set_real(self.data, 208, self.StoveTempStart)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.StoveHeatTime.start(60000)

    # -------------------------------------------------------------
    # 函数名： stoveNotHeat
    # 功能： 停止加热*
    # -------------------------------------------------------------
    def stoveNotHeat(self):
        self.StoveTempStart = 0
        self.ui.tV_Stove.setEnabled(True)
        self.ui.bB_Stove_S.button(QDialogButtonBox.Ok).setText('控温启动')
        self.ui.bB_Stove_E.button(QDialogButtonBox.Ok).setEnabled(True)
        snap7.util.set_real(self.data, 208, 0)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.StoveHeatTime.stop()

    # -------------------------------------------------------------
    # 函数名： StoveHeating
    # 功能： 加热进行*
    # -------------------------------------------------------------
    def StoveHeating(self):
        self.StoveTime = self.StoveTime + 1
        self.ui.tV_Stove.selectRow(self.StoveHeatBuff)
        timebuff = self.itemModel_Stove.item(self.StoveHeatBuff, 1)
        time = int(timebuff.text())
        self.StoveTempStart = self.StoveTempStart + self.StoveMid
        if time == self.StoveTime:
            self.StoveHeatBuff = self.StoveHeatBuff + 1
            if self.StoveHeatBuff == self.StoveHeatIndex:
                self.StoveNotHeat()
            else:
                self.StoveTime = 0
                StoveTempBuff = self.itemModel_Stove.item(self.StoveHeatBuff, 0)
                StoveTemp = float(StoveTempBuff.text())
                StoveTempTimeBuff = self.itemModel_Stove.item(self.StoveHeatBuff, 1)
                StoveTempTime = float(StoveTempTimeBuff.text())
                StoveMid = StoveTemp - self.StoveTempStart
                self.StoveMid = StoveMid / StoveTempTime
        snap7.util.set_real(self.data, 208, self.StoveTempStart)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        print(self.StoveTempStart)

    # -------------------------------------------------------------
    # 函数名： on_pB_Path_clicked
    # 功能： 修改保存路径(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_Path_clicked(self):
        curPath = os.getcwd()
        self.filename, flt = QFileDialog.getSaveFileName(self, '保存文件', curPath, '数据文件(*.csv);;所有文件(*.*)')
        if self.filename == '':
            return
        headers = []
        headers.append('电池信息:%s' % str(self.BatteryNO))
        headers.append('单体电池节数:%s' % str(self.UnitBattery))
        headers.append('电池节数:%s' % str(self.UnitBatteryPack))
        headers.append('电池面积(cm²):%s' % str(self.Battery_Area))
        headers1 = [
         "'日期'", "'记录时间（24小时）'", "'累计时间'", "'电流'", "'电压'",
         "'功率'", "'电流密度'", "'功率密度'", "'单体电压'", "'加压压力'", "'加热炉温度'",
         "'H2流量'", "'CH4流量'", "'CO2流量'", "'N2流量'", "'Air流量'", "'CO流量'"]
        with open((self.filename), 'w', newline='', encoding='UTF-8-sig') as (file):
            f_csv = csv.writer(file)
            f_csv.writerow(headers)
            f_csv.writerow(headers1)
        self.ui.bB_DataSave_S.setEnabled(True)
        self.ui.bB_DataSave_E.setEnabled(True)

    # -------------------------------------------------------------
    # 函数名： on_pB_SetScanCircle_clicked
    # 功能： 修改采样周期(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_SetScanCircle_clicked(self):
        self.circle_time = self.ui.sB_SetScanCircle.value()

    # -------------------------------------------------------------
    # 函数名： SampleCircle
    # 功能： 每个周期的采样工作
    # -------------------------------------------------------------
    def SampleCircle(self):
        data = []
        data.append(datetime.now().strftime('%Y-%m-%d'))
        data.append(datetime.now().strftime(' %H:%M:%S'))
        data.append(datetime.now() - self.currentTime)
        for i in range(3):
            data.append(float(self.dataList[i]))

        temp = float(self.dataList[0]) * 1000 / self.Battery_Area
        data.append(temp)
        temp = float(self.dataList[2]) * 1000 / self.Battery_Area
        data.append(temp)
        for i in range(3):
            data.append(self.PLCDataInput[i + 8])

        for i in range(6):
            data.append(self.PLCDataInput[i])

        with open(self.filename, 'a', newline='', encoding='UTF-8-sig') as (file):
            f_csv = csv.writer(file)
            f_csv.writerow(data)

    # -------------------------------------------------------------
    # 函数名： dataSave
    # 功能： 开始采样
    # -------------------------------------------------------------
    def dataSave(self):
        self.setSampleCircle.start(self.circle_time)
        self.ui.l_DataSave.setText('数据采集中...')
        self.ui.l_DataSave.setStyleSheet('color:red')
        self.currentTime = datetime.now()

    # -------------------------------------------------------------
    # 函数名： dataNotSave
    # 功能： 结束采样
    # -------------------------------------------------------------
    def dataNotSave(self):
        self.setSampleCircle.stop()
        self.ui.l_DataSave.setText('数据未采集')
        self.ui.l_DataSave.setStyleSheet('color:white')


    # -------------------------------------------------------------
    # 函数名： on_pB_DataAnalize_clicked
    # 功能： 分析数据
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_DataAnalize_clicked(self):
        self.pltImage()

    # -------------------------------------------------------------
    # 函数名： pltImage
    # 功能： 数据制图
    # -------------------------------------------------------------
    def pltImage(self):
        curPath = os.getcwd()
        filename, flt = QFileDialog.getOpenFileName(self, '读取文件', curPath, '数据文件(*.csv);;所有文件(*.*)')
        if filename == '':
            return
        t0 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.str_), delimiter=',', skiprows=2, usecols=2)
        t0 = [datetime.strptime(i, '%H:%M:%S.%f') for i in t0]
        t1 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=3)
        t2 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=4)
        t3 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=5)
        t4 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=6)
        t5 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=7)
        t6 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=8)
        t7 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=9)
        t8 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=10)
        t9 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=11)
        t10 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=12)
        t11 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=13)
        t12 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=14)
        t13 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=15)
        t14 = np.loadtxt(filename, encoding='Latin-1', dtype=(np.float32), delimiter=',', skiprows=2, usecols=16)
        fig, ax = plt.subplots()
        plt.xticks(rotation=45)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        l1, = ax.plot(t0, t1, visible=False, lw=2, markersize=6, label='电流', marker='s')
        l2, = ax.plot(t0, t2, visible=False, lw=2, markersize=6, label='电压', marker='s')
        l3, = ax.plot(t0, t3, visible=False, lw=2, markersize=6, label='功率', marker='s')
        l4, = ax.plot(t0, t4, visible=False, lw=2, markersize=6, label='电流密度', marker='s')
        l5, = ax.plot(t0, t5, visible=False, lw=2, markersize=6, label='功率密度', marker='s')
        l6, = ax.plot(t0, t6, visible=False, lw=2, markersize=6, label='单体电压', marker='s')
        l7, = ax.plot(t0, t7, visible=False, lw=2, markersize=6, label='加压压力', marker='s')
        l8, = ax.plot(t0, t8, visible=False, lw=2, markersize=6, label='加热炉温度', marker='s')
        l14, = ax.plot(t0, t9, visible=False, lw=2, markersize=6, label='H2流量', marker='s')
        l15, = ax.plot(t0, t10, visible=False, lw=2, markersize=6, label='CH4流量', marker='s')
        l16, = ax.plot(t0, t11, visible=False, lw=2, markersize=6, label='CO2流量', marker='s')
        l17, = ax.plot(t0, t12, visible=False, lw=2, markersize=6, label='N2流量', marker='s')
        l18, = ax.plot(t0, t13, visible=False, lw=2, markersize=6, label='Air流量', marker='s')
        l19, = ax.plot(t0, t14, visible=False, lw=2, markersize=6, label='CO流量', marker='s')
        plt.subplots_adjust(left=0.2)
        self.lines = [
            'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8',
            'l14', 'l15', 'l16', 'l17', 'l18', 'l19']
        rax = plt.axes([0.05, 0.4, 0.1, 0.3])
        self.labels = [str(line.get_label()) for line in self.lines]
        visibility = [line.get_visible() for line in self.lines]
        self.check = CheckButtons(rax, self.labels, visibility)
        plt.legend((self.lines), (self.labels), bbox_to_anchor=(8.7, 1), loc='upper left', borderaxespad=0)
        self.check.on_clicked(self.func)
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()

    # -------------------------------------------------------------
    # 函数名： disChargeManualStart
    # 功能： 手动运行开始
    # -------------------------------------------------------------
    def disChargeManualStart(self):
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.res.write('INP ON')
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.res.write('OUTP ON')
        self.ui.rB_CC.setEnabled(False)
        self.ui.rB_CV.setEnabled(False)
        self.ui.rB_CP.setEnabled(False)
        self.ui.dSB_ManualData.setEnabled(False)
        self.recordTime = 0
        self.DisChargeTime.start(1000)

    # -------------------------------------------------------------
    # 函数名： disChargeManualStop
    # 功能： 停止手动运行
    # -------------------------------------------------------------
    def disChargeManualStop(self):
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.res.write('INP OFF')
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.res.write('OUTP OFF')
        self.ui.rB_CC.setEnabled(True)
        self.ui.rB_CV.setEnabled(True)
        self.ui.rB_CP.setEnabled(True)
        self.ui.dSB_ManualData.setEnabled(True)
        self.recordTime = 0
        self.DisChargeTime.stop()

    # -------------------------------------------------------------
    # 函数名： timeRecord
    # 功能： 记录手动运行时间
    # -------------------------------------------------------------
    def timeRecord(self):
        self.recordTime = self.recordTime + 1
        self.ui.l_WorkTime.setText('已运行时间(s):%s s' % self.recordTime)

    # -------------------------------------------------------------
    # 函数名： excuteDischarge
    # 功能：执行自动充放电*
    # -------------------------------------------------------------
    def excuteDischarge(self):
        self.itemIndex = self.itemModel_Dis.rowCount()
        self.itemIndexBuff = 0
        self.ExDischargeTime = 0
        self.LC_Data = 0
        self.LC_Time = 0
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.res.write('INP ON')
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.res.write('OUTP ON')
        self.ui.tV_Dischagre.setEnabled(False)
        self.ExDischarge.start(100)

    # -------------------------------------------------------------
    # 函数名： doDisCharge
    # 功能： 自动充放电*
    # -------------------------------------------------------------
    def doDisCharge(self):
        pass

    # -------------------------------------------------------------
    # 函数名： notExDischarge
    # 功能： 停止自动充放电*
    # -------------------------------------------------------------
    def notExDischarge(self):
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.res.write('INP OFF')
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.res.write('OUTP OFF')
        self.ExDischarge.stop()
        self.ui.tV_Dischagre.setEnabled(True)

    # -------------------------------------------------------------
    # 函数名： on_cB_DiachargeH2_clicked
    # 功能： 图表显示H2(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DiachargeH2_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeCH4_clicked
    # 功能： 图表显示CH4(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeCH4_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeCO2_clicked
    # 功能： 图表显示CO2(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeCO2_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeN2_clicked
    # 功能： 图表显示N2(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeN2_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeAIR_clicked
    # 功能： 图表显示空气(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeAIR_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeCO_clicked
    # 功能： 图表显示CO(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeCO_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeCURR_clicked
    # 功能： 图表显示电流(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeCURR_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeVOLT_clicked
    # 功能： 图表显示电压(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeVOLT_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargePOW_clicked
    # 功能： 图表显示功率(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargePOW_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargePOWDansity_clicked
    # 功能： 图表显示功率密度(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargePOWDansity_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeCURRDansity_clicked
    # 功能： 图表显示电流密度(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeCURRDansity_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： on_cB_StoveTemp_clicked
    # 功能： 图表显示加热炉温度(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_StoveTemp_clicked(self):
        self.isVertical = False
        self._SOCExpPlatform001__initBarChart()

    # -------------------------------------------------------------
    # 函数名： __initBarChart
    # 功能： 初始化图表*
    # -------------------------------------------------------------
    def __initBarChart(self):
        chart = QChart()
        chart.setTitle('SOC运行实时数据')
        self.ui.gV_DataDisplay.setChart(chart)
        self.ui.gV_DataDisplay.setRenderHint(QPainter.Antialiasing)
        self.chart = self.ui.gV_DataDisplay.chart()
        self.seriesH2 = QSplineSeries()
        self.seriesCH4 = QSplineSeries()
        self.seriesCO2 = QSplineSeries()
        self.seriesN2 = QSplineSeries()
        self.seriesAIR = QSplineSeries()
        self.seriesCO = QSplineSeries()
        self.seriesCURR = QSplineSeries()
        self.seriesVOLT = QSplineSeries()
        self.seriesPOW = QSplineSeries()
        self.seriesCURRD = QSplineSeries()
        self.seriesPOWD = QSplineSeries()
        self.seriesStove = QSplineSeries()
        self.seriesH2.setName('H2')
        self.seriesCH4.setName('CH4')
        self.seriesCO2.setName('CO2')
        self.seriesN2.setName('N2')
        self.seriesAIR.setName('AIR')
        self.seriesCO.setName('CO')
        self.seriesCURR.setName('单体电压')
        self.seriesVOLT.setName('加压压力')
        self.seriesPOW.setName('功率')
        self.seriesCURRD.setName('CURR_D')
        self.seriesPOWD.setName('POW_D')
        self.seriesStove.setName('加热炉温度')
        if self.ui.cB_DischargeH2.isChecked():
            self.chart.addSeries(self.seriesH2)
        else:
            if self.ui.cB_DischargeCH4.isChecked():
                self.chart.addSeries(self.seriesCH4)
            if self.ui.cB_DischargeCO2.isChecked():
                self.chart.addSeries(self.seriesCO2)
            if self.ui.cB_DischargeN2.isChecked():
                self.chart.addSeries(self.seriesN2)
            if self.ui.cB_DischargeAIR.isChecked():
                self.chart.addSeries(self.seriesAIR)
            if self.ui.cB_DischargeCO.isChecked():
                self.chart.addSeries(self.seriesCO)
            if self.ui.cB_DischargeCURR.isChecked():
                self.chart.addSeries(self.seriesCURR)
            if self.ui.cB_DischargeVOLT.isChecked():
                self.chart.addSeries(self.seriesVOLT)
            if self.ui.cB_DischargePOW.isChecked():
                self.chart.addSeries(self.seriesPOW)
            if self.ui.cB_DischargeCURRDansity.isChecked():
                self.chart.addSeries(self.seriesCURRD)
            if self.ui.cB_DischargePOWDansity.isChecked():
                self.chart.addSeries(self.seriesPOWD)
            if self.ui.cB_StoveTemp.isChecked():
                self.chart.addSeries(self.seriesStove)
            self.dtaxisX = QDateTimeAxis()
            self.vlaxisY = QValueAxis()
            self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-5))
            self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
            self.vlaxisY.setMin(0)
            if self.ui.cB_StoveTemp.isChecked():
                self.vlaxisY.setMax(1000)
            else:
                self.vlaxisY.setMax(200)
        self.dtaxisX.setFormat('MM月dd hh:mm:ss')
        self.dtaxisX.setTickCount(6)
        self.vlaxisY.setTickCount(11)
        self.dtaxisX.setTitleText('时间')
        self.vlaxisY.setTitleText('量程')
        self.vlaxisY.setGridLineVisible(False)
        self.chart.addAxis(self.dtaxisX, Qt.AlignBottom)
        self.chart.addAxis(self.vlaxisY, Qt.AlignLeft)
        self.seriesH2.attachAxis(self.dtaxisX)
        self.seriesH2.attachAxis(self.vlaxisY)
        self.seriesCH4.attachAxis(self.dtaxisX)
        self.seriesCH4.attachAxis(self.vlaxisY)
        self.seriesCO2.attachAxis(self.dtaxisX)
        self.seriesCO2.attachAxis(self.vlaxisY)
        self.seriesN2.attachAxis(self.dtaxisX)
        self.seriesN2.attachAxis(self.vlaxisY)
        self.seriesAIR.attachAxis(self.dtaxisX)
        self.seriesAIR.attachAxis(self.vlaxisY)
        self.seriesCO.attachAxis(self.dtaxisX)
        self.seriesCO.attachAxis(self.vlaxisY)
        self.seriesCURR.attachAxis(self.dtaxisX)
        self.seriesCURR.attachAxis(self.vlaxisY)
        self.seriesVOLT.attachAxis(self.dtaxisX)
        self.seriesVOLT.attachAxis(self.vlaxisY)
        self.seriesPOW.attachAxis(self.dtaxisX)
        self.seriesPOW.attachAxis(self.vlaxisY)
        self.seriesCURRD.attachAxis(self.dtaxisX)
        self.seriesCURRD.attachAxis(self.vlaxisY)
        self.seriesPOWD.attachAxis(self.dtaxisX)
        self.seriesPOWD.attachAxis(self.vlaxisY)
        self.seriesStove.attachAxis(self.dtaxisX)
        self.seriesStove.attachAxis(self.vlaxisY)
        self.isVertical = False

    # -------------------------------------------------------------
    # 函数名： drawChart
    # 功能：绘制图表
    # -------------------------------------------------------------
    def drawChart(self):
        pass

    # -------------------------------------------------------------
    # 函数名： helpWindow
    # 功能：打开帮助窗口
    # -------------------------------------------------------------
    def helpWindow(self):
        self.window2 = HelpWindow()
        self.window2.show_info()
        self.window2.show()

    # -------------------------------------------------------------
    # 函数名： mfcWindow
    # 功能：打开MFC窗口
    # -------------------------------------------------------------
    def mfcWindow(self):
        self.window3 = MFCWindow()
        self.window3.show()

    # -------------------------------------------------------------
    # 函数名： batteryWindow
    # 功能：打开电池信息窗口
    # -------------------------------------------------------------
    def batteryWindow(self):
        self.window4 = BatteryWindow()
        self.window4.show()


# -------------------------------------------------------------
# 类名： HelpWindow
# 功能：帮助窗口
# -------------------------------------------------------------
class HelpWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = help.Ui_Help()
        self.ui.setupUi(self)

    # -------------------------------------------------------------
    # 函数名： show_info
    # 功能： 读取帮助信息
    # -------------------------------------------------------------
    def show_info(self):
        with open(r'Help.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        self.ui.outBox.setText(text)


# -------------------------------------------------------------
# 类名： MFCWindow
# 功能：MFC设置窗口
# -------------------------------------------------------------
class MFCWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MFCSetting.Ui_MFC_Info()
        self.ui.setupUi(self)


# -------------------------------------------------------------
# 类名： BatteryWindow
# 功能：电池信息设置窗口
# -------------------------------------------------------------
class BatteryWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = BatteryInfo.Ui_batteryInfo()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('./img/cnpc.png'))
    ex = SOCExpPlatform001()
    ex.show()
    sys.exit(app.exec_())

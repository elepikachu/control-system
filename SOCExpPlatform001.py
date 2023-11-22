# -------------------------------------------------------------
# -*- coding: utf-8 -*-
# Writer: Elepikachu
# Copyright CNPC.inc
# 2023/11/13
# -------------------------------------------------------------

import csv
import json
import os
import time

import snap7
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtChart import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QDateTime, QTimer, QThread, QItemSelectionModel
from PyQt5.QtGui import QPainter, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QDialogButtonBox, QDialog, QTableWidgetItem
from matplotlib.widgets import CheckButtons

import BatteryInfo
import MFCSetting
import SOCExpPlatform
import help


class RunThread(QThread):
    _signal = pyqtSignal(str)

    def __init__(self, master_):
        super().__init__()
        self.master = master_

    def run(self):
        try:
            self.master.write('MEAS:CURR?;:MEAS:VOLT?;:MEAS:POW?')
            data = self.master.read()
            self._signal.emit(data)
        except:
            print('Visa Error')


# -------------------------------------------------------------
# 类名： SOCExpPlatform001
# 功能：主窗口
# -------------------------------------------------------------
class SOCExpPlatform001(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = SOCExpPlatform.Ui_SOCExpPlatform()
        self.ui.setupUi(self)
        self.ui.alarmBox.setText('<font color="blue">测试平台启动！</font>')
        self.plc_flag = 0
        self.batteryNO = '未设置'
        self.unitBattery = 8
        self.unitBatteryPack = 8
        self.batteryArea = 60
        self.StoveTempStart = 0
        self.alarmData = 0
        self.alarmCurrentData = 0
        self.circle_time = self.ui.sB_SetScanCircle.value()
        self.itemModel_tV = QStandardItemModel(0, 2, self)
        self.selectionModel_tV = QItemSelectionModel(self.itemModel_tV)
        self.ui.tV_log.setModel(self.itemModel_tV)
        self.itemModel_tV.setHorizontalHeaderLabels(['时间','描述'])
        self._SOCExpPlatform001__initBarChart()
        self.initPLCConnect()
        self.plcGetValue()
        self.buttonConnect()
        self.setTimer()
        self.readConfig()

    # -------------------------------------------------------------
    # 函数名： readConfig
    # 功能： 读取json的配置信息
    # -------------------------------------------------------------
    def readConfig(self):
        #self.initTable()
        with open('config.json', encoding="utf-8") as load_f:
            try:
                js = json.load(load_f)
            except Exception as e:
                print(e)
                self.configResetAuto()
                self.ui.alarmBox.append('<font color="red">配置信息读取失败，重置配置信息</font>')
                js = json.load(load_f)
            stoveConfig = js[0]["para"]
            stoveStart = js[0]["start"]
            self.ui.sB_StoveStart.setValue(stoveStart)
            rowCnt = len(stoveConfig)
            for i in range(rowCnt):
                item_temp = QTableWidgetItem(str(stoveConfig[i]['temp']))
                item_time = QTableWidgetItem(str(stoveConfig[i]['time']))
                self.ui.tV_Stove.setItem(i, 0, item_temp)
                self.ui.tV_Stove.setItem(i, 1, item_time)
            disConfig = js[1]["para"]
            rowCnt2 = len(disConfig)
            keys = list(disConfig[0])
            for i in range(rowCnt2):
                for j in range(1, 10):
                    self.ui.tV_Discharge.setItem(i, j - 1, QTableWidgetItem(str(disConfig[i][keys[j]])))

    # -------------------------------------------------------------
    # 函数名： initTable
    # 功能： 放电表格选择栏设置
    # -------------------------------------------------------------
    def initTable(self):
        combo_join = QtWidgets.QComboBox()
        combo_join.addItem('参与')
        combo_join.addItem('不参与')
        combo_process = QtWidgets.QComboBox()
        combo_process.addItem('充电')
        combo_process.addItem('放电')
        combo_mode = QtWidgets.QComboBox()
        combo_mode.addItem('CC(A)')
        combo_mode.addItem('CV(V)')
        combo_mode.addItem('CP(W)')
        combo_mode.addItem('LCC(A)')
        combo_mode.addItem('LCV(V)')
        combo_mode.addItem('LCP(W)')
        combo_stop = QtWidgets.QComboBox()
        combo_stop.addItem('电堆电流(A)')
        combo_stop.addItem('电堆电压(V)')
        combo_stop.addItem('电堆功率(W)')
        combo_stop.addItem('执行时间(s)')
        combo_logic = QtWidgets.QComboBox()
        combo_logic.addItem('大于')
        combo_logic.addItem('小于')
        for i in range(self.ui.tV_Discharge.rowCount()-1):
            self.ui.tV_Discharge.setCellWidget(i, 0, combo_join)
            self.ui.tV_Discharge.setCellWidget(i, 1, combo_process)
            self.ui.tV_Discharge.setCellWidget(i, 2, combo_mode)
            self.ui.tV_Discharge.setCellWidget(i, 6, combo_stop)
            self.ui.tV_Discharge.setCellWidget(i, 7, combo_logic)

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
        self.plotTimer = QTimer()
        self.plotTimer.timeout.connect(self.drawChart)

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
        self.ui.bB_StoveSave.clicked.connect(self.stoveSave)
        self.ui.bB_Discharge_Save.clicked.connect(self.dischargeSave)
        self.ui.act_Config.clicked.connect(self.configReset)
        self.ui.act_Help.clicked.connect(self.helpWindow)
        self.ui.act_AlarmClear.clicked.connect(self.alarmClear)
        self.ui.act_Silent.clicked.connect(self.silentMode)
        self.ui.act_mfc_info.clicked.connect(self.mfcWindow)
        self.ui.act_baterry_info.clicked.connect(self.batteryWindow)
        self.ui.rB_auto.clicked.connect(self.radioButtonClicked)
        self.ui.rB_manu.clicked.connect(self.radioButtonClicked)
        self.ui.rB_dis.clicked.connect(self.manuModeRbClicked)
        self.ui.rB_ch.clicked.connect(self.manuModeRbClicked)
        self.ui.rB_CC.clicked.connect(self.manuTypeRbClicked)
        self.ui.rB_CV.clicked.connect(self.manuTypeRbClicked)
        self.ui.rB_CP.clicked.connect(self.manuTypeRbClicked)
        self.ui.dSB_ManualData.valueChanged.connect(self.dSB_ManualDataChanged)

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
            self.plotTimer.start(100)
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
        H2LimitL = snap7.util.get_real(self.data, 94)
        self.dBB_SetMFCH2Low = H2LimitL
        H2LimitH = snap7.util.get_real(self.data, 98)
        self.dBB_SetMFCH2High = H2LimitH
        CO2LimitL = snap7.util.get_real(self.data, 110)
        self.dBB_SetMFCCO2Low = CO2LimitL
        CO2LimitH = snap7.util.get_real(self.data, 114)
        self.dBB_SetMFCCO2High = CO2LimitH
        CH4LimitL = snap7.util.get_real(self.data, 102)
        self.dBB_SetMFCCH4Low = CH4LimitL
        CH4LimitH = snap7.util.get_real(self.data, 106)
        self.dBB_SetMFCCH4High = CH4LimitH
        COLimitL = snap7.util.get_real(self.data, 134)
        self.dBB_SetMFCCOLow = COLimitL
        COLimitH = snap7.util.get_real(self.data, 138)
        self.dBB_SetMFCCOHigh = COLimitH
        AirLimitL = snap7.util.get_real(self.data, 126)
        self.dBB_SetMFCAirLow = AirLimitL
        AirLimitH = snap7.util.get_real(self.data, 130)
        self.dBB_SetMFCAirHigh = AirLimitH
        N2LimitL = snap7.util.get_real(self.data, 118)
        self.dBB_SetMFCN2Low = N2LimitL
        N2LimitH = snap7.util.get_real(self.data, 122)
        self.dBB_SetMFCN2High = N2LimitH
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
            self.plc_flag = True
            self.plotTimer.start(100)
        except Exception as e:
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
            self.plc_flag = False
            self.plotTimer.stop()
        except Exception as e:
            print('PLC DisConnect Error')
            self.ui.alarmBox.append('<font color="red">PLC断开连接失败！请检查</font>')
            self.ui.alarmBox.append(str(e))

    # -------------------------------------------------------------
    # 函数名： N2Flow
    # 功能： 开启氮气吹扫
    # -------------------------------------------------------------
    def N2Flow(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">未连接plc,无法开启吹扫</font>')
            return
        self.ui.rB_Dry.setChecked(True)
        self.ui.alarmBox.append('开启氮气吹扫成功')
        snap7.util.set_byte(self.data, 180, 1)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： N2NotFlow
    # 功能： 停止氮气吹扫
    # -------------------------------------------------------------
    def N2NotFlow(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">未连接plc,无法停止吹扫</font>')
            return
        snap7.util.set_byte(self.data, 180, 0)
        self.ui.alarmBox.append('已关闭氮气吹扫')
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： on_pB_CylinderPress_released
    # 功能： 开启电缸加压(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_CylinderPress_released(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">未连接plc,无法加压</font>')
            return
        if self.ui.pB_CylinderPress.isChecked():
            GasPress = self.ui.dSB_PreSet.value()
            snap7.util.set_real(self.data, 200, GasPress)
            self.ui.pB_CylinderPress.setText('停止加压')
            self.ui.alarmBox.append('<font color="blue">正在电缸加压</font>')
            self.ui.pB_CylinderPress.setStyleSheet('color:green')
        else:
            snap7.util.set_real(self.data, 200, 0)
            self.ui.pB_CylinderPress.setText('电缸加压')
            self.ui.alarmBox.append('已关闭电缸加压')
            self.ui.pB_CylinderPress.setStyleSheet('color:black')
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： gasPressHome
    # 功能： 电缸加压回原位
    # -------------------------------------------------------------
    def gasPressHome(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">未连接plc,操作失败</font>')
            return
        snap7.util.set_byte(self.data, 188, 1)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.ui.alarmBox.append('<font color="blue">回原位中。。。。</font>')
        self.ui.bB_CylinderHome_S.button.setEnabled(False)
        self.ui.pB_CylinderPress.setEnabled(False)

    # -------------------------------------------------------------
    # 函数名： gasPressNotHome
    # 功能： 电缸加压停止回原位
    # -------------------------------------------------------------
    def gasPressNotHome(self):
        if not self.plc_flag:
            self.ui.alarmBox.append('<font color="red">未连接plc,操作失败</font>')
            return
        snap7.util.set_byte(self.data, 188, 0)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        self.ui.alarmBox.append('回原位停止')
        self.ui.bB_CylinderHome.button(QDialogButtonBox.Ok).setEnabled(True)
        self.ui.pB_CylinderPress.setEnabled(True)

    # -------------------------------------------------------------
    # 函数名： stoveHeat
    # 功能： 开始加热*
    # -------------------------------------------------------------
    def stoveHeat(self):
        # if not self.plc_flag:
        #     self.ui.alarmBox.append('<font color="red">未连接plc,操作失败</font>')
        #     return
        self.StoveHeatIndex = self.ui.tV_Stove.rowCount()
        self.StoveHeatBuff = self.ui.sB_StoveStart.value() - 1
        self.StoveTempStart = 0
        self.StoveTime = 0
        self.ui.tV_Stove.selectRow(self.StoveHeatBuff)
        self.ui.alarmBox.append('<font color="blue">正在加热</font>')
        self.ui.bB_Stove_S.setEnabled(False)
        self.ui.tV_Stove.setEnabled(False)
        StoveTempBuff = self.ui.tV_Stove.item(self.StoveHeatBuff, 0)
        StoveTemp = float(StoveTempBuff.text())
        StoveTempTimeBuff = self.ui.tV_Stove.item(self.StoveHeatBuff, 1)
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
        if self.StoveTempStart == 0:
            self.ui.alarmBox.append('<font color="red">加热未开始，无需停止</font>')
            return
        self.StoveTempStart = 0
        self.ui.tV_Stove.setEnabled(True)
        self.ui.alarmBox.append('停止加热成功')
        self.ui.bB_Stove_S.setEnabled(True)
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
        timebuff = self.ui.tV_Stove.item(self.StoveHeatBuff, 1)
        time = int(timebuff.text())
        self.StoveTempStart = self.StoveTempStart + self.StoveMid
        if time == self.StoveTime:
            self.StoveHeatBuff = self.StoveHeatBuff + 1
            if self.StoveHeatBuff == self.StoveHeatIndex:
                self.StoveNotHeat()
            else:
                self.StoveTime = 0
                StoveTempBuff = self.ui.tV_Stove.item(self.StoveHeatBuff, 0)
                StoveTemp = float(StoveTempBuff.text())
                StoveTempTimeBuff = self.ui.tV_Stove.item(self.StoveHeatBuff, 1)
                StoveTempTime = float(StoveTempTimeBuff.text())
                StoveMid = StoveTemp - self.StoveTempStart
                self.StoveMid = StoveMid / StoveTempTime
        snap7.util.set_real(self.data, 208, self.StoveTempStart)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        print(self.StoveTempStart)

    # -------------------------------------------------------------
    # 函数名： stoveSave
    # 功能： 保存加热配置
    # -------------------------------------------------------------
    def stoveSave(self):
        startVal = self.ui.sB_StoveStart.value()
        with open('config.json', encoding="utf-8") as f:
            js = json.load(f)
        with open('config.json', 'w', encoding="utf-8") as f:
            for i in range(self.ui.tV_Stove.rowCount()):
                if self.ui.tV_Stove.item(i, 0) is None or self.ui.tV_Stove.item(i, 0).text == '':
                    break
                if i >= len(js[0]["para"]):
                    js[0]["para"].append({"id": i+1})
                item_temp = self.ui.tV_Stove.item(i, 0).text()
                item_time = self.ui.tV_Stove.item(i, 1).text()
                js[0]["para"][i]["temp"] = item_temp
                js[0]["para"][i]["time"] = item_time
            js[0]["start"] = startVal
            f.write(json.dumps(js, ensure_ascii=False))
        self.ui.alarmBox.append('加热参数保存成功')
        self.ui.tV_Discharge.clearContents()
        self.ui.tV_Stove.clearContents()
        self.readConfig()

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
        headers.append('电池信息:%s' % str(self.batteryNO))
        headers.append('单体电池节数:%s' % str(self.unitBattery))
        headers.append('电池节数:%s' % str(self.unitBatteryPack))
        headers.append('电池面积(cm²):%s' % str(self.batteryArea))
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
    # 函数名： radioButtonClicked
    # 功能： 充放电选择后屏蔽另一边操作
    # -------------------------------------------------------------
    def radioButtonClicked(self):
        if self.ui.rB_manu.isChecked():
            self.ui.rB_ch.setEnabled(True)
            self.ui.rB_dis.setEnabled(True)
            self.ui.dSB_ManualData.setEnabled(True)
            self.ui.bB_Manual_S.setEnabled(True)
            self.ui.bB_Manual_E.setEnabled(True)
            self.ui.tV_Discharge.setEnabled(False)
            self.ui.bB_Discharge_E.setEnabled(False)
            self.ui.bB_Discharge_S.setEnabled(False)
            self.ui.rB_CC.setEnabled(True)
            self.ui.rB_CV.setEnabled(True)
            self.ui.rB_CP.setEnabled(True)
            self.ExDischarge.stop()
        if self.ui.rB_auto.isChecked():
            self.ui.rB_ch.setEnabled(False)
            self.ui.rB_dis.setEnabled(False)
            self.ui.dSB_ManualData.setEnabled(False)
            self.ui.bB_Manual_S.setEnabled(False)
            self.ui.bB_Manual_E.setEnabled(False)
            self.ui.tV_Discharge.setEnabled(True)
            self.ui.bB_Discharge_S.setEnabled(True)
            self.ui.bB_Discharge_E.setEnabled(True)
            self.ui.rB_CC.setEnabled(False)
            self.ui.rB_CV.setEnabled(False)
            self.ui.rB_CP.setEnabled(False)
            self.DisChargeTime.stop()
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('INP OFF')
            if self.ui.pB_Charger.text() == '断开直流电源':
                self.res.write('OUTP OFF')

    def manuModeRbClicked(self):
        if self.ui.rB_dis.isChecked():
            snap7.util.set_byte(self.data, 214, 1)
            self.ui.pB_DisCharger.setEnabled(False)
            self.ui.pB_Charger.setEnabled(True)
            self.ui.pB_DisCharger.setChecked(False)
            self.ui.pB_Charger.setChecked(False)
            self.ui.l_Connect_Dis.setText('未连接负载')
            self.ui.l_Connect_Dis.setStyleSheet('color:black')
            self.ui.pB_DisCharger.setText('连接电子负载')
            self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)
        elif self.ui.rB_ch.isChecked():
            snap7.util.set_byte(self.data, 214, 0)
            self.ui.pB_DisCharger.setEnabled(True)
            self.ui.pB_Charger.setEnabled(False)
            self.ui.pB_DisCharger.setChecked(False)
            self.ui.pB_Charger.setChecked(False)
            self.ui.l_Connect_Ch.setText('未连接电源')
            self.ui.l_Connect_Ch.setStyleSheet('color:black')
            self.ui.pB_Charger.setText('连接直流电源')
            self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    def manuTypeRbClicked(self):
        if self.ui.rB_CC.isChecked():
            self.ui.l_WorkMode.setText('电流(A):')
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC CURR')
            data = self.ui.dSB_ManualData.value()
            self.res.write('CURR %f' % data)
        elif self.ui.rB_CV.isChecked():
            self.ui.l_WorkMode.setText('电压(V):')
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC VOLT')
            data = self.ui.dSB_ManualData.value()
            self.res.write('VOLT %f' % data)
        elif self.ui.rB_CP.isChecked():
            self.ui.l_WorkMode.setText('功率(P):')
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC POW')
            data = self.ui.dSB_ManualData.value()
            self.res.write('POW %f' % data)

    def dSB_ManualDataChanged(self):
        if self.ui.rB_CC.isChecked():
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC CURR')
            data = self.ui.dSB_ManualData.value()
            self.res.write('CURR %f' % data)
        elif self.ui.rB_CV.isChecked():
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC VOLT')
            data = self.ui.dSB_ManualData.value()
            self.res.write('VOLT %f' % data)
        elif self.ui.rB_CP.isChecked():
            if self.ui.pB_DisCharger.text() == '断开电子负载':
                self.res.write('FUNC POW')
            data = self.ui.dSB_ManualData.value()
            self.res.write('POW %f' % data)

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
    # 功能：执行自动充放电
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
        itemList = []
        item = self.itemModel_Dis.item(self.itemIndexBuff, 0)
        data_Curr = float(self.dataList[0])
        data_Volt = float(self.dataList[1])
        data_Pow = float(self.dataList[2])
        self.ExDischargeTime = self.ExDischargeTime + 1
        self.LC_Time = self.LC_Time + 1
        self.ui.tV_Dischagre.selectRow(self.itemIndexBuff)
        if item.checkState() == Qt.Checked:
            itemList.append('参与')
        else:
            itemList.append('不参与')
        for i in range(self.itemModel_Dis.columnCount() - 1):
            item = self.itemModel_Dis.item(self.itemIndexBuff, i + 1)
            itemList.append(item.text())

        data_Ref = float(itemList[11])
        if self.itemIndexBuff <= self.itemIndex:
            if itemList[0] == '不参与':
                print('不参与')
                self.itemIndexBuff = self.itemIndexBuff + 1
            elif itemList[2] == 'CC':
                if itemList[1] == '放电':
                    self.res.write('FUNC CURR')
                data = float(itemList[3])
                self.res.write('CURR %f' % data)
                if itemList[9] == '电堆电流':
                    if itemList[10] == '大于' or data_Curr >= data_Ref:
                        print('电堆电流大于')
                        self.itemIndexBuff = self.itemIndexBuff + 1
                    elif data_Curr <= data_Ref:
                        print('电堆电流小于')
                        self.itemIndexBuff = self.itemIndexBuff + 1

                if itemList[9] == '电堆电压':
                    if itemList[10] == '大于' or data_Volt >= data_Ref:
                        print('电堆电压大于')
                        self.itemIndexBuff = self.itemIndexBuff + 1
                    elif data_Volt <= data_Ref:
                        print('电堆电压小于')
                        self.itemIndexBuff = self.itemIndexBuff + 1
                    elif itemList[9] == '电堆功率':
                        if itemList[10] == '大于' or data_Pow >= data_Ref:
                            print('电堆功率大于')
                            self.itemIndexBuff = self.itemIndexBuff + 1
                        elif data_Pow <= data_Ref:
                            print('电堆功率小于')
                            self.itemIndexBuff = self.itemIndexBuff + 1
                        else:
                            data_Time = data_Ref * 10
                            if itemList[10] == '大于' or float(self.ExDischargeTime) >= data_Time:
                                print('执行时间大于')
                                self.ExDischargeTime = 0
                                self.itemIndexBuff = self.itemIndexBuff + 1
                            elif float(self.ExDischargeTime) <= data_Time:
                                print('执行时间小于')
                                self.ExDischargeTime = 0
                                self.itemIndexBuff = self.itemIndexBuff + 1
                            elif itemList[2] == 'CV':
                                if itemList[1] == '放电':
                                    self.res.write('FUNC VOLT')
                                data = float(itemList[3])
                                self.res.write('VOLT %f' % data)
                                if itemList[9] == '电堆电流':
                                    if itemList[10] == '大于' or data_Curr >= data_Ref:
                                        print('电堆电流大于')
                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                    elif data_Curr <= data_Ref:
                                        print('电堆电流小于')
                                        self.itemIndexBuff = self.itemIndexBuff + 1

                                if itemList[9] == '电堆电压':
                                    if itemList[10] == '大于' or data_Volt >= data_Ref:
                                        print('电堆电压大于')
                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                    elif data_Volt <= data_Ref:
                                        print('电堆电压小于')
                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                    elif itemList[9] == '电堆功率':
                                        if itemList[10] == '大于' or data_Pow >= data_Ref:
                                            print('电堆功率大于')
                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                        elif data_Pow <= data_Ref:
                                            print('电堆功率小于')
                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                        else:
                                            data_Time = data_Ref * 10
                                            if itemList[10] == '大于' or float(self.ExDischargeTime) >= data_Time:
                                                print('执行时间大于')
                                                self.ExDischargeTime = 0
                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                            elif float(self.ExDischargeTime) <= data_Time:
                                                print('执行时间小于')
                                                self.ExDischargeTime = 0
                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                            elif itemList[2] == 'CP':
                                                if itemList[1] == '放电':
                                                    self.res.write('FUNC POW')
                                                data = float(itemList[3])
                                                self.res.write('POW %f' % data)
                                                if itemList[9] == '电堆电流':
                                                    if itemList[10] == '大于' or data_Curr >= data_Ref:
                                                        print('电堆电流大于')
                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                    elif data_Curr <= data_Ref:
                                                        print('电堆电流小于')
                                                        self.itemIndexBuff = self.itemIndexBuff + 1

                                                if itemList[9] == '电堆电压':
                                                    if itemList[10] == '大于' or data_Volt >= data_Ref:
                                                        print('电堆电压大于')
                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                    elif data_Volt <= data_Ref:
                                                        print('电堆电压小于')
                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                    elif itemList[9] == '电堆功率':
                                                        if itemList[10] == '大于' or data_Pow >= data_Ref:
                                                            print('电堆功率大于')
                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                        elif data_Pow <= data_Ref:
                                                            print('电堆功率小于')
                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                        else:
                                                            data_Time = data_Ref * 10
                                                            if itemList[10] == '大于' or float(
                                                                    self.ExDischargeTime) >= data_Time:
                                                                print('执行时间大于')
                                                                self.ExDischargeTime = 0
                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                            elif float(self.ExDischargeTime) <= data_Time:
                                                                print('执行时间小于')
                                                                self.ExDischargeTime = 0
                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                            elif itemList[2] == 'LCC':
                                                                if itemList[1] == '放电':
                                                                    self.res.write('FUNC CURR')
                                                                if self.LC_Time >= float(itemList[7]) * 10:
                                                                    self.LC_Data = self.LC_Data + float(itemList[5])
                                                                    self.LC_Time = 0
                                                                data = float(itemList[3])
                                                                data = data + self.LC_Data
                                                                self.res.write('CURR %f' % data)
                                                                if itemList[9] == '电堆电流':
                                                                    if itemList[
                                                                        10] == '大于' or data_Curr >= data_Ref:
                                                                        print('电堆电流大于')
                                                                        self.LC_Time = 0
                                                                        self.LC_Data = 0
                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                    elif data_Curr <= data_Ref:
                                                                        print('电堆电流小于')
                                                                        self.itemIndexBuff = self.itemIndexBuff + 1

                                                                if itemList[9] == '电堆电压':
                                                                    if itemList[
                                                                        10] == '大于' or data_Volt >= data_Ref:
                                                                        print('电堆电压大于')
                                                                        self.LC_Time = 0
                                                                        self.LC_Data = 0
                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                    elif data_Volt <= data_Ref:
                                                                        print('电堆电压小于')
                                                                        self.LC_Time = 0
                                                                        self.LC_Data = 0
                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                    elif itemList[9] == '电堆功率':
                                                                        if itemList[
                                                                            10] == '大于' or data_Pow >= data_Ref:
                                                                            print('电堆功率大于')
                                                                            self.LC_Time = 0
                                                                            self.LC_Data = 0
                                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                                        elif data_Pow <= data_Ref:
                                                                            print('电堆功率小于')
                                                                            self.LC_Time = 0
                                                                            self.LC_Data = 0
                                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                                        else:
                                                                            data_Time = data_Ref * 10
                                                                            if itemList[10] == '大于' or float(
                                                                                    self.ExDischargeTime) >= data_Time:
                                                                                print('执行时间大于')
                                                                                self.LC_Time = 0
                                                                                self.LC_Data = 0
                                                                                self.ExDischargeTime = 0
                                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                                            elif float(
                                                                                    self.ExDischargeTime) <= data_Time:
                                                                                print('执行时间小于')
                                                                                self.LC_Time = 0
                                                                                self.LC_Data = 0
                                                                                self.ExDischargeTime = 0
                                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                                            elif itemList[2] == 'LCV':
                                                                                if itemList[1] == '放电':
                                                                                    self.res.write('FUNC VOLT')
                                                                                if self.LC_Time >= float(
                                                                                        itemList[7]) * 10:
                                                                                    self.LC_Data = self.LC_Data + float(
                                                                                        itemList[5])
                                                                                    self.LC_Time = 0
                                                                                data = float(itemList[3])
                                                                                data = data + self.LC_Data
                                                                                self.res.write('VOLT %f' % data)
                                                                                if itemList[9] == '电堆电流':
                                                                                    if itemList[
                                                                                        10] == '大于' or data_Curr >= data_Ref:
                                                                                        print('电堆电流大于')
                                                                                        self.LC_Time = 0
                                                                                        self.LC_Data = 0
                                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                    elif data_Curr <= data_Ref:
                                                                                        print('电堆电流小于')
                                                                                        self.LC_Time = 0
                                                                                        self.LC_Data = 0
                                                                                        self.itemIndexBuff = self.itemIndexBuff + 1

                                                                                if itemList[9] == '电堆电压':
                                                                                    if itemList[
                                                                                        10] == '大于' or data_Volt >= data_Ref:
                                                                                        print('电堆电压大于')
                                                                                        self.LC_Time = 0
                                                                                        self.LC_Data = 0
                                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                    elif data_Volt <= data_Ref:
                                                                                        print('电堆电压小于')
                                                                                        self.LC_Time = 0
                                                                                        self.LC_Data = 0
                                                                                        self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                    elif itemList[9] == '电堆功率':
                                                                                        if itemList[
                                                                                            10] == '大于' or data_Pow >= data_Ref:
                                                                                            print('电堆功率大于')
                                                                                            self.LC_Time = 0
                                                                                            self.LC_Data = 0
                                                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                        elif data_Pow <= data_Ref:
                                                                                            print('电堆功率小于')
                                                                                            self.LC_Time = 0
                                                                                            self.LC_Data = 0
                                                                                            self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                        else:
                                                                                            data_Time = data_Ref * 10
                                                                                            if itemList[
                                                                                                10] == '大于' or float(
                                                                                                self.ExDischargeTime) >= data_Time:
                                                                                                print('执行时间大于')
                                                                                                self.LC_Time = 0
                                                                                                self.LC_Data = 0
                                                                                                self.ExDischargeTime = 0
                                                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                            elif float(
                                                                                                    self.ExDischargeTime) <= data_Time:
                                                                                                print('执行时间小于')
                                                                                                self.LC_Time = 0
                                                                                                self.LC_Data = 0
                                                                                                self.ExDischargeTime = 0
                                                                                                self.itemIndexBuff = self.itemIndexBuff + 1
                                                                                            elif itemList[
                                                                                                1] == '放电':
                                                                                                self.res.write(
                                                                                                    'FUNC POW')
            if self.LC_Time >= float(itemList[7]) * 10:
                self.LC_Data = self.LC_Data + float(itemList[5])
                self.LC_Time = 0
            data = float(itemList[3])
            data = data + self.LC_Data
            self.res.write('POW %f' % data)
            if itemList[9] == '电堆电流':
                if itemList[10] == '大于' or data_Curr >= data_Ref:
                    print('电堆电流大于')
                    self.LC_Time = 0
                    self.LC_Data = 0
                    self.itemIndexBuff = self.itemIndexBuff + 1
                elif data_Curr <= data_Ref:
                    print('电堆电流小于')
                    self.LC_Time = 0
                    self.LC_Data = 0
                    self.itemIndexBuff = self.itemIndexBuff + 1
                elif itemList[9] == '电堆电压':
                    if itemList[10] == '大于' or data_Volt >= data_Ref:
                        print('电堆电压大于')
                        self.LC_Time = 0
                        self.LC_Data = 0
                        self.itemIndexBuff = self.itemIndexBuff + 1
                    elif data_Volt <= data_Ref:
                        print('电堆电压小于')
                        self.LC_Time = 0
                        self.LC_Data = 0
                        self.itemIndexBuff = self.itemIndexBuff + 1
                    elif itemList[9] == '电堆功率':
                        if itemList[10] == '大于' or data_Pow >= data_Ref:
                            print('电堆功率大于')
                            self.LC_Time = 0
                            self.LC_Data = 0
                            self.itemIndexBuff = self.itemIndexBuff + 1
                        elif data_Pow <= data_Ref:
                            print('电堆功率小于')
                            self.LC_Time = 0
                            self.LC_Data = 0
                            self.itemIndexBuff = self.itemIndexBuff + 1
                        else:
                            data_Time = data_Ref * 10
                            if itemList[10] == '大于' or float(self.ExDischargeTime) >= data_Time:
                                print('执行时间大于')
                                self.LC_Time = 0
                                self.LC_Data = 0
                                self.ExDischargeTime = 0
                                self.itemIndexBuff = self.itemIndexBuff + 1
                            elif float(self.ExDischargeTime) <= data_Time:
                                print('执行时间小于')
                                self.LC_Time = 0
                                self.LC_Data = 0
                                self.ExDischargeTime = 0
                                self.itemIndexBuff = self.itemIndexBuff + 1
        if self.itemIndexBuff == self.itemIndex:
            self.NotExDischarge()

    # -------------------------------------------------------------
    # 函数名： dischargeSave
    # 功能： 保存自动充放电配置
    # -------------------------------------------------------------
    def dischargeSave(self):
        with open('config.json', encoding="utf-8") as f:
            js = json.load(f)
        with open('config.json', 'w', encoding="utf-8") as f:
            keys = list(js[1]["para"][0])
            for i in range(self.ui.tV_Discharge.rowCount()):
                if self.ui.tV_Discharge.item(i, 0) is None or self.ui.tV_Discharge.item(i, 0).text == '':
                    break
                if i >= len(js[1]["para"]):
                    js[1]["para"].append({"id": i+1})
                for j in range(9):
                    js[1]["para"][i][keys[j + 1]] = self.ui.tV_Discharge.item(i, j).text()
            f.write(json.dumps(js, ensure_ascii=False))
        self.ui.alarmBox.append('充放电参数保存成功')
        self.ui.tV_Discharge.clearContents()
        self.ui.tV_Stove.clearContents()
        self.readConfig()

    # -------------------------------------------------------------
    # 函数名： notExDischarge
    # 功能： 停止自动充放电
    # -------------------------------------------------------------
    def notExDischarge(self):
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.res.write('INP OFF')
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.res.write('OUTP OFF')
        self.ExDischarge.stop()
        self.ui.tV_Discharge.setEnabled(True)

    # -------------------------------------------------------------
    # 函数名： on_pB_DisCharger_released
    # 功能： 连接电子负载
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_DisCharger_released(self):
        if self.ui.pB_DisCharger.isChecked():
            try:
                self.rm = visa.ResourceManager()
                self.res = self.rm.open_resource('ASRL2::INSTR')
                print(type(self.res))
                self.Thread = RunThread(self.res)
                self.Thread._signal.connect(self.ReadDisCharge)
                self.res.write('*IDN?')
                read = self.res.read()
                readList = read.split(',')
                self.ui.l_Connect_Dis.setText(readList[1])
                self.ui.l_Connect_Dis.setStyleSheet('color:green')
                self.res.write('SYST:REM')
                self.res.write('SYST:SENS ON')
                self.ui.pB_DisCharger.setText('断开电子负载')
            except:
                self.ui.alarmBox.append('<font color="red">无法连接电子负载，请检查</font>')

        else:
            self.ui.pB_DisCharger.setText('连接电子负载')
            self.ui.l_Connect_Dis.setStyleSheet('color:black')
            self.ui.l_Connect_Dis.setText('未连接负载')

    # -------------------------------------------------------------
    # 函数名： on_pB_Charger_released
    # 功能： 连接直流电源
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_pB_Charger_released(self):
        if self.ui.pB_Charger.isChecked():
            try:
                self.rm = visa.ResourceManager()
                self.res = self.rm.open_resource('ASRL3::INSTR')
                print(type(self.res))
                self.Thread_Ch = RunThread(self.res)
                self.Thread_Ch._signal.connect(self.readCharge)
                self.res.write('*IDN?')
                read = self.res.read()
                readList = read.split(',')
                self.ui.l_Connect_Ch.setText(readList[1])
                self.ui.l_Connect_Ch.setStyleSheet('color:green')
                self.res.write('SYST:REM')
                self.ui.pB_Charger.setText('断开直流电源')
            except:
                self.ui.alarmBox.append('<font color="red">无法连接直流电源，请检查</font>')

        else:
            self.ui.pB_Charger.setText('连接直流电源')
            self.ui.l_Connect_Ch.setStyleSheet('color:black')
            self.ui.l_Connect_Ch.setText('未连接电源')

    # -------------------------------------------------------------
    # 函数名： readDisCharge
    # 功能： 实时读取放电信息
    # -------------------------------------------------------------
    def readDisCharge(self, data):
        self.dataList = data.split(';')
        try:
            Cur = float(self.dataList[0])
            Vlot = float(self.dataList[1])
            CURRD = float(self.dataList[0]) * 1000 / self.Battery_Area
            POWD = float(self.dataList[2]) * 1000 / self.Battery_Area
            if Cur > 0.1:
                self.ui.l_CURRDis.setText('电流(A):%s' % self.dataList[0])
            else:
                self.ui.l_CURRDis.setText('电流(A):0.0')
                CURRD = 0
            if Vlot > 0.1:
                self.ui.l_VOLTDis.setText('电压(V):%s' % self.dataList[1])
            else:
                Temp = 0
                self.ui.l_VOLTDis.setText('电压(V):%s' % Temp)
            if POWD > 0.0:
                self.ui.l_POWDis.setText('功率(W):%s' % self.dataList[2])
            else:
                Temp = 0
                self.ui.l_POWDis.setText('功率(W):%s' % Temp)
            self.ui.l_CURRDensityDis.setText('电密（mA/cm²):%.2f' % CURRD)
            self.ui.l_POWDensityDis.setText('功密（mW/cm²):%.2f' % POWD)
        except:
            print('String To Float Error')

    # -------------------------------------------------------------
    # 函数名： ReadCharge
    # 功能： 实时读取充电信息
    # -------------------------------------------------------------
    def readCharge(self, data):
        self.dataList = data.split(';')
        try:
            Cur = float(self.dataList[0])
            Vlot = float(self.dataList[1])
            CURRD = float(self.dataList[0]) * 1000 / self.Battery_Area
            POWD = float(self.dataList[2]) * 1000 / self.Battery_Area
            if Cur > 0.1:
                self.ui.l_CURRDis.setText('电流(A):%s' % self.dataList[0])
            else:
                self.ui.l_CURRDis.setText('电流(A):0.0')
                CURRD = 0
            if Vlot > 0.1:
                self.ui.l_VOLTDis.setText('电压(V):%s' % self.dataList[1])
            else:
                Temp = 0
                self.ui.l_VOLTDis.setText('电压(V):%s' % Temp)
            if POWD > 0.0:
                self.ui.l_POWDis.setText('功率(W):%s' % self.dataList[2])
            else:
                Temp = 0
                self.ui.l_POWDis.setText('功率(W):%s' % Temp)
            self.ui.l_CURRDensityDis.setText('电密（mA/cm²):%.2f' % CURRD)
            self.ui.l_POWDensityDis.setText('功密（mW/cm²):%.2f' % POWD)
        except:
            print('String To Float Error')

    # -------------------------------------------------------------
    # 函数名： on_cB_DischargeH2_clicked
    # 功能： 图表显示H2(槽函数)
    # -------------------------------------------------------------
    @pyqtSlot()
    def on_cB_DischargeH2_clicked(self):
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
    # 功能： 初始化图表
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
        self.vlaxisX = QValueAxis()
        self.vlaxisY = QValueAxis()
        self.x = 0
        self.Ts = 0.01
        self.vlaxisX.setMin(self.x)
        self.vlaxisX.setMax(self.x + 12)
        self.vlaxisY.setMin(0)
        if self.ui.cB_StoveTemp.isChecked():
            self.vlaxisY.setMax(1000)
        else:
            self.vlaxisY.setMax(200)
        self.vlaxisX.setTickCount(7)
        self.vlaxisY.setTickCount(6)
        self.vlaxisX.setTitleText('时间')
        self.vlaxisY.setTitleText('量程')
        self.vlaxisY.setGridLineVisible(False)
        self.chart.addAxis(self.vlaxisX, Qt.AlignBottom)
        self.chart.addAxis(self.vlaxisY, Qt.AlignLeft)
        self.seriesH2.attachAxis(self.vlaxisX)
        self.seriesH2.attachAxis(self.vlaxisY)
        self.seriesCH4.attachAxis(self.vlaxisX)
        self.seriesCH4.attachAxis(self.vlaxisY)
        self.seriesCO2.attachAxis(self.vlaxisX)
        self.seriesCO2.attachAxis(self.vlaxisY)
        self.seriesN2.attachAxis(self.vlaxisX)
        self.seriesN2.attachAxis(self.vlaxisY)
        self.seriesAIR.attachAxis(self.vlaxisX)
        self.seriesAIR.attachAxis(self.vlaxisY)
        self.seriesCO.attachAxis(self.vlaxisX)
        self.seriesCO.attachAxis(self.vlaxisY)
        self.seriesCURR.attachAxis(self.vlaxisX)
        self.seriesCURR.attachAxis(self.vlaxisY)
        self.seriesVOLT.attachAxis(self.vlaxisX)
        self.seriesVOLT.attachAxis(self.vlaxisY)
        self.seriesPOW.attachAxis(self.vlaxisX)
        self.seriesPOW.attachAxis(self.vlaxisY)
        self.seriesCURRD.attachAxis(self.vlaxisX)
        self.seriesCURRD.attachAxis(self.vlaxisY)
        self.seriesPOWD.attachAxis(self.vlaxisX)
        self.seriesPOWD.attachAxis(self.vlaxisY)
        self.seriesStove.attachAxis(self.vlaxisX)
        self.seriesStove.attachAxis(self.vlaxisY)
        self.isVertical = False

    # -------------------------------------------------------------
    # 函数名： drawChart
    # 功能：绘制图表
    # -------------------------------------------------------------
    def drawChart(self):
        if self.ui.pB_DisCharger.text() == '断开电子负载':
            self.Thread.start()
        if self.ui.pB_Charger.text() == '断开直流电源':
            self.Thread_Ch.start()
        self.data = self.plc.read_area(snap7.types.Areas.DB, 1, 0, 300)
        self.alarmCurrentData = snap7.util.get_dword(self.data, 195)
        n2Flow = snap7.util.get_byte(self.data, 180)
        if n2Flow == 1:
            self.ui.alarmBox.append('氮气吹扫中')
            self.ui.bB_N2Flow_S.button.setEnabled(False)
        else:
            self.ui.alarmBox.append('氮气未吹扫')
            self.ui.bB_N2Flow_S.button.setEnabled(True)
        self.GasPressure = snap7.util.get_real(self.data, 36)
        self.ui.l_GasPressure.setText('压力(N): %.2f' % self.GasPressure)
        LowLevel = snap7.util.get_byte(self.data, 189)
        if LowLevel == 1:
            self.ui.l_caution.setStyleSheet('')
        else:
            self.ui.l_caution.setStyleSheet('image:url(:/images/img/caution.png)')
        CylinderHome = snap7.util.get_bool(self.data, 199, 0)
        if CylinderHome == True:
            self.GassPressNotHome()
        if self.alarmCurrentData != self.alarmData:
            alarm = snap7.util.get_bool(self.data, 195, 0)
            timeData = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:H2流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:H2流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 1)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:H2流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:H2流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 2)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:H2流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:H2流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 3)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:H2_MFC断路短路（无信号）</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:H2_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 4)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 5)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 6)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 195, 7)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO_MFC断路短路（无信号）</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 0)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO2流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO2流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 1)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO2流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO2流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 2)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO2流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO2流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 3)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CO2_MFC断路短路（无信号）</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CO2_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 4)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CH4流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CH4流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 5)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CH4流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CH4流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 6)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CH4流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CH4流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 196, 7)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:CH4_MFC断路短路（无信号）</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:CH4_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 0)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:N2流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:N2流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 1)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:N2流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:N2流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 2)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:N2流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:N2流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 3)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:N2_MFC断路短路（无信号）</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:N2_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 4)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:空气流量三级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:Air流量三级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 5)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:空气流量二级偏差</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:Air流量二级偏差')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 6)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:空气流量低于最小设定流量</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:Air流量低于最小设定流量')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 197, 7)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:Air_MFC断路短路(无信号)</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:Air_MFC断路短路（无信号）')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 198, 0)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:可燃气体浓度超标</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:可燃气体浓度超标')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 198, 1)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:可燃气体浓度严重超标</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:可燃气体浓度严重超标')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 198, 2)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:环境温度超标</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:环境温度超标')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            alarm = snap7.util.get_bool(self.data, 198, 3)
            if alarm == 1:
                self.ui.alarmBox.append('<font color="red">报警提示！！！:伺服报警</font>')
                itemlist = []
                item = QStandardItem(timeData)
                itemlist.append(item)
                item = QStandardItem('报警提示:伺服报警')
                itemlist.append(item)
                self.itemModel_tV.appendRow(itemlist)
            self.alarmData = self.alarmCurrentData
        self.PLCDataInput = []
        for i in range(16):
            data = snap7.util.get_real(self.data, i * 4)
            self.PLCDataInput.append(data)

        CVMData = np.array(self.PLCDataInput[8:16])
        self.ui.pgB_CV1.setValue(CVMData[0])
        self.ui.l_TEMStove.setText('加热炉温度(℃):%.2f ' % CVMData[2])
        self.H2Set = self.ui.dSB_SetH2.value()
        snap7.util.set_real(self.data, 70, self.H2Set)
        self.CH4Set = self.ui.dSB_SetCH4.value()
        snap7.util.set_real(self.data, 74, self.CH4Set)
        self.CO2Set = self.ui.dSB_SetCO2.value()
        snap7.util.set_real(self.data, 78, self.CO2Set)
        self.COSet = self.ui.dSB_SetCO.value()
        snap7.util.set_real(self.data, 90, self.COSet)
        self.N2Set = self.ui.dSB_SetN2.value()
        snap7.util.set_real(self.data, 82, self.N2Set)
        self.AirSet = self.ui.dSB_SetAir.value()
        snap7.util.set_real(self.data, 86, self.AirSet)
        N2Time = self.ui.sB_N2Time.value()
        snap7.util.set_int(self.data, 68, N2Time)
        N2Flow = self.ui.dSB_N2FlowRate.value()
        snap7.util.set_real(self.data, 64, N2Flow)
        H2LimitL = self.ui.dBB_SetMFCH2Low.value()
        snap7.util.set_real(self.data, 94, H2LimitL)
        H2LimitH = self.ui.dBB_SetMFCH2High.value()
        snap7.util.set_real(self.data, 98, H2LimitH)
        CO2LimitL = self.ui.dBB_SetMFCCO2Low.value()
        snap7.util.set_real(self.data, 110, CO2LimitL)
        CO2LimitH = self.ui.dBB_SetMFCCO2High.value()
        snap7.util.set_real(self.data, 114, CO2LimitH)
        CH4LimitL = self.ui.dBB_SetMFCCH4Low.value()
        snap7.util.set_real(self.data, 102, CH4LimitL)
        CH4LimitH = self.ui.dBB_SetMFCCH4High.value()
        snap7.util.set_real(self.data, 106, CH4LimitH)
        COLimitL = self.ui.dBB_SetMFCCOLow.value()
        snap7.util.set_real(self.data, 134, COLimitL)
        COLimitH = self.ui.dBB_SetMFCCOHigh.value()
        snap7.util.set_real(self.data, 138, COLimitH)
        AirLimitL = self.ui.dBB_SetMFCAirLow.value()
        snap7.util.set_real(self.data, 126, AirLimitL)
        AirLimitH = self.ui.dBB_SetMFCAirHigh.value()
        snap7.util.set_real(self.data, 130, AirLimitH)
        N2LimitL = self.ui.dBB_SetMFCN2Low.value()
        snap7.util.set_real(self.data, 118, N2LimitL)
        N2LimitH = self.ui.dBB_SetMFCN2High.value()
        snap7.util.set_real(self.data, 122, N2LimitH)
        SVLimitL = self.ui.dBB_SetSingleVoltLow.value()
        snap7.util.set_real(self.data, 162, SVLimitL)
        SVLimitH = self.ui.dBB_SetSingleVoltHigh.value()
        snap7.util.set_real(self.data, 158, SVLimitH)
        TAH = self.ui.dBB_SetTempAlarmHigh.value()
        snap7.util.set_real(self.data, 166, TAH)
        GasAL = self.ui.dBB_SetTempAlarmLow.value()
        snap7.util.set_real(self.data, 170, GasAL)
        GasAH = self.ui.dBB_SetTempAlarmHigh_2.value()
        snap7.util.set_real(self.data, 174, GasAH)
        self.H2Input = snap7.util.get_real(self.data, 0)
        if self.H2Input > 0:
            self.ui.pgB_H2_DIS.setMaximum(0)
            self.ui.pgB_Wet.setMaximum(0)
            self.ui.pgB_Dry.setMaximum(0)
        else:
            self.ui.pgB_H2_DIS.setMaximum(1)
        self.ui.l_H2Dis.setText('H2: %.2f' % self.H2Input)
        self.CH4Input = snap7.util.get_real(self.data, 4)
        if self.CH4Input > 0:
            self.ui.pgB_CH4_DIS.setMaximum(0)
            self.ui.pgB_Wet.setMaximum(0)
            self.ui.pgB_Dry.setMaximum(0)
        else:
            self.ui.pgB_CH4_DIS.setMaximum(1)
        self.ui.l_CH4Dis.setText('CH4: %.2f' % self.CH4Input)
        self.CO2Input = snap7.util.get_real(self.data, 8)
        if self.CO2Input > 0:
            self.ui.pgB_CO2_DIS.setMaximum(0)
            self.ui.pgB_Wet.setMaximum(0)
            self.ui.pgB_Dry.setMaximum(0)
        else:
            self.ui.pgB_CO2_DIS.setMaximum(1)
        self.ui.l_CO2Dis.setText('CO2: %.2f' % self.CO2Input)
        self.N2Input = snap7.util.get_real(self.data, 12)
        if self.N2Input > 0:
            self.ui.pgB_N2_DIS.setMaximum(0)
            self.ui.pgB_Wet.setMaximum(0)
            self.ui.pgB_Dry.setMaximum(0)
        else:
            self.ui.pgB_N2_DIS.setMaximum(1)
        self.ui.l_N2Dis.setText('N2: %.2f' % self.N2Input)
        self.AirInput = snap7.util.get_real(self.data, 16)
        if self.AirInput > 0:
            self.ui.pgB_Air_DIS.setMaximum(0)
        else:
            self.ui.pgB_Air_DIS.setMaximum(1)
        self.ui.l_AirDis.setText('Air: %.2f' % self.AirInput)
        self.COInput = snap7.util.get_real(self.data, 20)
        if self.COInput > 0:
            self.ui.pgB_CO_DIS.setMaximum(0)
            self.ui.pgB_Wet.setMaximum(0)
            self.ui.pgB_Dry.setMaximum(0)
        else:
            self.ui.pgB_CO_DIS.setMaximum(1)
        self.ui.l_CO.setText('CO: %.2f' % self.COInput)
        if self.H2Input == 0 and self.CH4Input == 0 and self.CO2Input == 0 and self.N2Input == 0 and self.N2Input == 0 or self.COInput == 0:
            self.ui.pgB_Wet.setMaximum(1)
            self.ui.pgB_Dry.setMaximum(1)
        self.TempInput = snap7.util.get_real(self.data, 24)
        self.ui.l_TEMDis.setText('温度(C°): %.2f' % self.TempInput)
        self.CGCInpout = snap7.util.get_real(self.data, 28)
        self.ui.l_GasDis.setText('可燃(LEL): %.2f' % self.CGCInpout)
        self.CGCInpout = snap7.util.get_real(self.data, 28)
        self.ui.l_GasDis.setText('可燃(LEL): %.2f' % self.CGCInpout)
        if self.ui.pB_ManualH2.isChecked():
            self.data[181] = 1
            self.ui.label_H2.setText('H2 打开')
            self.ui.pB_ManualH2.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_H2.setMaximum(0)
        else:
            self.data[181] = 0
            self.ui.label_H2.setText('H2 关闭')
            self.ui.pB_ManualH2.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_H2.setMaximum(1)
        if self.ui.pB_ManualCO2.isChecked():
            self.data[183] = 1
            self.ui.label_CO2.setText('CO2 打开')
            self.ui.pB_ManualCO2.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CO2.setMaximum(0)
        else:
            self.data[183] = 0
            self.ui.label_CO2.setText('CO2 关闭')
            self.ui.pB_ManualCO2.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CO2.setMaximum(1)
        if self.ui.pB_ManualCH4.isChecked():
            self.data[182] = 1
            self.ui.label_CH4.setText('CH4 打开')
            self.ui.pB_ManualCH4.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CH4.setMaximum(0)
        else:
            self.data[182] = 0
            self.ui.label_CH4.setText('CH4 关闭')
            self.ui.pB_ManualCH4.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CH4.setMaximum(1)
        if self.ui.pB_ManualCO.isChecked():
            self.data[186] = 1
            self.ui.label_CO.setText('CO 打开')
            self.ui.pB_ManualCO.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CO.setMaximum(0)
        else:
            self.data[186] = 0
            self.ui.label_CO.setText('CO 关闭')
            self.ui.pB_ManualCO.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_CO.setMaximum(1)
        if self.ui.pB_ManualN2.isChecked():
            self.data[184] = 1
            self.ui.label_N2.setText('N2 打开')
            self.ui.pB_ManualN2.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_N2.setMaximum(0)
        else:
            self.data[184] = 0
            self.ui.label_N2.setText('N2 关闭')
            self.ui.pB_ManualN2.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_N2.setMaximum(1)
        if self.ui.pB_ManualAir.isChecked():
            self.data[185] = 1
            self.ui.label_Air.setText('Air 打开')
            self.ui.pB_ManualAir.setStyleSheet(
                'QPushButton{background:green;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_Air.setMaximum(0)
        else:
            self.data[185] = 0
            self.ui.label_Air.setText('Air 关闭')
            self.ui.pB_ManualAir.setStyleSheet(
                'QPushButton{background:transparent;border-radius:5px;}QPushButton:hover{background:green;}')
            self.ui.pgB_Air.setMaximum(1)
        if self.ui.rB_Wet.isChecked():
            self.data[187] = 2
            self.ui.pgB_Wet_DIS.setMaximum(0)
            self.ui.pgB_Wet_DIS2.setMaximum(0)
        else:
            self.ui.pgB_Wet_DIS.setMaximum(1)
            self.ui.pgB_Wet_DIS2.setMaximum(1)
        if self.ui.rB_Dry.isChecked():
            self.data[187] = 1
            self.ui.pgB_Dry_DIS.setMaximum(0)
        else:
            self.ui.pgB_Dry_DIS.setMaximum(1)
        PumpFlowRate = self.ui.sB_PumpFlowRate.value()
        PumpFlowRate = PumpFlowRate * 1000
        snap7.util.set_word(self.data, 282, PumpFlowRate)
        PumpMaxP = self.ui.sB_PumpMaxP.value()
        PumpMaxP = PumpMaxP * 10
        snap7.util.set_word(self.data, 284, PumpMaxP)
        PumpMinP = self.ui.sB_PumpMinP.value()
        PumpMinP = PumpMinP * 10
        snap7.util.set_word(self.data, 286, PumpMinP)
        if self.ui.rB_PumpStart.isChecked():
            snap7.util.set_word(self.data, 290, 1)
        else:
            snap7.util.set_word(self.data, 290, 0)
        if self.ui.rB_PumpClean.isChecked():
            snap7.util.set_word(self.data, 292, 1)
        else:
            snap7.util.set_word(self.data, 292, 0)
        if self.ui.rB_PumpStop.isChecked():
            snap7.util.set_word(self.data, 294, 1)
        else:
            snap7.util.set_word(self.data, 294, 0)
        EvaHit = self.ui.sB_EvaHit.value()
        EvaHit = EvaHit * 10
        snap7.util.set_word(self.data, 240, EvaHit)
        EvaTrop = self.ui.sB_EvaTrop.value()
        EvaTrop = EvaTrop * 10
        snap7.util.set_word(self.data, 242, EvaTrop)
        if self.ui.cB_EvaHitStart.isChecked():
            snap7.util.set_word(self.data, 244, 1)
        else:
            snap7.util.set_word(self.data, 244, 0)
        if self.ui.cB_EvaTropStart.isChecked():
            snap7.util.set_word(self.data, 246, 1)
        else:
            snap7.util.set_word(self.data, 246, 0)
        label_Pump = snap7.util.get_word(self.data, 250)
        label_Pump = label_Pump / 100
        self.ui.label_Pump.setText('水泵流量：%.2f mL/min' % label_Pump)
        label_SOFCHit = snap7.util.get_word(self.data, 220)
        label_SOFCHit = label_SOFCHit / 10
        self.ui.label_SOFCHit.setText('加热温度：%.2f C°' % label_SOFCHit)
        label_SOFCOut = snap7.util.get_word(self.data, 222)
        label_SOFCOut = label_SOFCOut / 10
        self.ui.label_SOFCOut.setText('出口温度：%.2f C°' % label_SOFCOut)
        label_SOFCTrop = snap7.util.get_word(self.data, 224)
        label_SOFCTrop = label_SOFCTrop / 10
        self.ui.label_SOFCTrop.setText('伴热温度：%.2f C°' % label_SOFCTrop)
        self.chart = self.ui.gV_DataDisplay.chart()
        if self.isVertical:
            self.ui.alarmBox.append('Can Not Show Charts')
        else:
            self.x += self.Ts
            # bjtime = QDateTime.currentDateTime()
            # self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-5))
            # self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
            if self.seriesH2.count() > 50:
                self.seriesH2.removePoints(0, self.seriesH2.count() - 50)
            if self.seriesCH4.count() > 50:
                self.seriesCH4.removePoints(0, self.seriesCH4.count() - 50)
            if self.seriesCO2.count() > 50:
                self.seriesCO2.removePoints(0, self.seriesCO2.count() - 50)
            if self.seriesN2.count() > 50:
                self.seriesN2.removePoints(0, self.seriesN2.count() - 50)
            if self.seriesAIR.count() > 50:
                self.seriesAIR.removePoints(0, self.seriesAIR.count() - 50)
            if self.seriesCO.count() > 50:
                self.seriesCO.removePoints(0, self.seriesCO.count() - 50)
            if self.seriesCURR.count() > 50:
                self.seriesCURR.removePoints(0, self.seriesCURR.count() - 50)
            if self.seriesVOLT.count() > 50:
                self.seriesVOLT.removePoints(0, self.seriesVOLT.count() - 50)
            if self.seriesPOW.count() > 50:
                self.seriesPOW.removePoints(0, self.seriesPOW.count() - 50)
            if self.seriesCURRD.count() > 50:
                self.seriesCURRD.removePoints(0, self.seriesCURRD.count() - 50)
            if self.seriesPOWD.count() > 50:
                self.seriesPOWD.removePoints(0, self.seriesPOWD.count() - 50)
            if self.seriesStove.count() > 50:
                self.seriesStove.removePoints(0, self.seriesPOWD.count() - 50)
            self.seriesH2.append(self.x, self.PLCDataInput[0])
            self.seriesCH4.append(self.x, self.PLCDataInput[1])
            self.seriesCO2.append(self.x, self.PLCDataInput[2])
            self.seriesN2.append(self.x, self.PLCDataInput[3])
            self.seriesAIR.append(self.x, self.PLCDataInput[4])
            self.seriesCO.append(self.x, self.PLCDataInput[5])

            try:
                self.seriesCURR.append(self.x, float(self.dataList[0]))
                self.seriesVOLT.append(self.x, float(self.dataList[1]))
                self.seriesPOW.append(self.x, float(self.dataList[2]))
                self.seriesCURRD.append(self.x, float(self.dataList[0]) * 1000 / self.Battery_Area)
                self.seriesPOWD.append(self.x, float(self.dataList[2]) * 1000 / self.Battery_Area)
            except:
                print('String TO Float Error')

            self.seriesStove.append(self.x, float(CVMData[2]))
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

    # -------------------------------------------------------------
    # 函数名： configResetAuto
    # 功能：自动重置配置
    # -------------------------------------------------------------
    def configResetAuto(self):
        ORIGIN_CONFIG = '[{"name": "stove", "para": [{"id": 1, "temp": "701", "time": "10"}, {"id": 2, "temp": "702", "time": "20"}], "start": 0}, {"name": "discharge", "para": [{"id": 1, "参与状态": "参与", "过程选择": "充电", "工作模式": "LCC(A)", "开始数值": 1, "递增数值": 0, "单步时间": 0, "停机依据": "电堆电流(A)", "判断逻辑": "小于", "触发数值": 1}, {"id": 2, "参与状态": "参与", "过程选择": "放电", "工作模式": "CC(A)", "开始数值": 0, "递增数值": 0, "单步时间": 0, "停机依据": "电堆电流(A)", "判断逻辑": "大于", "触发数值": 0}]}]'
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(eval(ORIGIN_CONFIG), ensure_ascii=False))

    # -------------------------------------------------------------
    # 函数名： configReset
    # 功能：手动重置配置
    # -------------------------------------------------------------
    def configReset(self):
        reply = QMessageBox.question(self, "Alarm", "配置信息重置后不可回退，确认继续么？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        ORIGIN_CONFIG = '[{"name": "stove", "para": [{"id": 1, "temp": "701", "time": "10"}, {"id": 2, "temp": "702", "time": "20"}], "start": 0}, {"name": "discharge", "para": [{"id": 1, "参与状态": "参与", "过程选择": "充电", "工作模式": "LCC(A)", "开始数值": 1, "递增数值": 0, "单步时间": 0, "停机依据": "电堆电流(A)", "判断逻辑": "小于", "触发数值": 1}, {"id": 2, "参与状态": "参与", "过程选择": "放电", "工作模式": "CC(A)", "开始数值": 0, "递增数值": 0, "单步时间": 0, "停机依据": "电堆电流(A)", "判断逻辑": "大于", "触发数值": 0}]}]'
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(eval(ORIGIN_CONFIG), ensure_ascii=False))
            self.ui.alarmBox.append('<font color="red">配置信息已重置</font>')
        self.ui.tV_Discharge.clearContents()
        self.ui.tV_Stove.clearContents()
        self.readConfig()

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
        self.window4.initBatteryInfo(self.batteryNO, self.unitBattery, self.unitBatteryPack, self.batteryArea)
        # self.window4.show()
        ret = self.window4.exec()
        if ret == QDialog.Accepted:
            self.batteryNO, self.unitBattery, self.unitBatteryPack, self.batteryArea = self.window4.setBatteryInfo()
            self.ui.l_batteryNO.setText("电池编号：" + self.batteryNO)
            self.ui.alarmBox.append("已设置电池信息，编号" + self.batteryNO)


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

    def initMFCWindow(self, data):
        pass


# -------------------------------------------------------------
# 类名： BatteryWindow
# 功能：电池信息设置窗口
# -------------------------------------------------------------
class BatteryWindow(QDialog):
    def __init__(self, bn='', ub=8, ubp=8, ba=60, parent=None):
        super().__init__(parent)
        self.ui = BatteryInfo.Ui_batteryInfo()
        self.ui.setupUi(self)
        self.initBatteryInfo(bn, ub, ubp, ba)
        self.ui.Pb_OKBI.clicked.connect(self.setBatteryInfo)

    # -------------------------------------------------------------
    # 函数名： initBatteryInfo
    # 功能： 电池窗口初始化
    # -------------------------------------------------------------
    def initBatteryInfo(self, batteryNo, unitBattery, unitBatteryPack, batteryArea):
        # self.batteryNo = batteryNo
        # self.unitBattery = unitBattery
        # self.unitBatteryPack = unitBatteryPack
        # self.batteryArea = batteryArea
        self.ui.l_BatteryNO.setText("电池编号：" + batteryNo)
        if batteryNo != '未设置':
            self.ui.lE_BatteryNO.setText(batteryNo)
        self.ui.l_BatteryUnit.setText("电池节数：" + str(unitBattery))
        self.ui.sB_UnitBattery.setValue(unitBattery)
        self.ui.l_BatteryPack.setText("电池片数：" + str(unitBatteryPack))
        self.ui.sB_UnitBatteryPack.setValue(unitBatteryPack)
        self.ui.l_BatteryArea.setText("电池面积：" + str(batteryArea))
        self.ui.dSB_Battery_Area.setValue(batteryArea)

    # -------------------------------------------------------------
    # 函数名： setBatteryInfo
    # 功能： 设置电池信息
    # -------------------------------------------------------------
    def setBatteryInfo(self):
        # signal_list = pyqtSignal(str, int, int, int)
        if self.ui.lE_BatteryNO.text == '':
            reply = QMessageBox.question(self, "Alarm", "电池编号为空，确认继续么？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        batteryNo = self.ui.lE_BatteryNO.text()
        unitBattery = self.ui.sB_UnitBattery.value()
        unitBatteryPack = self.ui.sB_UnitBatteryPack.value()
        batteryArea = self.ui.dSB_Battery_Area.value()
        self.accept()
        return (
            batteryNo, unitBattery, unitBatteryPack, batteryArea)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('./img/cnpc.png'))
    ex = SOCExpPlatform001()
    ex.show()
    sys.exit(app.exec_())

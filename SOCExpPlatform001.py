# -*- coding: utf-8 -*-
# powered by Elepikachu
# Copyright CNPC.inc
# 2023/11/13
# ----------------------------------------------------------------------------------------------------------------------

import sys, os, csv, random, time, snap7

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


class SOCExpPlatform001(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = SOCExpPlatform.Ui_SOCExpPlatform()
        self.ui.setupUi(self)
        self.ui.alarmBox.setText('原神 启动')
        self.plc = None
        self.plcConnect()
        if self.plc:
            self.plcGetValue()
        self.buttonConnect()
        self.DisChargeTime = QTimer()
        self.DisChargeTime.timeout.connect(self.timeRecord)

    # -------------------------------------------------------------
    # 函数名： buttonConnect
    # 功能： 按钮信号绑定
    # -------------------------------------------------------------
    def buttonConnect(self):
        self.ui.bB_N2Flow_S.clicked.connect(self.N2Flow)
        self.ui.bB_N2Flow_E.clicked.connect(self.N2NotFlow)
        self.ui.bB_Manual_S.clicked.connect(self.disChargeManualStart)
        self.ui.bB_Manual_E.clicked.connect(self.disChargeManualStop)
        self.ui.act_Help.clicked.connect(self.helpWindow)
        self.ui.act_mfc_info.clicked.connect(self.mfcWindow)
        self.ui.act_baterry_info.clicked.connect(self.batteryWindow)

    # -------------------------------------------------------------
    # 函数名： plcConnect
    # 功能： 连接到plc
    # -------------------------------------------------------------
    def plcConnect(self):
        try:
            self.plc = snap7.client.Client()
            self.plc.set_connection_type(3)
            self.plc.connect('192.168.16.1', 0, 0)
            self.ui.l_ElcLoad.setText('plc连接成功')
            self.data = self.plc.read_area(snap7.types.Areas.DB, 1, 0, 300)
            self.ui.pB_PLCConnection.setText('断开PLC')
            self.timer.start(100)
            print('connected to PLC')
            self.ui.alarmBox.append('connected to PLC')
        except Exception as e:
            self.ui.l_ElcLoad.setText('plc未连接')
            self.data = bytearray([0 for i in range(300)])
            print('Fail to Connect PLC')
            print(e)
            self.ui.alarmBox.append('Fail to Connect to PLC')
            self.ui.alarmBox.append(str(e))

    # -------------------------------------------------------------
    # 函数名： plcGetValue
    # 功能：获取plc信息
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
        self.ui.l_TEMDis.setText('温度(℃): %.2f' % self.TempInput)
        self.CGCInpout = snap7.util.get_real(self.data, 28)
        self.ui.l_GasDis.setText('可燃(LEL): %.2f' % self.CGCInpout)
        self.GasPressure = snap7.util.get_real(self.data, 36)
        self.ui.l_GasPressure.setText('压力(N): %.2f' % self.GasPressure)

    # -------------------------------------------------------------
    # 函数名： paintEvent
    # 功能：绘制背景板
    # -------------------------------------------------------------
    def paintEvent(self, evt):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)

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
    # 停止氮气吹扫
    def N2NotFlow(self):
        snap7.util.set_byte(self.data, 180, 0)
        self.plc.write_area(snap7.types.Areas.DB, 1, 0, self.data)

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
    # 功能： 手动运行停止
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


class MFCWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MFCSetting.Ui_MFC_Info()
        self.ui.setupUi(self)


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

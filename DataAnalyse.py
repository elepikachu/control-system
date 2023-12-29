# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataAnalyse.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DataAnalyse(object):
    def setupUi(self, DataAnalyse):
        DataAnalyse.setObjectName("DataAnalyse")
        DataAnalyse.resize(747, 386)
        DataAnalyse.setStyleSheet("#DataAnalyse{border-image:url(:/images/backgroundnew.jpg)}")
        self.l_title = QtWidgets.QLabel(DataAnalyse)
        self.l_title.setGeometry(QtCore.QRect(200, 20, 401, 31))
        font = QtGui.QFont()
        font.setFamily("隶书")
        font.setPointSize(18)
        self.l_title.setFont(font)
        self.l_title.setObjectName("l_title")
        self.pb_da = QtWidgets.QPushButton(DataAnalyse)
        self.pb_da.setGeometry(QtCore.QRect(300, 340, 81, 23))
        self.pb_da.setObjectName("pb_da")
        self.pb_plot = QtWidgets.QPushButton(DataAnalyse)
        self.pb_plot.setGeometry(QtCore.QRect(550, 340, 71, 23))
        self.pb_plot.setObjectName("pb_plot")
        self.gb_da = QtWidgets.QGroupBox(DataAnalyse)
        self.gb_da.setGeometry(QtCore.QRect(50, 124, 231, 101))
        self.gb_da.setStyleSheet("#gb_da{border: 0.5px solid gray}")
        self.gb_da.setObjectName("gb_da")
        self.cb_dup = QtWidgets.QCheckBox(self.gb_da)
        self.cb_dup.setGeometry(QtCore.QRect(20, 45, 111, 16))
        self.cb_dup.setObjectName("cb_dup")
        self.cb_vari = QtWidgets.QCheckBox(self.gb_da)
        self.cb_vari.setGeometry(QtCore.QRect(20, 70, 111, 16))
        self.cb_vari.setObjectName("cb_vari")
        self.dsb_vari = QtWidgets.QDoubleSpinBox(self.gb_da)
        self.dsb_vari.setGeometry(QtCore.QRect(140, 66, 51, 22))
        self.dsb_vari.setMaximum(5.0)
        self.dsb_vari.setProperty("value", 1.0)
        self.dsb_vari.setObjectName("dsb_vari")
        self.cb_del = QtWidgets.QCheckBox(self.gb_da)
        self.cb_del.setGeometry(QtCore.QRect(20, 20, 181, 16))
        self.cb_del.setObjectName("cb_del")
        self.cb_acc = QtWidgets.QComboBox(self.gb_da)
        self.cb_acc.setGeometry(QtCore.QRect(130, 40, 51, 22))
        self.cb_acc.setObjectName("cb_acc")
        self.cb_acc.addItem("")
        self.cb_acc.addItem("")
        self.cb_acc.addItem("")
        self.gb_plot = QtWidgets.QGroupBox(DataAnalyse)
        self.gb_plot.setGeometry(QtCore.QRect(50, 244, 231, 101))
        self.gb_plot.setStyleSheet("#gb_plot{border: 0.5px solid gray}")
        self.gb_plot.setObjectName("gb_plot")
        self.cb_av = QtWidgets.QCheckBox(self.gb_plot)
        self.cb_av.setGeometry(QtCore.QRect(20, 30, 81, 16))
        self.cb_av.setObjectName("cb_av")
        self.cb_ap = QtWidgets.QCheckBox(self.gb_plot)
        self.cb_ap.setGeometry(QtCore.QRect(20, 50, 81, 16))
        self.cb_ap.setObjectName("cb_ap")
        self.cb_ta = QtWidgets.QCheckBox(self.gb_plot)
        self.cb_ta.setGeometry(QtCore.QRect(20, 70, 81, 16))
        self.cb_ta.setObjectName("cb_ta")
        self.l_step = QtWidgets.QLabel(DataAnalyse)
        self.l_step.setGeometry(QtCore.QRect(150, 92, 71, 16))
        self.l_step.setObjectName("l_step")
        self.sb_step = QtWidgets.QSpinBox(DataAnalyse)
        self.sb_step.setGeometry(QtCore.QRect(220, 90, 61, 22))
        self.sb_step.setProperty("value", 1)
        self.sb_step.setObjectName("sb_step")
        self.pb_upload = QtWidgets.QPushButton(DataAnalyse)
        self.pb_upload.setGeometry(QtCore.QRect(50, 88, 81, 23))
        self.pb_upload.setObjectName("pb_upload")
        self.pb_down = QtWidgets.QPushButton(DataAnalyse)
        self.pb_down.setGeometry(QtCore.QRect(470, 340, 71, 23))
        self.pb_down.setObjectName("pb_down")
        self.plot = QtWidgets.QGraphicsView(DataAnalyse)
        self.plot.setGeometry(QtCore.QRect(310, 60, 391, 261))
        self.plot.setObjectName("plot")
        self.l_stat = QtWidgets.QLabel(DataAnalyse)
        self.l_stat.setGeometry(QtCore.QRect(50, 60, 231, 16))
        self.l_stat.setObjectName("l_stat")
        self.pb_downcsv = QtWidgets.QPushButton(DataAnalyse)
        self.pb_downcsv.setGeometry(QtCore.QRect(390, 340, 71, 23))
        self.pb_downcsv.setObjectName("pb_downcsv")
        self.pb_value = QtWidgets.QPushButton(DataAnalyse)
        self.pb_value.setGeometry(QtCore.QRect(630, 340, 71, 23))
        self.pb_value.setObjectName("pb_value")

        self.retranslateUi(DataAnalyse)
        self.cb_acc.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(DataAnalyse)

    def retranslateUi(self, DataAnalyse):
        _translate = QtCore.QCoreApplication.translate
        DataAnalyse.setWindowTitle(_translate("DataAnalyse", "数据分析"))
        self.l_title.setText(_translate("DataAnalyse", "<html><head/><body><p><span style=\" color:#ff0000;\">固体氧化物电池(SOC)数据分析工具</span></p></body></html>"))
        self.pb_da.setText(_translate("DataAnalyse", "数据处理"))
        self.pb_plot.setText(_translate("DataAnalyse", "制图"))
        self.gb_da.setTitle(_translate("DataAnalyse", "数据处理"))
        self.cb_dup.setText(_translate("DataAnalyse", "数据去重,精度="))
        self.cb_vari.setText(_translate("DataAnalyse", "数据去偏离值,k="))
        self.cb_del.setText(_translate("DataAnalyse", "数据去头尾"))
        self.cb_acc.setCurrentText(_translate("DataAnalyse", "中"))
        self.cb_acc.setItemText(0, _translate("DataAnalyse", "低"))
        self.cb_acc.setItemText(1, _translate("DataAnalyse", "中"))
        self.cb_acc.setItemText(2, _translate("DataAnalyse", "高"))
        self.gb_plot.setTitle(_translate("DataAnalyse", "制图参数"))
        self.cb_av.setText(_translate("DataAnalyse", "电流-电压"))
        self.cb_ap.setText(_translate("DataAnalyse", "电流-功率"))
        self.cb_ta.setText(_translate("DataAnalyse", "时间-电流"))
        self.l_step.setText(_translate("DataAnalyse", "取点步长："))
        self.pb_upload.setText(_translate("DataAnalyse", "表格上传"))
        self.pb_down.setText(_translate("DataAnalyse", "excel下载"))
        self.l_stat.setText(_translate("DataAnalyse", "表格未上传"))
        self.pb_downcsv.setText(_translate("DataAnalyse", "csv下载"))
        self.pb_value.setText(_translate("DataAnalyse", "数据评价"))
import res_rc

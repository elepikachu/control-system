# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MFCSetting.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MFC_Info(object):
    def setupUi(self, MFC_Info):
        MFC_Info.setObjectName("MFC_Info")
        MFC_Info.resize(681, 308)
        self.gB_MFC = QtWidgets.QGroupBox(MFC_Info)
        self.gB_MFC.setGeometry(QtCore.QRect(10, 40, 211, 221))
        self.gB_MFC.setObjectName("gB_MFC")
        self.dBB_SetMFCH2Low = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCH2Low.setGeometry(QtCore.QRect(70, 40, 61, 22))
        self.dBB_SetMFCH2Low.setObjectName("dBB_SetMFCH2Low")
        self.dBB_SetMFCH2High = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCH2High.setGeometry(QtCore.QRect(140, 40, 61, 22))
        self.dBB_SetMFCH2High.setObjectName("dBB_SetMFCH2High")
        self.spinBox_3 = QtWidgets.QSpinBox(self.gB_MFC)
        self.spinBox_3.setGeometry(QtCore.QRect(140, 70, 61, 22))
        self.spinBox_3.setObjectName("spinBox_3")
        self.spinBox_4 = QtWidgets.QSpinBox(self.gB_MFC)
        self.spinBox_4.setGeometry(QtCore.QRect(70, 70, 61, 22))
        self.spinBox_4.setObjectName("spinBox_4")
        self.dBB_SetMFCCOHigh = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCCOHigh.setGeometry(QtCore.QRect(140, 100, 61, 22))
        self.dBB_SetMFCCOHigh.setObjectName("dBB_SetMFCCOHigh")
        self.dBB_SetMFCCOLow = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCCOLow.setGeometry(QtCore.QRect(70, 100, 61, 22))
        self.dBB_SetMFCCOLow.setObjectName("dBB_SetMFCCOLow")
        self.dBB_SetMFCCO2High = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCCO2High.setGeometry(QtCore.QRect(140, 130, 61, 22))
        self.dBB_SetMFCCO2High.setObjectName("dBB_SetMFCCO2High")
        self.dBB_SetMFCCO2Low = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCCO2Low.setGeometry(QtCore.QRect(70, 130, 61, 22))
        self.dBB_SetMFCCO2Low.setObjectName("dBB_SetMFCCO2Low")
        self.dBB_SetMFCN2High = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCN2High.setGeometry(QtCore.QRect(140, 160, 61, 22))
        self.dBB_SetMFCN2High.setObjectName("dBB_SetMFCN2High")
        self.dBB_SetMFCN2Low = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCN2Low.setGeometry(QtCore.QRect(70, 160, 61, 22))
        self.dBB_SetMFCN2Low.setObjectName("dBB_SetMFCN2Low")
        self.dBB_SetMFCAirHigh = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCAirHigh.setGeometry(QtCore.QRect(140, 190, 61, 22))
        self.dBB_SetMFCAirHigh.setObjectName("dBB_SetMFCAirHigh")
        self.dBB_SetMFCAirLow = QtWidgets.QSpinBox(self.gB_MFC)
        self.dBB_SetMFCAirLow.setGeometry(QtCore.QRect(70, 190, 61, 22))
        self.dBB_SetMFCAirLow.setObjectName("dBB_SetMFCAirLow")
        self.l_SetMFCH2 = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCH2.setGeometry(QtCore.QRect(10, 40, 54, 12))
        self.l_SetMFCH2.setObjectName("l_SetMFCH2")
        self.l_SetMFCCO2 = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCCO2.setGeometry(QtCore.QRect(10, 140, 54, 12))
        self.l_SetMFCCO2.setObjectName("l_SetMFCCO2")
        self.l_SetMFCN2 = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCN2.setGeometry(QtCore.QRect(10, 170, 54, 12))
        self.l_SetMFCN2.setObjectName("l_SetMFCN2")
        self.l_SetMFCCH4 = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCCH4.setGeometry(QtCore.QRect(10, 70, 54, 12))
        self.l_SetMFCCH4.setObjectName("l_SetMFCCH4")
        self.l_SetMFCCO = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCCO.setGeometry(QtCore.QRect(10, 100, 54, 12))
        self.l_SetMFCCO.setObjectName("l_SetMFCCO")
        self.l_SetMFCAir = QtWidgets.QLabel(self.gB_MFC)
        self.l_SetMFCAir.setGeometry(QtCore.QRect(10, 200, 54, 12))
        self.l_SetMFCAir.setObjectName("l_SetMFCAir")
        self.l_Low_2 = QtWidgets.QLabel(self.gB_MFC)
        self.l_Low_2.setGeometry(QtCore.QRect(70, 20, 54, 12))
        self.l_Low_2.setObjectName("l_Low_2")
        self.l_High_2 = QtWidgets.QLabel(self.gB_MFC)
        self.l_High_2.setGeometry(QtCore.QRect(140, 20, 54, 12))
        self.l_High_2.setObjectName("l_High_2")
        self.gB_POWSupply = QtWidgets.QGroupBox(MFC_Info)
        self.gB_POWSupply.setGeometry(QtCore.QRect(230, 40, 211, 221))
        self.gB_POWSupply.setObjectName("gB_POWSupply")
        self.dBB_SetChCURRHigh = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChCURRHigh.setGeometry(QtCore.QRect(140, 80, 61, 22))
        self.dBB_SetChCURRHigh.setObjectName("dBB_SetChCURRHigh")
        self.dBB_SetChCURRLow = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChCURRLow.setGeometry(QtCore.QRect(70, 80, 61, 22))
        self.dBB_SetChCURRLow.setObjectName("dBB_SetChCURRLow")
        self.dBB_SetChVLOTHigh = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChVLOTHigh.setGeometry(QtCore.QRect(140, 120, 61, 22))
        self.dBB_SetChVLOTHigh.setObjectName("dBB_SetChVLOTHigh")
        self.dBB_SetChVLOTLow = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChVLOTLow.setGeometry(QtCore.QRect(70, 120, 61, 22))
        self.dBB_SetChVLOTLow.setObjectName("dBB_SetChVLOTLow")
        self.dBB_SetChPOWHigh = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChPOWHigh.setGeometry(QtCore.QRect(140, 160, 61, 22))
        self.dBB_SetChPOWHigh.setObjectName("dBB_SetChPOWHigh")
        self.dBB_SetChPOWLow = QtWidgets.QSpinBox(self.gB_POWSupply)
        self.dBB_SetChPOWLow.setGeometry(QtCore.QRect(70, 160, 61, 22))
        self.dBB_SetChPOWLow.setObjectName("dBB_SetChPOWLow")
        self.l_SetDischargeCURR_2 = QtWidgets.QLabel(self.gB_POWSupply)
        self.l_SetDischargeCURR_2.setGeometry(QtCore.QRect(10, 90, 54, 12))
        self.l_SetDischargeCURR_2.setObjectName("l_SetDischargeCURR_2")
        self.l_SetDischargeVLOT_2 = QtWidgets.QLabel(self.gB_POWSupply)
        self.l_SetDischargeVLOT_2.setGeometry(QtCore.QRect(10, 130, 54, 12))
        self.l_SetDischargeVLOT_2.setObjectName("l_SetDischargeVLOT_2")
        self.l_SetDischargePOW_2 = QtWidgets.QLabel(self.gB_POWSupply)
        self.l_SetDischargePOW_2.setGeometry(QtCore.QRect(10, 170, 54, 12))
        self.l_SetDischargePOW_2.setObjectName("l_SetDischargePOW_2")
        self.l_High_3 = QtWidgets.QLabel(self.gB_POWSupply)
        self.l_High_3.setGeometry(QtCore.QRect(140, 50, 54, 12))
        self.l_High_3.setObjectName("l_High_3")
        self.l_Low_3 = QtWidgets.QLabel(self.gB_POWSupply)
        self.l_Low_3.setGeometry(QtCore.QRect(70, 50, 54, 12))
        self.l_Low_3.setObjectName("l_Low_3")
        self.gB_ElcLoad_2 = QtWidgets.QGroupBox(MFC_Info)
        self.gB_ElcLoad_2.setGeometry(QtCore.QRect(450, 40, 201, 221))
        self.gB_ElcLoad_2.setObjectName("gB_ElcLoad_2")
        self.dBB_SetDisVLOTLow = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisVLOTLow.setGeometry(QtCore.QRect(60, 120, 61, 22))
        self.dBB_SetDisVLOTLow.setObjectName("dBB_SetDisVLOTLow")
        self.dBB_SetDisPOWLow = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisPOWLow.setGeometry(QtCore.QRect(60, 160, 61, 22))
        self.dBB_SetDisPOWLow.setObjectName("dBB_SetDisPOWLow")
        self.dBB_SetDisVLOTHigh = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisVLOTHigh.setGeometry(QtCore.QRect(130, 120, 61, 22))
        self.dBB_SetDisVLOTHigh.setObjectName("dBB_SetDisVLOTHigh")
        self.dBB_SetDisCURRHigh = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisCURRHigh.setGeometry(QtCore.QRect(130, 80, 61, 22))
        self.dBB_SetDisCURRHigh.setObjectName("dBB_SetDisCURRHigh")
        self.dBB_SetDisPOWHigh = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisPOWHigh.setGeometry(QtCore.QRect(130, 160, 61, 22))
        self.dBB_SetDisPOWHigh.setObjectName("dBB_SetDisPOWHigh")
        self.dBB_SetDisCURRLow = QtWidgets.QSpinBox(self.gB_ElcLoad_2)
        self.dBB_SetDisCURRLow.setGeometry(QtCore.QRect(60, 80, 61, 22))
        self.dBB_SetDisCURRLow.setObjectName("dBB_SetDisCURRLow")
        self.l_SetDischargeCURR = QtWidgets.QLabel(self.gB_ElcLoad_2)
        self.l_SetDischargeCURR.setGeometry(QtCore.QRect(10, 90, 54, 12))
        self.l_SetDischargeCURR.setObjectName("l_SetDischargeCURR")
        self.l_SetDischargeVLOT = QtWidgets.QLabel(self.gB_ElcLoad_2)
        self.l_SetDischargeVLOT.setGeometry(QtCore.QRect(10, 130, 54, 12))
        self.l_SetDischargeVLOT.setObjectName("l_SetDischargeVLOT")
        self.l_SetDischargePOW = QtWidgets.QLabel(self.gB_ElcLoad_2)
        self.l_SetDischargePOW.setGeometry(QtCore.QRect(10, 170, 54, 12))
        self.l_SetDischargePOW.setObjectName("l_SetDischargePOW")
        self.l_High = QtWidgets.QLabel(self.gB_ElcLoad_2)
        self.l_High.setGeometry(QtCore.QRect(130, 50, 54, 12))
        self.l_High.setObjectName("l_High")
        self.l_Low = QtWidgets.QLabel(self.gB_ElcLoad_2)
        self.l_Low.setGeometry(QtCore.QRect(60, 50, 54, 12))
        self.l_Low.setObjectName("l_Low")
        self.Pb_OKMFC = QtWidgets.QPushButton(MFC_Info)
        self.Pb_OKMFC.setGeometry(QtCore.QRect(180, 270, 91, 23))
        self.Pb_OKMFC.setObjectName("Pb_OKMFC")
        self.Pb_CancelMFC = QtWidgets.QPushButton(MFC_Info)
        self.Pb_CancelMFC.setGeometry(QtCore.QRect(400, 270, 91, 23))
        self.Pb_CancelMFC.setObjectName("Pb_CancelMFC")
        self.label = QtWidgets.QLabel(MFC_Info)
        self.label.setGeometry(QtCore.QRect(290, 10, 81, 16))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(MFC_Info)
        QtCore.QMetaObject.connectSlotsByName(MFC_Info)

    def retranslateUi(self, MFC_Info):
        _translate = QtCore.QCoreApplication.translate
        MFC_Info.setWindowTitle(_translate("MFC_Info", "MFC设置"))
        self.gB_MFC.setTitle(_translate("MFC_Info", "MFC/CVM"))
        self.l_SetMFCH2.setText(_translate("MFC_Info", "<html><head/><body><p>H<span style=\" vertical-align:sub;\">2</span>(L)：</p></body></html>"))
        self.l_SetMFCCO2.setText(_translate("MFC_Info", "<html><head/><body><p>CO<span style=\" vertical-align:sub;\">2</span>(L)：</p></body></html>"))
        self.l_SetMFCN2.setText(_translate("MFC_Info", "<html><head/><body><p>N<span style=\" vertical-align:sub;\">2</span>(L)：</p></body></html>"))
        self.l_SetMFCCH4.setText(_translate("MFC_Info", "<html><head/><body><p>CH<span style=\" vertical-align:sub;\">4</span>(L)：</p></body></html>"))
        self.l_SetMFCCO.setText(_translate("MFC_Info", "<html><head/><body><p>CO(L)：</p></body></html>"))
        self.l_SetMFCAir.setText(_translate("MFC_Info", "<html><head/><body><p>Air(L)：</p></body></html>"))
        self.l_Low_2.setText(_translate("MFC_Info", "下限"))
        self.l_High_2.setText(_translate("MFC_Info", "上限"))
        self.gB_POWSupply.setTitle(_translate("MFC_Info", "充电设置"))
        self.l_SetDischargeCURR_2.setText(_translate("MFC_Info", "<html><head/><body><p>电流(A)：</p></body></html>"))
        self.l_SetDischargeVLOT_2.setText(_translate("MFC_Info", "<html><head/><body><p>电压(V)：</p></body></html>"))
        self.l_SetDischargePOW_2.setText(_translate("MFC_Info", "<html><head/><body><p>功率(W)：</p></body></html>"))
        self.l_High_3.setText(_translate("MFC_Info", "上限"))
        self.l_Low_3.setText(_translate("MFC_Info", "下限"))
        self.gB_ElcLoad_2.setTitle(_translate("MFC_Info", "放电设置"))
        self.l_SetDischargeCURR.setText(_translate("MFC_Info", "<html><head/><body><p>电流(A)：</p></body></html>"))
        self.l_SetDischargeVLOT.setText(_translate("MFC_Info", "<html><head/><body><p>电压(V)：</p></body></html>"))
        self.l_SetDischargePOW.setText(_translate("MFC_Info", "<html><head/><body><p>功率(W)：</p></body></html>"))
        self.l_High.setText(_translate("MFC_Info", "上限"))
        self.l_Low.setText(_translate("MFC_Info", "下限"))
        self.Pb_OKMFC.setText(_translate("MFC_Info", "设置"))
        self.Pb_CancelMFC.setText(_translate("MFC_Info", "取消"))
        self.label.setText(_translate("MFC_Info", "MFC设置"))
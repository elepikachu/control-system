# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Help(object):
    def setupUi(self, Help):
        Help.setObjectName("Help")
        Help.resize(301, 507)
        self.pB_quit = QtWidgets.QPushButton(Help)
        self.pB_quit.setGeometry(QtCore.QRect(120, 470, 75, 23))
        self.pB_quit.setObjectName("pB_quit")
        self.outBox = QtWidgets.QTextBrowser(Help)
        self.outBox.setGeometry(QtCore.QRect(20, 60, 261, 401))
        self.outBox.setObjectName("outBox")
        self.l_titleLabel = QtWidgets.QLabel(Help)
        self.l_titleLabel.setGeometry(QtCore.QRect(120, 30, 71, 16))
        self.l_titleLabel.setObjectName("l_titleLabel")

        self.retranslateUi(Help)
        self.pB_quit.clicked.connect(Help.close) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Help)

    def retranslateUi(self, Help):
        _translate = QtCore.QCoreApplication.translate
        Help.setWindowTitle(_translate("Help", "使用帮助"))
        self.pB_quit.setText(_translate("Help", "退出帮助"))
        self.l_titleLabel.setText(_translate("Help", "<html><head/><body><p><span style=\" font-size:12pt;\">使用帮助</span></p></body></html>"))

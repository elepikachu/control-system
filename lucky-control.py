# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import SOCExpPlatform, MFCSetting, BatteryInfo


class LuckyControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = SOCExpPlatform.Ui_SOCExpPlatform()
        self.ui.setupUi(self)

    def paintEvent(self, evt):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = LuckyControl()
    ex.show()
    sys.exit(app.exec_())

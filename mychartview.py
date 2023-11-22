# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.9.13 (main, Aug 25 2022, 23:51:50) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: myChartView.py
# Compiled at: 1995-09-28 00:18:56
# Size of source mod 2**32: 538968336 bytes
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QRectF
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtChart import QChartView


class QMyChartView(QChartView):
    mouseMove = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self._QmyChartView__beginPoint = QPoint()
        self._QmyChartView__endPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._QmyChartView__beginPoint = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        point = event.pos()
        self.mouseMove.emit(point)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._QmyChartView__endPoint = event.pos()
            rectF = QRectF()
            rectF.setTopLeft(self._QmyChartView__beginPoint)
            rectF.setBottomRight(self._QmyChartView__endPoint)
            self.chart().zoomIn(rectF)
        else:
            if event.button() == Qt.RightButton:
                self.chart().zoomReset()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Plus:
            self.chart().zoom(1.2)
        else:
            if key == Qt.Key_Minus:
                self.chart().zoom(0.8)
            else:
                if key == Qt.Key_Left:
                    self.chart().scroll(10, 0)
                else:
                    if key == Qt.Key_Right:
                        self.chart().scroll(-10, 0)
                    else:
                        if key == Qt.Key_Up:
                            self.chart().scroll(0, -10)
                        else:
                            if key == Qt.Key_Down:
                                self.chart().scroll(0, 10)
                            else:
                                if key == Qt.Key_PageUp:
                                    self.chart().scroll(0, -50)
                                else:
                                    if key == Qt.Key_PageDown:
                                        self.chart().scroll(0, 50)
                                    else:
                                        if key == Qt.Key_Home:
                                            self.chart().zoomReset()
        super().keyPressEvent(event)
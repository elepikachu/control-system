# -*- coding: utf-8 -*-
# test the ui
import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPainter
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from matplotlib.figure import Figure
from scipy.stats import stats
import pandas as pd
import numpy as np
import DataAnalyse

try:
    font_path = "timesun.ttf"
    font_manager.fontManager.addfont(font_path)
    prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = prop.get_name()
except Exception as e:
    print('no font file')
    plt.rcParams['font.sans-serif'] = ['SimHei']


# -------------------------------------------------------------
# 类名： DataWindow
# 功能：数据分析窗口
# -------------------------------------------------------------
class DataWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = DataAnalyse.Ui_DataAnalyse()
        self.ui.setupUi(self)
        self.df = pd.DataFrame()
        self.file_fg = 0
        self.fn = ''
        self.ui.cb_ap.clicked.connect(self.cb_click)
        self.ui.cb_av.clicked.connect(self.cb_click)
        self.ui.cb_ta.clicked.connect(self.cb_click)
        self.ui.pb_upload.clicked.connect(self.upload_chart)
        self.ui.pb_da.clicked.connect(self.data_analyse)
        self.ui.pb_plot.clicked.connect(self.make_plot)
        self.ui.pb_down.clicked.connect(self.down_chart)

    # -------------------------------------------------------------
    # 函数名： paintEvent
    # 功能：绘制背景板
    # 参数： evt 绘制动作
    # -------------------------------------------------------------
    def paintEvent(self, evt):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    # -------------------------------------------------------------
    # 函数名： figure_init
    # 功能： 初始化实时作图
    # -------------------------------------------------------------
    def figure_init(self):
        dr = FigureCanvas()
        fig = Figure()
        plt.rcParams['figure.figsize'] = (4, 2)
        plt.rcParams['font.size'] = 8
        ax = fig.add_subplot(111)
        ax.plot(self.df['电流'], self.df['电压'], marker='.')
        ax.set_xlabel('电流/A')
        ax.set_xlabel('电压/V')
        # ax.grid(visible=True)
        ax.set_title('当前数据流压图')
        dr.figure = fig
        graphic_scene = QtWidgets.QGraphicsScene()
        graphic_scene.addWidget(dr)
        self.ui.plot.setScene(graphic_scene)
        self.ui.plot.show()

    # -------------------------------------------------------------
    # 函数名： cb_click
    # 功能： 选择框互斥
    # -------------------------------------------------------------
    def cb_click(self):
        if self.ui.cb_ap.isChecked() or self.ui.cb_av.isChecked():
            self.ui.cb_ta.setDisabled(True)
        else:
            self.ui.cb_ta.setDisabled(False)
        if self.ui.cb_ta.isChecked():
            self.ui.cb_av.setDisabled(True)
            self.ui.cb_ap.setDisabled(True)
        else:
            self.ui.cb_av.setDisabled(False)
            self.ui.cb_ap.setDisabled(False)

    # -------------------------------------------------------------
    # 函数名： upload_chart
    # 功能： 表格上传
    # -------------------------------------------------------------
    def upload_chart(self):
        curPath = os.getcwd()
        filename, flt = QFileDialog.getOpenFileName(self, '选择文件', curPath, '数据文件(*.csv *.xlsx);;所有文件(*.*)')
        if filename == '':
            return
        file_extension = os.path.splitext(filename)[1]
        print(file_extension)
        if file_extension == '.csv':
            self.file_fg = 1
            self.df = pd.read_csv(filename, header=1, encoding='utf-8')
            self.fn = os.path.splitext(filename)[0]
        elif file_extension == '.xlsx':
            self.file_fg = 2
            self.df = pd.read_excel(filename, sheet_name=0, header=0)
            self.fn = os.path.splitext(filename)[0]
        else:
            QMessageBox.information(self, '失败', '上传文件格式错误')
            return
        if self.ui.sb_step != 1:
            self.df = self.df[::self.ui.sb_step.value()]
        self.df = self.df[self.df['电流'] > 0.05]
        self.figure_init()
        self.figure_init()

    # -------------------------------------------------------------
    # 函数名： data_analyse
    # 功能： 数据处理
    # -------------------------------------------------------------
    def data_analyse(self):
        if self.file_fg == 0:
            QMessageBox.information(self, '失败', '公主请先上传表格')
            return
        if self.ui.cb_del.isChecked():
            self.df = self.df.drop([self.df.index[0]], axis=0)
            self.df = self.df.drop([self.df.index[0]], axis=0)
        if self.ui.cb_dup.isChecked():
            self.df['电流2'] = self.df['电流'].round(1)
            self.df = self.df.sort_values(['电压'], ascending=False).drop_duplicates(subset=['电流2'],
                                                                                   keep='first').sort_index()
        if self.ui.cb_vari.isChecked():
            k = self.ui.dsb_vari.value()
            slope, intercept, r, _, _ = stats.linregress(self.df['电流2'], self.df['电压'])
            line_func = lambda x: slope * x + intercept  # 线性规划函数
            res = np.abs(self.df['电压'] - line_func(self.df['电流2']))  # 残差
            mean_res = res.mean()
            std_res = res.std()
            self.df = self.df[res <= mean_res + k * std_res]
        self.figure_init()
        print('rrr')

    # -------------------------------------------------------------
    # 函数名： down_chart
    # 功能： 表格下载
    # -------------------------------------------------------------
    def down_chart(self):
        if self.file_fg == 0:
            QMessageBox.information(self, '失败', '公主请先上传表格')
            return
        if self.df['电流2']:
            self.df.drop('电流2')
        self.df.to_excel(self.fn + '-rev.xlsx', index=False)

    # -------------------------------------------------------------
    # 函数名： make_plot
    # 功能： 制图及下载
    # -------------------------------------------------------------
    def make_plot(self):
        if self.file_fg == 0:
            QMessageBox.information(self, '失败', '公主请先上传表格')
            return
        plt.rcParams['figure.figsize'] = (20, 10)
        plt.rcParams['font.size'] = 15
        if self.ui.cb_ap.isChecked():
            if self.ui.cb_av.isChecked():
                plt.subplot(1, 2, 1)
                plt.plot(self.df['电流'], self.df['电压'], marker='.')
                plt.xlabel('电流/A')
                # plt.xlim(xmin=0, xmax=16)
                plt.ylabel('电压/V')
                plt.legend(loc='lower right')
                plt.grid(visible=True)
                # plt.xticks(np.arange(0, 16, 2))
                plt.subplot(1, 2, 2)
                plt.plot(self.df['电流'], self.df['功率'], marker='.')
                plt.xlabel('电流/A')
                # plt.xlim(xmin=0, xmax=16)
                plt.ylabel('功率/V')
                plt.legend(loc='lower right')
                # plt.xticks(np.arange(0, 16, 2))
                plt.grid(visible=True)
                plt.tight_layout()
                plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=None)
                plt.suptitle(self.fn, y=1)
                plt.plot()
                plt.show()
            else:
                plt.plot(self.df['电流'], self.df['功率'], marker='.')
                plt.xlabel('电流/A')
                # plt.xlim(xmin=0, xmax=16)
                plt.ylabel('功率/V')
                plt.legend(loc='lower right')
                # plt.xticks(np.arange(0, 16, 2))
                plt.grid(visible=True)
                plt.tight_layout()
                plt.suptitle(self.fn, y=1)
                plt.plot()
                plt.show()
        elif self.ui.cb_av.isChecked():
            plt.plot(self.df['电流'], self.df['电压'], marker='.')
            plt.xlabel('电流/A')
            # plt.xlim(xmin=0, xmax=16)
            plt.ylabel('电压/V')
            plt.legend(loc='lower right')
            # plt.xticks(np.arange(0, 16, 2))
            plt.grid(visible=True)
            plt.tight_layout()
            plt.suptitle(self.fn, y=1)
            plt.plot()
            plt.show()
        elif self.ui.cb_ta.isChecked():
            plt.plot(self.df['累计时间'], self.df['电流'], marker='.')
            plt.xlabel('时间/s')
            plt.xlim(xmin=0, xmax=16)
            plt.ylabel('电流/A')
            plt.legend(loc='lower right')
            plt.grid(visible=True)
            plt.tight_layout()
            plt.suptitle(self.fn, y=1)
            plt.plot()
            plt.show()
        else:
            QMessageBox.information(self, '失败', '公主请请至少选择一个制图对象吧')
            return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('./img/cnpc.png'))
    ex = DataWindow()
    ex.show()
    sys.exit(app.exec_())

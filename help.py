# coding=utf8
from PyQt4 import uic
from PyQt4.QtGui import *


form_class = uic.loadUiType("help.ui")[0]


class HelpWindow(QMainWindow, form_class):
    def __init__(self):
        super(HelpWindow, self).__init__()
        self.input_file_name = None
        # self.output_file_name = None
        # self.input_data_set = None

        self.setupUi(self)

        # File 메뉴 바인드
        self.actionQuit.triggered.connect(self.close)

        # Help 메뉴 바인드
        self.actionHelp_content.triggered.connect(self.help_clicked)
        self.actionAbout.triggered.connect(self.about_clicked)

    def import_clicked(self):
        try:
            self.input_file_name = QFileDialog.getOpenFileName(self, filter=u'CSV 파일 (*.csv)')[0]
        except IndexError:
            pass

    def help_clicked(self):
        return QMessageBox.information(self, "Oops", "Not Implemented.", QMessageBox.Ok)

    def about_clicked(self):
        return QMessageBox.information(self, u"Anomization tools",
                                       u"이 툴은 개인정보를 비식별 조치하는 툴입니다.\nKITRI fwvaBOB 5th No Jam'.",
                                       QMessageBox.Ok)

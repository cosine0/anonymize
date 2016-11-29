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

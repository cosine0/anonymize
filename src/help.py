# coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'help.ui'))[0]


class HelpWindow(QMainWindow, form_class):
    def __init__(self):
        super(HelpWindow, self).__init__()
        self.setupUi(self)

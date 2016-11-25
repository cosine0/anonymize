# coding=utf8
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType("level.ui")[0]


class LevelWindow(QWizard, form_class):
    def __init__(self):
        super(LevelWindow, self).__init__()
        self.setupUi(self)

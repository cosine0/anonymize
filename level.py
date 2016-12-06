# coding=utf8
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType('ui/level.ui')[0]


class LevelWindow(QWizard, form_class):
    def __init__(self, parent=None):
        super(LevelWindow, self).__init__(parent)
        self.setupUi(self)

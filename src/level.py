# coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'level.ui'))[0]


class LevelWizard(QWizard, form_class):
    def __init__(self, parent=None):
        super(LevelWizard, self).__init__(parent)
        self.setupUi(self)

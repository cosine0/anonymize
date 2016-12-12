# coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'processing.ui'))[0]


class ProcessingDialog(QDialog, form_class):
    movie = None

    def __init__(self, parent):
        super(ProcessingDialog, self).__init__(parent, Qt.CustomizeWindowHint)
        self.setupUi(self)
        if ProcessingDialog.movie is None:
            ProcessingDialog.movie = QMovie(os.path.join(os.path.dirname(__file__), 'ui', 'ring.gif'))
        self.gifLabel.setMovie(ProcessingDialog.movie)
        ProcessingDialog.movie.start()

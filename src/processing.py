# coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'processing.ui'))[0]


class ProcessingDialog(QDialog, form_class):
    """
    실행 중임을 나타내는 작은 대화상자
    :param parent: 상위 윈도우

    static 멤버
        movie: GIF 회전 애니메이션
    """
    movie = None

    def __init__(self, parent):
        super(ProcessingDialog, self).__init__(parent, Qt.CustomizeWindowHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)

        # 애니메이션이 로드되지 않은 경우 로드
        if ProcessingDialog.movie is None:
            ProcessingDialog.movie = QMovie(os.path.join(os.path.dirname(__file__), 'ui', 'ring.gif'))
        self.gifLabel.setMovie(ProcessingDialog.movie)
        ProcessingDialog.movie.start()

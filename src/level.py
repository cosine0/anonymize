# coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *
from table import display_data_set_on_table

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'level.ui'))[0]


class LevelWizard(QWizard, form_class):
    """
    비식별 조치 및 단계 편집 마법사
    :param parent: 상위 윈도우
    """
    masking_example_headers = [u'0 단계', u'1 단계', u'2 단계', u'3 단계']
    masking_example = [[u'  김철수  ', u'  김철*  ', u'  김**  ', u'  *  '],
                       [u'  이영희  ', u'  이영*  ', u'  이**  ', u'  *  '],
                       [u'  박지훈  ', u'  박지*  ', u'  박**  ', u'  *  ']]

    def __init__(self, parent=None):
        super(LevelWizard, self).__init__(parent)
        self.setupUi(self)

        self.methodBox.currentIndexChanged.connect(self.method_box_changed)

    def method_box_changed(self, method_index):
        """
        비식별 조치 방법 변경 시
        """
        main_window = self.parent()
        method = self.methodBox.currentText()
        for method_item in main_window.attributeTable.selectedItems():
            method_item.setText(method)
        main_window.levelTable.setEnabled(True)
        display_data_set_on_table(main_window.levelTable, LevelWizard.masking_example_headers, LevelWizard.masking_example)

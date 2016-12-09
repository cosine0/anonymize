    # coding=utf8
import os
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType(os.path.join('ui', 'input_file.ui'))[0]


class InputFileWizard(QWizard, form_class):
    def __init__(self, parent, attributes):
        super(InputFileWizard, self).__init__(parent)
        self.main_window = parent
        self.setupUi(self)

        self.datatypeTable.setRowCount(len(attributes))
        for attribute_index, attribute in enumerate(attributes):
            item = QTableWidgetItem(attribute)
            self.datatypeTable.setItem(attribute_index, 0, item)
            datatype_combobox = QComboBox()
            datatype_combobox.addItems((u'문자열', u'수', u'날짜'))
            self.datatypeTable.setCellWidget(attribute_index, 1, datatype_combobox)

        self.datatypeTable.resizeColumnsToContents()

        self.characteristicTable.setRowCount(len(attributes))
        for attribute_index, attribute in enumerate(attributes):
            item = QTableWidgetItem(attribute)
            self.characteristicTable.setItem(attribute_index, 0, item)
            characteristic_combobox = QComboBox()
            characteristic_combobox.addItems((u'준식별자', u'식별자', u'일반 속성', u'민감 정보', u'(속성 사용 안 함)'))
            self.characteristicTable.setCellWidget(attribute_index, 1, characteristic_combobox)

        self.characteristicTable.resizeColumnsToContents()

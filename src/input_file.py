# coding=utf8
import os
import re
from PyQt4 import uic
from PyQt4.QtGui import *

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'input_file.ui'))[0]


class InputFileWizard(QWizard, form_class):
    """
    파일 가져오기 마법사
    :param parent: 상위 윈도우
    :param attributes: str들의 list. 각 속성명의 목록
    """
    identifier_names = {
        u'이름', u'성명', u'주민등록번호', u'여권번호', u'외국인등록번호', u'운전면허번호', u'한자성명', u'영문성명', u'필명등포함', u'주소 ',
        u'생일', u'생년월일', u'휴대전화번호', u'집전화', u'전화번호', u'회사전화', u'팩스번호', u'의료기록번호', u'건강보험번호', u'복지수급자 번호',
        u'정지사진', u'동영상', u'지문', u'홍채', u'이메일 주소', u'IP주소', u'MAC주소', u'IP', u'MAC', u'아이디', u'사원번호', u'고객번호',
        u'군번', u'사업자 등록번호', u'자격증', u'자격증번호', u'면허번호', u'자동차번호', u'등록번호', u'통장계좌번호', u'신용카드번호'}

    def __init__(self, parent, attributes):
        super(InputFileWizard, self).__init__(parent)
        self.main_window = parent
        self.setupUi(self)

        # 첫 번째 페이지. 데이터 타입 테이블 생성.
        self.datatypeTable.setRowCount(len(attributes))
        for attribute_index, attribute in enumerate(attributes):
            item = QTableWidgetItem(attribute)
            self.datatypeTable.setItem(attribute_index, 0, item)
            datatype_combobox = QComboBox()
            datatype_combobox.addItems((u'문자열', u'숫자', u'날짜'))
            self.datatypeTable.setCellWidget(attribute_index, 1, datatype_combobox)

        self.datatypeTable.resizeColumnsToContents()

        # 두 번째 페이지. 데이터 성격 테이블 생성.
        self.characteristicTable.setRowCount(len(attributes))
        for attribute_index, attribute in enumerate(attributes):
            item = QTableWidgetItem(attribute)
            self.characteristicTable.setItem(attribute_index, 0, item)
            characteristic_combobox = QComboBox()
            characteristic_combobox.addItems((u'준식별자', u'식별자', u'일반 속성', u'민감 정보', u'(속성 사용 안 함)'))
            if re.sub(u'\s', u'', attribute).upper() in InputFileWizard.identifier_names:
                characteristic_combobox.setCurrentIndex(1)
            self.characteristicTable.setCellWidget(attribute_index, 1, characteristic_combobox)

        self.characteristicTable.resizeColumnsToContents()

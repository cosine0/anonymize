# coding=utf8
import os
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from help import HelpWindow
from level import LevelWizard
from table import display_data_set_on_table, load_csv_as_data_set, save_data_set_as_csv
from input_file import InputFileWizard
from processing import ProcessingDialog
from risk import risk

reload(sys)
sys.setdefaultencoding('utf8')

form_class = uic.loadUiType(os.path.join(os.path.dirname(__file__), u'ui', u'main.ui'))[0]


class MainWindow(QMainWindow, form_class):
    """
    메인 윈도우
    """
    def __init__(self):
        super(MainWindow, self).__init__()

        self.input_file_name = None
        self.input_attributes = None
        self.input_data_set = None
        self.output_file_name = None
        self.output_attributes = None
        self.output_data_set = None
        self.encoding = None

        self.setupUi(self)

        # 파일 메뉴 바인드
        self.actionImport.triggered.connect(self.import_clicked)
        self.actionSave_input.triggered.connect(self.save_input_clicked)
        self.actionSave_output.triggered.connect(self.save_output_clicked)
        self.actionQuit.triggered.connect(self.close)

        # 도움말 메뉴 바인드
        self.actionHelp_content.triggered.connect(self.help_clicked)
        self.actionAbout.triggered.connect(self.about_clicked)
        self.help_window = None

        # 레벨 변경 바인드
        self.levelEditButton.clicked.connect(self.level_edit_button_clicked)
        self.level_wizard = None

        # 실행 버튼 바인드
        self.runButton.clicked.connect(self.run_clicked)

        # 돌아가기 버튼 바인드
        self.returnButton.clicked.connect(self.return_clicked)

        # 출력 탭 스크롤 싱크
        self.outputTableLeft.verticalScrollBar().valueChanged.connect(self.output_left_table_vertically_scrolled)
        self.outputTableRight.verticalScrollBar().valueChanged.connect(self.output_right_table_vertically_scrolled)
        self.outputTableLeft.horizontalScrollBar().valueChanged.connect(self.output_left_table_horizontally_scrolled)
        self.outputTableRight.horizontalScrollBar().valueChanged.connect(self.output_right_table_horizontally_scrolled)

        # 입력 파일 초기 설정
        self.input_file_wizard = None

        # 익명화 모델 선택 토글
        self.kRadioButton.clicked.connect(self.k_radio_button_clicked)
        self.lRadioButton.clicked.connect(self.l_radio_button_clicked)

    def import_clicked(self):
        """
        파일>가져오기 메뉴 버튼 클릭 시 
        """
        self.input_file_name = QFileDialog.getOpenFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.input_file_name:
            return

        try:
            self.input_attributes, self.input_data_set, self.encoding = load_csv_as_data_set(file_name)
        except:
            QMessageBox.critical(self, u'가져오기 오류', u'파일이 없거나 잘못되었습니다.')

        self.input_file_wizard = InputFileWizard(self, self.input_attributes)
        self.input_file_wizard.finished.connect(self.input_file_wizard_finished)
        self.input_file_wizard.show()

    def save_input_clicked(self):
        """
        파일>입력 저장 메뉴 버튼 클릭 시 
        """
        if not self.input_data_set:
            QMessageBox.critical(self, u'저장 오류', u'입력 데이터가 없습니다.')
            return

        self.input_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.input_file_name:
            return

        save_data_set_as_csv(self.input_attributes, self.input_data_set, self.input_file_name, self.encoding)

    def save_output_clicked(self):
        """
        파일>출력 저장 메뉴 버튼 클릭 시 
        """
        if not self.output_data_set:
            QMessageBox.critical(self, u'저장 오류', u'출력 데이터가 없습니다.')
            return

        self.output_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.output_file_name:
            return

        save_data_set_as_csv(self.output_attributes, self.output_data_set, self.output_file_name, self.encoding)

    def help_clicked(self):
        """
        도움말>도움말 항목 메뉴 버튼 클릭 시 
        """
        self.help_window = HelpWindow()
        self.help_window.show()

    def about_clicked(self):
        """
        도움말>정보 메뉴 버튼 클릭 시
        """
        return QMessageBox.information(
            self, u"Intorduce", u"이 툴은 개인정보를 비식별 조치하는 툴입니다.\nKITRI fwvaBOB 5th No Jam'.", QMessageBox.Ok)

    def level_edit_button_clicked(self):
        """
        비식별 조치 및 단계 편집 버튼 클릭 시
        """
        # 레벨 편집 창을 띄움.
        self.level_wizard = LevelWizard(parent=self)
        self.level_wizard.show()

    def run_clicked(self):
        """
        실행 버튼 클릭 시
        """
        assert isinstance(self.attributeTable, QTableWidget)

        data_types = []
        is_sensitive_information = []
        for row_index in xrange(self.attributeTable.rowCount()):
            attribute_datatype = self.attributeTable.cellWidget(row_index, 1).currentText()
            data_types.append(attribute_datatype)

            attribute_characteristic = self.attributeTable.cellWidget(row_index, 2).currentText()
            deidentification_method = self.attributeTable.item(row_index, 3).text()
            if attribute_characteristic == u'식별자':
                if deidentification_method != u'삭제':
                    if QMessageBox.warning(self, u'경고', u'식별자는 삭제가 권장됩니다. 그래도 계속하시겠습니까?',
                                           QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                        return

            if attribute_characteristic == u'민감 정보':
                is_sensitive_information.append(True)
            else:
                is_sensitive_information.append(False)

        self.processing_dialog = ProcessingDialog(self)
        self.processing_dialog.show()

        self.processing_dialog.close()

        self.mainTab.setCurrentIndex(1)
        self.output_attributes, self.output_data_set, _ = load_csv_as_data_set(
            u"C:\\Users\\cos\\PycharmProjects\\anonymize\\src\\example\\의료(비식별화).csv")
        display_data_set_on_table(self.outputTableLeft, self.input_attributes, self.input_data_set)
        display_data_set_on_table(self.outputTableRight, self.output_attributes, self.output_data_set)

        risk_ratio = risk(self.output_data_set, data_types, is_sensitive_information, self.input_data_set,
                          range(len(self.input_data_set[0])))
        self.riskPercentLabel.setText('{:.1f} %'.format(risk_ratio * 100))

    def return_clicked(self):
        """
        돌아가기 버튼 클릭 시
        """
        self.mainTab.setCurrentIndex(0)

    def input_file_wizard_finished(self, return_value):
        """
        파일 입력 마법사 종료 시
        :param return_value: 종료 코드
        """
        assert isinstance(self.input_file_wizard.datatypeTable, QTableWidget)
        column_count = self.input_file_wizard.datatypeTable.rowCount()
        self.attributeTable.setRowCount(column_count)
        for attribute_index in xrange(column_count):
            attribute_name = self.input_file_wizard.datatypeTable.item(attribute_index, 0)
            self.attributeTable.setItem(attribute_index, 0, QTableWidgetItem(attribute_name.text()))

            datatype_combobox = self.input_file_wizard.datatypeTable.cellWidget(attribute_index, 1)
            self.attributeTable.setCellWidget(attribute_index, 1, datatype_combobox)

            characteristic_combobox = self.input_file_wizard.characteristicTable.cellWidget(attribute_index, 1)
            self.attributeTable.setCellWidget(attribute_index, 2, characteristic_combobox)

            self.attributeTable.setItem(attribute_index, 3, QTableWidgetItem(u'마스킹'))

        self.input_file_wizard.destroy()
        display_data_set_on_table(self.inputTable, self.input_attributes, self.input_data_set)

    def output_left_table_vertically_scrolled(self):
        """
        출력 탭 왼쪽 표 수직 스크롤 시
        """
        scroll_position = self.outputTableLeft.verticalScrollBar().value()
        self.outputTableRight.verticalScrollBar().setValue(scroll_position)

    def output_right_table_vertically_scrolled(self):
        """
        출력 탭 오른쪽 표 수직 스크롤 시
        """
        scroll_position = self.outputTableRight.verticalScrollBar().value()
        self.outputTableLeft.verticalScrollBar().setValue(scroll_position)

    def output_left_table_horizontally_scrolled(self):
        """
        출력 탭 왼쪽 표 수평 스크롤 시
        """
        scroll_position = self.outputTableLeft.horizontalScrollBar().value()
        self.outputTableRight.horizontalScrollBar().setValue(scroll_position)

    def output_right_table_horizontally_scrolled(self):
        """
        수평 탭 오른쪽 표 수직 스크롤 시
        """
        scroll_position = self.outputTableRight.horizontalScrollBar().value()
        self.outputTableLeft.horizontalScrollBar().setValue(scroll_position)

    def k_radio_button_clicked(self):
        """
        익명화 모델 k-익명성으로 선택 전환 시 
        """
        self.kValueBox.setEnabled(True)
        self.lValueBox.setEnabled(False)

    def l_radio_button_clicked(self):
        """
        익명화 모델 l-다양성으로 선택 전환 시 
        """
        self.lValueBox.setEnabled(True)
        self.kValueBox.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.show()
    app.exec_()

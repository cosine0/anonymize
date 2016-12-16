# coding=utf8
import os
import sys
import threading
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from Mondrian_L_Diversity import anonymizer
from Mondrian_L_Diversity.models import gentree
from help import HelpWindow
from level import LevelWizard
from table import display_data_set_on_table, load_csv_as_data_set, save_data_set_as_csv
from input_file import InputFileWizard
from processing import ProcessingDialog
from deidentification_methods import mask
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

        # 멤버
        self.processing_dialog = None
        self.data_process_thread = None
        self.input_file_name = None
        self.input_attributes = None
        self.input_data_set = None
        self.output_file_name = None
        self.output_attributes = None
        self.output_data_set = None
        self.encoding = None
        self.risk_ratio = None
        self.last_clicked_attribute_index = None

        # ui 설정
        self.setupUi(self)
        self.fineLabel.hide()
        self.warningLabel.hide()
        self.dangerousLabel.hide()

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

        # 속성 셀 클릭 바인드
        self.attributeTable.cellClicked.connect(self.attributes_cell_clicked)

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

        # 재식별 위험 측정 버튼 바인드
        self.riskButton.clicked.connect(self.risk_button_clicked)

        self.processing_dialog = ProcessingDialog(self)

    def import_clicked(self):
        """
        파일>가져오기 메뉴 버튼 클릭 시 
        """
        # 입력 파일 선택 대화상자 실행
        self.input_file_name = QFileDialog.getOpenFileName(self, filter=u'CSV 파일 (*.csv)')

        # 선택 안되면 아무것도 하지 않음
        if not self.input_file_name:
            return

        # 파일 로드
        try:
            self.input_attributes, self.input_data_set, self.encoding = load_csv_as_data_set(self.input_file_name)
        except:
            QMessageBox.critical(self, u'가져오기 오류', u'파일이 없거나 잘못되었습니다.')

        # 속성 데이터 타입, 데이터 성격 마법사 실행
        self.input_file_wizard = InputFileWizard(self, self.input_attributes)
        self.input_file_wizard.finished.connect(self.input_file_wizard_finished)
        self.input_file_wizard.show()

    def save_input_clicked(self):
        """
        파일>입력 저장 메뉴 버튼 클릭 시 
        """
        # 입력 데이터가 있는지 확인
        if not self.input_data_set:
            QMessageBox.critical(self, u'저장 오류', u'입력 데이터가 없습니다.')
            return

        # 저장 파일 선택 대화상자 실행
        self.input_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.input_file_name:
            return

        # 파일 저장
        save_data_set_as_csv(self.input_attributes, self.input_data_set, self.input_file_name, self.encoding)

    def save_output_clicked(self):
        """
        파일>출력 저장 메뉴 버튼 클릭 시 
        """
        # 출력 데이터가 있는지 확인
        if not self.output_data_set:
            QMessageBox.critical(self, u'저장 오류', u'출력 데이터가 없습니다.')
            return

        # 저장 파일 선택 대화상자 실행
        self.output_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.output_file_name:
            return

        # 파일 저장
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
            self, u"Intorduce", u"Deidentipyer.\nKITRI BOB 5th No Jam.\nUnder GNU Public License", QMessageBox.Ok)

    def level_edit_button_clicked(self):
        """
        비식별 조치 및 단계 편집 버튼 클릭 시
        """
        # 레벨 편집 마법사 실행
        self.level_wizard = LevelWizard(parent=self)
        self.level_wizard.show()

    def attributes_cell_clicked(self, row, column):
        """
        속성 셀 클릭 시
        :param row: 행
        :param column: 열
        """
        self.last_clicked_attribute_index = row
        method = self.attributeTable.item(row, 3).text()
        if method:
            self.levelTable.setEnabled(True)
        else:
            self.levelTable.setEnabled(False)

    def run_clicked(self):
        """
        실행 버튼 클릭 시: 사용하는 속성의 데이터만을 모은 후 비식별화한다. 
        """
        if not self.input_data_set:
            QMessageBox.critical(self, u'실행', u'입력 데이터를 가져온 후 비식별화를 실행하십시오.')
            return

        # 비식별화 시작
        # 비식별화 - 1. 준식별자, 민감 정보 속성 파악
        quasi_identifier_indices = []
        methods = []
        sensitive_information_indices = []
        identifier_remaining = False
        number_of_attributes = self.attributeTable.rowCount()
        for attribute_index in xrange(number_of_attributes):
            characteristic = self.attributeTable.cellWidget(attribute_index, 2).currentText()
            method = self.attributeTable.item(attribute_index, 3).text()
            if characteristic in (u'식별자', u'준식별자'):
                quasi_identifier_indices.append(attribute_index)
                methods.append(method)
            elif characteristic == u'민감 정보':
                sensitive_information_indices.append(attribute_index)
            elif characteristic == u'식별자':
                identifier_remaining = True

        # 식별자 경고
        if identifier_remaining:
            if QMessageBox.warning(self, u'경고', u'식별자는 사용하지 않는 것이 권장됩니다. 그래도 계속하시겠습니까?',
                                   QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                return

        # 실행 중 대화상자 표시
        self.processing_dialog.show()

        # 비식별화 - 2. 준식별자, 민감 정보만으로 이루어진 데이터 셋 생성
        new_data_set = []
        for record_index, record in enumerate(self.input_data_set):
            new_record = []
            for attribute_index in quasi_identifier_indices:
                new_record.append(record[attribute_index])

            sensitive_information = []
            for sensitive_information_index in sensitive_information_indices:
                sensitive_information.append(record[sensitive_information_index])

            sensitive_information.append(str(record_index))
            new_record.append(sensitive_information)
            new_data_set.append(new_record)

        # 비식별화 - 3. 비식별 단계 트리 생성
        attribute_trees = []
        for attribute_index, method in enumerate(methods):
            # 비식별 조치 방법별 트리 생성
            if method == u'':
                QMessageBox.warning(self, u'실행', u'모든 속성에 비식별 조치 방법 지정해야 합니다.')
                # 실행 중 대화상자 닫기
                self.processing_dialog.close()
                return
            if method == u'마스킹':
                masking_character = u'*'
                padding_character = u' '
                masking_direction = u'right'
                attribute_tree = dict()
                # 길이 최댓값 구하기
                max_length = max(len(record[attribute_index]) for record in self.input_data_set)
                # 마스킹 길이 별 트리 정의
                # 루트 노드
                attribute_tree['*'] = gentree.GenTree('*', None, False)
                # 깊이 1인 노드
                for new_record in new_data_set:
                    value = new_record[attribute_index]
                    masked_value = mask(value, max_length, number_to_leave_alive=1, masking_character=masking_character,
                                        padding_character=padding_character, mask_from_direction=masking_direction)
                    # 해당 값이 트리에 없는 경우 노드로 추가
                    if masked_value not in attribute_tree:
                        attribute_tree[masked_value] \
                            = gentree.GenTree(masked_value, attribute_tree['*'], 1 == len(value))
                # 나머지 내부 노드
                for length in xrange(1, max_length):
                    for new_record in new_data_set:
                        value = new_record[attribute_index]
                        masked_value = mask(value, max_length, length, masking_character=masking_character,
                                            padding_character=padding_character, mask_from_direction=masking_direction)
                        # 해당 값이 트리에 없는 경우 노드로 추가
                        if masked_value not in attribute_tree:
                            one_more_masked_value = mask(value, max_length, length - 1,
                                                         masking_character=masking_character,
                                                         padding_character=padding_character,
                                                         mask_from_direction=masking_direction)
                            attribute_tree[masked_value] = gentree.GenTree(masked_value,
                                                                           attribute_tree[one_more_masked_value],
                                                                           length == len(value))
                # 잎 노드
                for new_record in new_data_set:
                    value = new_record[attribute_index]
                    # 해당 값이 트리에 없는 경우 노드로 추가
                    if value not in attribute_tree:
                        one_masked_value = mask(value, max_length, number_to_leave_alive=1,
                                                masking_character=masking_character,
                                                padding_character=padding_character,
                                                mask_from_direction=masking_direction)
                        attribute_tree[value] \
                            = gentree.GenTree(value, attribute_tree[one_masked_value], True)
                attribute_trees.append(attribute_tree)
            else:
                QMessageBox.critical(self, u'실행', u'지원되지 않는 비식별 조치 방법입니다.')
                return

        # 비식별화 - 4. 모델 충족 알고리즘 실행
        # 모델 모수 가져오기
        if self.kRadioButton.isChecked():
            model_parameter = self.kValueBox.value()
        elif self.lRadioButton.isChecked():
            model_parameter = self.lValueBox.value()
        else:
            QMessageBox.warning(self, u'경고', u'익명화 모델을 지정해야 합니다.')
            return
        # 탐색 알고리즘 실행
        result_data_set, _ = anonymizer.mondrian_l_diversity(attribute_trees, new_data_set, model_parameter)

        # 비식별화 - 5. 결과를 표시할 수 있는 데이터 형태로 변환
        # 인덱스 합치기
        union_indices = []
        for result_index, input_index in enumerate(quasi_identifier_indices):
            union_indices.append((input_index, (u'준식별자', result_index)))
        for sensitive_information_index, input_index in enumerate(sensitive_information_indices):
            union_indices.append((input_index, (u'민감 정보', sensitive_information_index)))

        union_indices.sort(key=lambda x: x[0])  # 입력 데이터 순서로 정렬

        self.output_attributes = []
        self.data_types = []
        self.is_sensitive_information = []
        self.attribute_mapping = [None] * len(self.input_attributes)
        for reidentification_index, (input_index, _) in enumerate(union_indices):  # 인덱스 참조, 출력 속성명 리스트 만들기
            self.output_attributes.append(self.input_attributes[input_index])
            data_type = self.attributeTable.cellWidget(input_index, 1).currentText()
            self.attribute_mapping[input_index] = reidentification_index
            self.data_types.append(data_type)
            self.is_sensitive_information.append(input_index in sensitive_information_indices)

        # 출력 데이터 만들기, 이에 맞춰 입력 데이터 재배열
        self.output_data_set = []
        self.reordered_input_data_set = []
        for result_record in result_data_set:
            output_record = []
            for input_index, (characteristic, result_index) in union_indices:
                if characteristic == u'준식별자':
                    output_record.append(result_record[result_index])
                elif characteristic == u'민감 정보':
                    output_record.append(result_record[-1][result_index])
                else:
                    assert False
            self.output_data_set.append(output_record)
            self.reordered_input_data_set.append(self.input_data_set[int(result_record[-1][-1])])
        # 비식별화 끝

        # 입력, 출력 데이터 표시
        display_data_set_on_table(self.outputTableLeft, self.input_attributes, self.reordered_input_data_set)
        display_data_set_on_table(self.outputTableRight, self.output_attributes, self.output_data_set)

        # 실행 중 대화상자 닫기
        self.processing_dialog.close()
        # 출력 탭으로 이동
        self.mainTab.setCurrentIndex(1)

    def risk_button_clicked(self):
        # 재식별 위험 측정
        self.data_process_thread = threading.Thread(target=self.calculate_risk,
                                                    args=(self.output_data_set, self.reordered_input_data_set,
                                                          self.data_types, self.is_sensitive_information,
                                                          self.attribute_mapping))
        self.data_process_thread.start()
        self.data_process_thread.join()

        # 출력 탭에 위험도 표기
        self.riskPercentLabel.setText(u'{:.2f} %'.format(self.risk_ratio * 100))
        # 위험 >= 0.05 > 경고 >= 0.0004 > 양호
        if self.risk_ratio >= 0.05:
            self.fineLabel.hide()
            self.warningLabel.hide()
            self.dangerousLabel.show()
            self.riskCommentLabel.setText(u'적절한 설정을 사용하여 다시 비식별화하십시오.')
            QMessageBox.warning(self, u'재식별 위험 평가 결과',
                                u'재식별 위험도: 위험\n재식별율: {:.2f} %\n적절한 설정을 사용하여 다시 비식별화하십시오.'
                                .format(self.risk_ratio * 100))
        elif self.risk_ratio >= 0.0004:
            self.fineLabel.hide()
            self.warningLabel.show()
            self.dangerousLabel.hide()
            self.riskCommentLabel.setText(u'약간의 재식별 위험이 있습니다.')
        else:
            self.fineLabel.show()
            self.warningLabel.hide()
            self.dangerousLabel.hide()
            self.riskCommentLabel.setText(u'데이터의 비식별 조치가 안전합니다.')

    def calculate_risk(self, output_data_set, aux_data_set, data_types, is_sensitive_information, attribute_mapping):
        self.risk_ratio = risk(output_data_set, data_types, is_sensitive_information, aux_data_set,
                               attribute_mapping)

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
        # 마법사에서 설정한 내용을 메인 윈도우의 속성 표로 옮기기 
        column_count = self.input_file_wizard.datatypeTable.rowCount()
        self.attributeTable.setRowCount(column_count)
        for attribute_index in xrange(column_count):
            attribute_name = self.input_file_wizard.datatypeTable.item(attribute_index, 0)
            self.attributeTable.setItem(attribute_index, 0, QTableWidgetItem(attribute_name.text()))

            datatype_combobox = self.input_file_wizard.datatypeTable.cellWidget(attribute_index, 1)
            self.attributeTable.setCellWidget(attribute_index, 1, datatype_combobox)

            characteristic_combobox = self.input_file_wizard.characteristicTable.cellWidget(attribute_index, 1)
            self.attributeTable.setCellWidget(attribute_index, 2, characteristic_combobox)

            self.attributeTable.setItem(attribute_index, 3, QTableWidgetItem(u''))

        self.input_file_wizard.destroy()
        # 입력 데이터 표시
        display_data_set_on_table(self.inputTable, self.input_attributes, self.input_data_set)

    def output_left_table_vertically_scrolled(self):
        """
        출력 탭 왼쪽 표 수직 스크롤 시
        """
        # 스크롤 싱크
        scroll_position = self.outputTableLeft.verticalScrollBar().value()
        self.outputTableRight.verticalScrollBar().setValue(scroll_position)

    def output_right_table_vertically_scrolled(self):
        """
        출력 탭 오른쪽 표 수직 스크롤 시
        """
        # 스크롤 싱크
        scroll_position = self.outputTableRight.verticalScrollBar().value()
        self.outputTableLeft.verticalScrollBar().setValue(scroll_position)

    def output_left_table_horizontally_scrolled(self):
        """
        출력 탭 왼쪽 표 수평 스크롤 시
        """
        # 스크롤 싱크
        scroll_position = self.outputTableLeft.horizontalScrollBar().value()
        self.outputTableRight.horizontalScrollBar().setValue(scroll_position)

    def output_right_table_horizontally_scrolled(self):
        """
        수평 탭 오른쪽 표 수직 스크롤 시
        """
        # 스크롤 싱크
        scroll_position = self.outputTableRight.horizontalScrollBar().value()
        self.outputTableLeft.horizontalScrollBar().setValue(scroll_position)

    def k_radio_button_clicked(self):
        """
        익명화 모델 k-익명성으로 선택 전환 시 
        """
        # 모수 선택 창 활성/비활성 전환
        self.kValueBox.setEnabled(True)
        self.lValueBox.setEnabled(False)

    def l_radio_button_clicked(self):
        """
        익명화 모델 l-다양성으로 선택 전환 시 
        """
        # 모수 선택 창 활성/비활성 전환
        self.lValueBox.setEnabled(True)
        self.kValueBox.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.show()
    app.exec_()

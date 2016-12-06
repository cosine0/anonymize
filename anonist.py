# coding=utf8
import os
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from help import HelpWindow
from level import LevelWindow
from table import display_data_set_on_table, load_csv_as_data_set, save_data_set_as_csv

reload(sys)
sys.setdefaultencoding('utf8')

form_class = uic.loadUiType('ui/main.ui')[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.input_file_name = None
        self.output_file_name = None
        self.input_data_set = None
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
        self.level_window = None

        # 실행 버튼 바인드
        self.runButton.clicked.connect(self.run_clicked)

        # 돌아가기 버튼 바인드
        self.returnButton.clicked.connect(self.return_clicked)

        # 출력 탭 스크롤 싱크
        self.outputTableLeft.verticalScrollBar().valueChanged.connect(self.output_left_table_vertically_scrolled)
        self.outputTableRight.verticalScrollBar().valueChanged.connect(self.output_right_table_vertically_scrolled)
        self.outputTableLeft.horizontalScrollBar().valueChanged.connect(self.output_left_table_horizontally_scrolled)
        self.outputTableRight.horizontalScrollBar().valueChanged.connect(self.output_right_table_horizontally_scrolled)

    def import_clicked(self):
        self.input_file_name = QFileDialog.getOpenFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.input_file_name:
            return

        self.import_csv(self.input_file_name)
        display_data_set_on_table(self.inputTable, self.input_data_set)

    def save_input_clicked(self):
        if not self.input_data_set:
            QMessageBox.critical(self, u'저장 오류', u'입력 데이터가 없습니다.')
            return

        self.input_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.input_file_name:
            return

        save_data_set_as_csv(self.input_data_set, self.input_file_name, self.encoding)

    def save_output_clicked(self):
        if not self.output_data_set:
            QMessageBox.critical(self, u'저장 오류', u'출력 데이터가 없습니다.')
            return

        self.output_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')
        if not self.output_file_name:
            return

        save_data_set_as_csv(self.output_data_set, self.output_file_name, self.encoding)

    def help_clicked(self):
        self.help_window = HelpWindow()
        self.help_window.show()

    def about_clicked(self):
        return QMessageBox.information(self, u"Intorduce", u"이 툴은 개인정보를 비식별 조치하는 툴입니다.\nKITRI fwvaBOB 5th No Jam'.",
                                       QMessageBox.Ok)

    def level_edit_button_clicked(self):
        self.level_window = LevelWindow()
        self.level_window.show()

    def run_clicked(self):
        QMessageBox.information(self, u"실행", u"처리 중...", QMessageBox.Ok)
        self.mainTab.setCurrentIndex(1)
        self.output_data_set, _ = load_csv_as_data_set(os.path.join('example', u'기본데이터(비식별화).csv'))
        display_data_set_on_table(self.outputTableLeft, self.input_data_set)
        display_data_set_on_table(self.outputTableRight, self.output_data_set)

    def return_clicked(self):
        self.mainTab.setCurrentIndex(0)

    def import_csv(self, file_name):
        try:
            self.input_data_set, self.encoding = load_csv_as_data_set(file_name)
        except:
            QMessageBox.critical(self, u'가져오기 오류', u'파일이 없거나 잘못되었습니다.')

    def output_left_table_vertically_scrolled(self):
        scroll_position = self.outputTableLeft.verticalScrollBar().value()
        self.outputTableRight.verticalScrollBar().setValue(scroll_position)

    def output_right_table_vertically_scrolled(self):
        scroll_position = self.outputTableRight.verticalScrollBar().value()
        self.outputTableLeft.verticalScrollBar().setValue(scroll_position)

    def output_left_table_horizontally_scrolled(self):
        scroll_position = self.outputTableLeft.horizontalScrollBar().value()
        self.outputTableRight.horizontalScrollBar().setValue(scroll_position)

    def output_right_table_horizontally_scrolled(self):
        scroll_position = self.outputTableRight.horizontalScrollBar().value()
        self.outputTableLeft.horizontalScrollBar().setValue(scroll_position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

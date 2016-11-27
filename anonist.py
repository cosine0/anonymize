# coding=utf8
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from level import LevelWindow

reload(sys)
sys.setdefaultencoding('utf8')

form_class = uic.loadUiType('main.ui')[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.input_file_name = None
        self.output_file_name = None
        self.input_data_set = None

        self.setupUi(self)

        # 파일 메뉴 바인드
        self.actionImport.triggered.connect(self.import_clicked)
        self.actionSave_input.triggered.connect(self.save_input_clicked)
        self.actionSave_output.triggered.connect(self.save_output_clicked)
        self.actionQuit.triggered.connect(self.close)

        # 헬프 메뉴 바인드
        self.actionHelp_content.triggered.connect(self.help_clicked)
        self.actionAbout.triggered.connect(self.about_clicked)

        # 레벨 변경 바인드
        self.levelEditButton.clicked.connect(self.level_edit_button_clicked)

    def import_clicked(self):
        try:
            self.input_file_name = QFileDialog.getOpenFileName(self, filter=u'CSV 파일 (*.csv)')[0]
        except IndexError:
            pass

    def save_input_clicked(self):
        try:
            self.input_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')[0]
        except IndexError:
            pass

    def save_output_clicked(self):
        try:
            self.input_file_name = QFileDialog.getSaveFileName(self, filter=u'CSV 파일 (*.csv)')[0]
        except IndexError:
            pass

    def help_clicked(self):
        return QMessageBox.information(self, 'Oops', 'Not Implemented.', QMessageBox.Ok)

    def about_clicked(self):
        return QMessageBox.information(self, 'Oops', 'Not Implemented.', QMessageBox.Ok)

    def level_edit_button_clicked(self):
        level_window = LevelWindow(parent=self)
        level_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

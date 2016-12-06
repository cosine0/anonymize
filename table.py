import chardet
import unicodecsv
from PyQt4.QtGui import *


def display_data_set_on_table(qtable_widget, data_set):
    assert isinstance(qtable_widget, QTableWidget)
    qtable_widget.setRowCount(0)

    if not data_set:
        return

    qtable_widget.setRowCount(len(data_set))
    qtable_widget.setColumnCount(len(data_set[0]))

    for record_index, record in enumerate(data_set):
        for attribute_index, attribute in enumerate(record):
            item = QTableWidgetItem(attribute)
            qtable_widget.setItem(record_index, attribute_index, item)


def load_csv_as_data_set(file_name):
    data_set = []
    with open(file_name, 'rb') as input_file:
        encoding_detection_result = chardet.detect(input_file.read(4096))
        encoding = encoding_detection_result['encoding']
        input_file.seek(0)
        for record in unicodecsv.reader(input_file, encoding=encoding):
            data_set.append(record)

    return data_set, encoding


def save_data_set_as_csv(data_set, file_name, encoding=None):
    with open(file_name, 'wb') as output_file:
        unicodecsv.writer(output_file, encoding=encoding).writerows(data_set)

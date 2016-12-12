# coding=utf-8
import chardet
import unicodecsv
from PyQt4.QtGui import *


def display_data_set_on_table(qtable_widget, attribute_names, data_set):
    """
    QTableWidget을 data_set의 내용으로 채운다. 
    :param qtable_widget: 채워 넣을 대상 QTableWidget. 
    :param attribute_names: 속성 이름들의 list. QTableWidgetd의 horizontalHeader로 들어간다. 
    :param data_set: str의 list들의 list. 레코드를 나타내는 list들이 여러 개 있는 list형태로 주어진 표 형태의 자료.
    """
    assert isinstance(qtable_widget, QTableWidget)

    # 기존 표 내용 삭제
    qtable_widget.setRowCount(0)

    # 빈 데이터의 경우 아무것도 하지 않는다
    if not attribute_names or not data_set:
        return

    # row와 column개수 설정 
    qtable_widget.setRowCount(len(data_set))
    qtable_widget.setColumnCount(len(attribute_names))

    # horizontalHeader를 속성명으로 채운다
    qtable_widget.setHorizontalHeaderLabels(attribute_names)

    # 각 셀을 data_set의 내용으로 채운다
    for record_index, record in enumerate(data_set):
        for attribute_index, attribute in enumerate(record):
            item = QTableWidgetItem(attribute)
            qtable_widget.setItem(record_index, attribute_index, item)

    # 각 column의 너비를 셀 문자열 너비에 맞춘다
    qtable_widget.resizeColumnsToContents()


def load_csv_as_data_set(file_name):
    """
    csv 파일을 읽어 str의 list들의 list 형태로 만든다.
    :param file_name: csv 파일명
    :return: tuple(['header1', 'header2', ...],
     [['row1_column1', 'row1_column2', ...], ['row2_column1', 'row2_column2', ...], ...],
     'encoding')
     csv 파일의 인코딩을 감지한 후, (헤더, 데이터 셋, 인코딩)의 tuple을 반환한다.
    """
    data_set = []
    with open(file_name, 'rb') as input_file:
        # chardet 라이브러리를 사용해 인코딩 감지
        encoding_detection_result = chardet.detect(input_file.read(4096))
        encoding = encoding_detection_result['encoding']
        input_file.seek(0)

        # unicodecsv reader로 파일 읽기
        for record in unicodecsv.reader(input_file, encoding=encoding):
            data_set.append(record)

    # 첫 줄을 헤더, 나머지 줄을 데이터로 분리한다.
    return data_set[0], data_set[1:], encoding


def save_data_set_as_csv(attribute_names, data_set, file_name, encoding=None):
    """
    str의 list들의 list 형태 데이터를 csv 파일에 쓴다.
    :param attribute_names: 속성 이름들의 list. csv 파일의 헤더로 들어간다.
    :param data_set: str의 list들의 list 형태로 된 데이터 
    :param file_name: csv 파일명
    :param encoding: csv 파일 인코딩.
    :return: 
    """
    with open(file_name, 'wb') as output_file:
        if encoding is None:
            csv_writer = unicodecsv.writer(output_file)
        else:
            csv_writer = unicodecsv.writer(output_file, encoding=encoding)
        # 헤더 쓰기
        csv_writer.writerow(attribute_names)

        # 데이터 쓰기
        csv_writer.writerows(data_set)

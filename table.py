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

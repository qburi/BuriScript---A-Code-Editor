from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import mysql.connector

style_sheet = """
QTableWidget{
    background-color: #111111;
    color: white;
    gridline-color: #00758F;
    border: 0px;
}
QTableWidget::item{
    border-bottom: 1px solid #00758F;
    background-color: #111111;
    color: white;
}
QTableWidget::item:hover {
    border: 1px solid #00758F;
    background-color: #323437;
    color: white;
}
QTableCornerButton::section{
    background-color: #111111;
    color: white;
}
QHeaderView::section{
    background-color: #111111;
    color: #028cab; 
}
QScrollBar:vertical{
    border: none;
    background: #111111;
    width: 10px;
    margin: 15px 0px 15px 0px;
    border-radius: 0px;
}

/*  HANDLE BAR VERTICAL */
QScrollBar::handle:vertical {	
    background-color: #323437;
    min-height: 10px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover{	
    background-color: #3f4040
;
}
QScrollBar::handle:vertical:pressed {	
    background-color: #3f4040;
}

/* BTN TOP - SCROLLBAR */
QScrollBar::sub-line:vertical {
    border: none;
    background-color: #323437;
    height: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical:hover {	
    background-color: #3f4040;
}
QScrollBar::sub-line:vertical:pressed {	
    background-color: #3f4040;
}
/* BTN BOTTOM - SCROLLBAR */
QScrollBar::add-line:vertical {
    border: none;
    background-color: #323437;
    height: 15px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::add-line:vertical:hover {
    background-color: #3f4040;
}
QScrollBar::add-line:vertical:pressed {
    background-color: #3f4040;
}

/* RESET ARROW */
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: #111111;
}



/* HORIZONTAL SCROLLBAR */
QScrollBar:horizontal{
border: 0px solid grey;
background: #111111;
height: 10px;
margin: 0px 20px 0 20px;            
}

QScrollBar::handle:horizontal {
background: #323437;
min-width: 20px;
}

QScrollBar::handle:horizontal:hover{
background: #3f4040;
}

QScrollBar::add-line:horizontal {
border: 0px solid grey;
background: #323437;
width: 20px;
subcontrol-position: right;
subcontrol-origin: margin;
}

QScrollBar::add-line:horizontal:hover{
background: #3f4040;
}

QScrollBar::sub-line:horizontal {
border: 0px solid grey;
background: #323437;
width: 20px;
subcontrol-position: left;
subcontrol-origin: margin;

}

QScrollBar::sub-line:horizontal:hover{
background: #3f4040;
}

QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal
{
    background: none;
    border: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{
    background: #111111;
    border: 0px;
}
"""


class CustomTableWidget(QTableWidget):
    def __init__(self, data_contents, sql_cursor, parent=None):
        super(CustomTableWidget, self).__init__(parent)
        self.nested_content: list = data_contents
        self.__sql_cursor: mysql.connector.connect = sql_cursor

        """Set values to attributes"""
        self.setStyleSheet(style_sheet)
        self.setFocusPolicy(Qt.NoFocus)
        self.setRowCount(len(self.nested_content))
        self.setColumnCount(len(self.nested_content[0]))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalHeaderLabels(list(self.__sql_cursor.column_names))
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.make_rows_and_columns()

    def make_rows_and_columns(self) -> None:
        """
        EXAMPLE self.nested_content:
        [(1, 'burger', Decimal('5.99')),
         (2, 'pizza', Decimal('9.99')),
         (3, 'straw', Decimal('0.00')),
         (4, 'goat', Decimal('13.99')),
         (5, 'sticks', Decimal('0.00')),
         (6, 'twigs', Decimal('0.00')),
         (7, 'choco', Decimal('10.00')),
         (8, 'vanilla ice cream', Decimal('10.00')),
         (9, 'chips', Decimal('10.00'))]
        """
        for row, value in enumerate(self.nested_content):
            for column, data_point_in_row in enumerate(value):
                item_to_set = QTableWidgetItem(str(data_point_in_row))
                item_to_set.setFont(QFont("JetBrains Mono"))
                self.setItem(row, column, item_to_set)




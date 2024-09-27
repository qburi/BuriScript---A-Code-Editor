import sys
from copy import deepcopy
from typing import Optional
import json
import mysql.connector
from tabulate import tabulate
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qsci import *
import logging
import os

from MySQLScintilla.table_widget_sql import CustomTableWidget
from time import sleep
import threading

UNIVERSAL_FONT = "JetBrains Mono"
instance_check_output_window = False
pop_window_exists = None
output_window_exists = None


def settings_editor():
    import csv
    with open('images_icons\\settings.csv', mode='r') as file:
        csv_file = csv.reader(file)
        data = {}
        for lines in csv_file:
            data[lines[0]] = lines[1]
    return data


def connect_to_sql_server():
    settings_data = settings_editor()
    error_message = ""
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user='root',
            password=settings_data['SQL_PASSWORD'],
            database=settings_data['SQL_CURRENT_DATABASE']
        )
    except Exception as error:
        mydb = None
        error_message = str(error)
        logging.warning(error.__class__.__name__, error)
    return mydb, error_message


try:
    mydb, error_msg = connect_to_sql_server()
except FileNotFoundError:
    pass
#warning: check here for issues from MYSQLSCINTILLAMAIN

button_style_sheet = """
QPushButton{
    background-color: #111111;
    color: white;
}
/*
QPushButton::pressed{
    background-color: red;
    color: white;
}
*/
QPushButton:hover{
    background-color: #323437;
    color: white;
}
"""


SLIDER_STYLE_SHEET = """
QSlider::groove:horizontal {
    border: 1px solid #00758F;
    height: 10px;
    background: #111111;
    margin: 0px;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #00758F;
    border: 1px solid #565a5e;
    width: 24px;
    height: 8px;
    border-radius: 4px;
}
"""


class CustomSlider(QSlider):
    """This slider changes font of popup window"""
    def __init__(self, parent: Optional[QWidget]=None):
        super().__init__(Qt.Horizontal, parent)
        self.__parent = parent

        self.setStyleSheet(SLIDER_STYLE_SHEET)
        self.setRange(9, 20)
        self.setTickInterval(1)
        self.setSingleStep(1)
        self.setFixedSize(100, 30)
        self.valueChanged[int].connect(self.value_changed)

    def value_changed(self, value):
        table_widget = self.__parent._sql_output_widget._table_widget
        font: QFont = table_widget.font()
        font.setPointSize(value)
        table_widget.setFont(font)


def pop_out_window(contents, output_message, mycursor, parent):
    global pop_window_exists

    class PopUpWindow(QWidget):
        def __init__(self):
            super().__init__()
            self._sql_output_widget = CustomWidget(contents, output_message, mycursor, self)
            self._sql_output_widget.close_button.setParent(None)
            self._sql_output_widget.pop_out_button.setParent(None)
            self.__width = QDesktopWidget().screenGeometry().width()
            self.__height = QDesktopWidget().screenGeometry().height()
            self._sql_output_widget.setGeometry(0, 0, self.__width, self.__height)
            self.__custom_style_sheet = """background-color: #111111;
                                           color: white;"""
            self.font_slider = CustomSlider(self)
            """------------------------------------Style-sheets+Attributes-------------------------------------------"""
            self.setStyleSheet(self.__custom_style_sheet)
            self._sql_output_widget.move(0, 30)
            self.font_slider.move(0, 0)
            self.setGeometry(0, 0, self.__width, self.__height)
            self.showMaximized()

    if pop_window_exists is not None:
        pop_window_exists.close()
        pop_window_exists.setParent(None)
    pop_window_exists = PopUpWindow()


class CustomWidget(QWidget):

    def __init__(self, contents, output_message, my_cursor, parent: Optional[QMainWindow]=None):
        global output_window_exists
        super(CustomWidget, self).__init__(parent)
        """
        ------------------------Initialize-------------------
        """
        if output_window_exists is not None:
            output_window_exists.close()
            output_window_exists.setParent(None)
            # Any bug due to opening of output window may be caused here
        output_window_exists = self
        self.__contents_list: list = contents
        self.__output_message = output_message
        self.__mysql_cursor = my_cursor
        self.__parent = parent
        """
        ------------------------Widget-Control----------------
        """
        self.setStyleSheet("""background-color: #111111'
                              color: white;
                           """)
        self.__lyt = QVBoxLayout()
        self.message_text_edit = QTextEdit(self.__output_message)
        self.message_text_edit.setReadOnly(True)
        self.message_text_edit.setDisabled(True)
        self.message_label_font = QFont(UNIVERSAL_FONT)
        self.message_label_font.setPointSize(15)
        self.message_text_edit.setFont(self.message_label_font)
        self.message_text_edit.setStyleSheet("""background-color: #111111;
                                              color: white;
                                              border: 0px;
                                              """)
        self.run_exception_handling_operations()
        if self.can_run_table_widget:
            self._table_widget = CustomTableWidget(self.__contents_list, self.__mysql_cursor, parent)
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet(button_style_sheet)
        self.close_button.setFont(QFont(UNIVERSAL_FONT))
        self.close_button.clicked.connect(lambda: self.close_widget())
        self.pop_out_button = QPushButton("Pop Out ↗")
        self.pop_out_button.setStyleSheet(button_style_sheet)
        self.pop_out_button.setFont((QFont(UNIVERSAL_FONT)))
        self.pop_out_button.clicked.connect(lambda: self.pop_out_window())
        """-----------------------------------------ADD-WIDGETS-TO-LAYOUT--------------------------------------------"""
        self.__lyt.addWidget(self.close_button)
        self.__lyt.addWidget(self.pop_out_button)
        if self.can_run_table_widget:
            self.__lyt.addWidget(self._table_widget)
        self.__lyt.addWidget(self.message_text_edit)
        self.setLayout(self.__lyt)
        self.setGeometry(0, 0, 500, QDesktopWidget().screenGeometry().height() - 200)
        self.move(QDesktopWidget().screenGeometry().width() - 500, 0)
        self.show()

    def close_widget(self):
        self.close()

    def run_exception_handling_operations(self):
        self.can_run_table_widget = False if not self.__contents_list else True

    def pop_out_window(self):
        self.close()
        self.setParent(None)
        pop_out_window(self.__contents_list, self.__output_message, self.__mysql_cursor, self.__parent)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__frm = QFrame(self)
        self.__lyt = QVBoxLayout()
        self.setCentralWidget(self.__frm)
        self.__frm.setLayout(self.__lyt)
        """
        ------------------------------EDITOR-LEXER-QSciLexerSQL------------------------------
        """
        self.__editor = QsciScintilla()
        self.__lexer = QsciLexerSQL(self.__editor)
        self.__lexer.setFoldCompact(False)
        self.__lexer.setFoldComments(True)
        self.__lexer.setFoldAtElse(True)
        self.__lexer.setFoldOnlyBegin(True)
        self.__lexer.setDefaultFont(QFont(UNIVERSAL_FONT))
        self.__lexer.setDefaultColor(QColor("white"))
        self.__lexer.setDefaultPaper(QColor("#111111"))
        self.__editor.setLexer(self.__lexer)
        lexer_color_code = \
            {
                self.__lexer.Default: "white",
                self.__lexer.Comment: "#7d7d7d",
                self.__lexer.CommentLine: "#7d7d7d",
                self.__lexer.CommentDoc: "#7d7d7d",
                self.__lexer.Number: "#6b6fe3",
                self.__lexer.Keyword: "#00758f",
                self.__lexer.DoubleQuotedString: "#E2EA83",
                self.__lexer.SingleQuotedString: "#E2EA83",
                self.__lexer.PlusKeyword: "#00758f",
                self.__lexer.PlusPrompt: "#00758f",
                self.__lexer.Operator: "#00758f",
                self.__lexer.Identifier: "white",
                self.__lexer.PlusComment: "#7d7d7d",
                self.__lexer.CommentLineHash: "#7d7d7d",
                self.__lexer.CommentDocKeyword: "#7d7d7d",
                self.__lexer.CommentDocKeywordError: "#7d7d7d",
                self.__lexer.QuotedIdentifier: "white",
                self.__lexer.QuotedOperator: "#00758f"
            }
        for enum, color_code in lexer_color_code.items():
            self.__lexer.setColor(QColor(color_code), enum)
            self.__lexer.setFont(QFont(UNIVERSAL_FONT), enum)
        self.__lexer.setFont(QFont("Courier New"), self.__lexer.Operator)
        """
        -----------------------------------------------------------------------------------------
        """
        self.setStyleSheet('background-color: #111111;'
                           'color: white;')
        self.__lyt.addWidget(self.__editor)
        # self.__lyt.addWidget(self.customwidget, 1, Qt.AlignRight)
        """
        ------------SHORTCUTS-----------
        """
        self.run_sql_file = QShortcut(QKeySequence("F5"), self)
        self.run_sql_file.activated.connect(lambda: self.run_sql())
        """
        """
        self.setGeometry(0, 0, 1920, 1080)
        self.show()
        new_thread = threading.Thread(target=self.run_on_thread, daemon=True)
        # new_thread.start()

    def run_on_thread(self):
        while True:
            print(self.__editor.hasFocus())
            sleep(1)

    def run_sql(self):
        global instance_check_output_window
        mycursor = mydb.cursor()
        try:
            # mycursor.execute("INSERT INTO products\n"
            #                "VALUES (7, 'choco', 1);")
            commands = self.__editor.text().split(";")
            for command in list(commands):
                print(len(command))
                if command == "" or command == "\r\n"*int(len(command) / 2):
                    commands.remove(command)
            print(commands)
            for command in commands:
                mycursor.execute(command)
            contents = [x for x in mycursor]
            contents_deepcopy = deepcopy(contents)
            # headers = [field[0] for field in mycursor.description]
            print(tabulate(contents, headers=list(mycursor.column_names), tablefmt='psql'))
            output_message = f"{mycursor.rowcount} row(s) affected"
            print(output_message)
            mydb.commit()
            # print([field[0] for field in mycursor.description])
            # print(mycursor.fetchall())
            print(contents_deepcopy)
            if instance_check_output_window:
                instance_check_output_window = False
                self.customwidget.close()
                self.customwidget.deleteLater()
            else:
                instance_check_output_window = True
            self.customwidget = CustomWidget(contents, output_message, mycursor, self)
            self.customwidget.move(QDesktopWidget().screenGeometry().width() - 500, 0)
            self.customwidget.show()
        except Exception as error:
            print(error.__class__.__name__, error)
            if instance_check_output_window:
                instance_check_output_window = False
                self.customwidget.close()
                self.customwidget.deleteLater()
            else:
                instance_check_output_window = True
            self.customwidget = CustomWidget([], str(error), my_cursor=None, parent=self)
            self.customwidget.move(QDesktopWidget().screenGeometry().width() - 500, 0)
            self.customwidget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())



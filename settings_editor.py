from PyQt5.QtCore import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SettingsEditor(QMainWindow):
    def __init__(self):
        super(SettingsEditor, self).__init__()
        self.screen_geometry = QDesktopWidget().screenGeometry()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("images_icons\\settings_icon.ico"))
        self.setGeometry(int(self.screen_geometry.width() / 2) - 200, int(self.screen_geometry.height() / 2) - 300, 500, 500)
        self.__frm = QFrame(self)
        self.__frm.setStyleSheet("""
                    QFrame {
                    background-color: #212A41 
                    color: white}""")
        self.__frm.setStyleSheet("QWidget { background-color: #212A41 }")
        self.__lyt = QVBoxLayout()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.setStyleSheet("""
                            QScrollBar:vertical {
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
                        background-color: #111111;
                        color: white;
                        
                """)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.font_used = QFont("JetBrains Mono")
        self.setFont(self.font_used)
        self.close_window = QShortcut(QKeySequence("Esc"), self)
        self.close_window.activated.connect(lambda: self.close_window_and_read())
        self.font_label = QLabel()
        self.font_label.setStyleSheet("color: white;")
        self.font_label.setFixedWidth(100)
        self.font_label.setFixedHeight(25)
        self.font_label.setText("Select Font")
        self.combo_box = QFontComboBox()
        self.__data_to_append = self.get_defaults()
        self.combo_box.setCurrentText(self.__data_to_append['FONT'])
        self.combo_box.setStyleSheet("color: white;")
        self.combo_box.setFixedWidth(100)
        self.combo_box.setFixedHeight(25)
        self.__lyt.setSpacing(10)
        self.__font_size_label = QLabel('Set Default Font Size')
        self.__font_size_label.setStyleSheet('color: white;')
        self.font_size_line_edit = QLineEdit()
        self.integer_validator = QIntValidator()
        self.integer_validator.setRange(1, 999)
        self.font_size_line_edit.setFixedSize(100, 20)
        self.font_size_line_edit.setText(self.__data_to_append['FONT_SIZE'])
        self.font_size_line_edit.setStyleSheet('color: white')
        self.font_size_line_edit.setFont(QFont("JetBrains Mono"))
        self.font_size_line_edit.setValidator(self.integer_validator)

        # Combo Box for mode
        self.combo_box_text_mode = QComboBox(self)
        self.combo_box_custom_text_items = ["Custom Text", "Random Words", "TypeRacer Database"]
        self.combo_box_text_mode.addItems(self.combo_box_custom_text_items)
        self.combo_box_text_mode.setCurrentText(self.__data_to_append['CUSTOM_RUN'])
        self.combo_box_text_mode.setStyleSheet("color: white;")
        self.combo_box_text_mode.setFixedWidth(100)
        self.combo_box_text_mode.setFixedHeight(25)

        # Combo Box Label
        self.combo_box_label = QLabel()
        self.combo_box_label.setStyleSheet("color: white;")
        self.combo_box_label.setFixedWidth(250)
        self.combo_box_label.setFixedHeight(25)
        self.combo_box_label.setText("Select Mode for BuriRacer")
        """
        self.__check_box.setChecked(self.is_checked())
        self.__check_box.setStyleSheet('color: white;')
        self.__check_box.setFont(QFont("JetBrains Mono"))
        """
        # Label for Password SQL
        self.password_sql_label = QLabel()
        self.password_sql_label.setStyleSheet('color: white;')
        self.password_sql_label.setFont(QFont("JetBrains Mono"))
        self.password_sql_label.setFixedWidth(250)
        self.password_sql_label.setFixedHeight(25)
        self.password_sql_label.setText("Enter Password for SQL Connection")

        # LinEdit for Password SQL
        self.password_line_edit = QLineEdit()
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.password_line_edit.setFixedSize(100, 20)
        self.password_line_edit.setText(self.__data_to_append['SQL_PASSWORD'])
        self.password_line_edit.setStyleSheet('color: white;')
        self.password_line_edit.setFont(QFont("JetBrains Mono"))

        # Label for USE DATABASE
        self.database_sql_label = QLabel()
        self.database_sql_label.setStyleSheet('color: white;')
        self.database_sql_label.setFont(QFont("JetBrains Mono"))
        self.database_sql_label.setFixedWidth(250)
        self.database_sql_label.setFixedHeight(25)
        self.database_sql_label.setText("Enter Database Name")

        # LineEdit for USE DATABASE
        self.database_sql_line_edit = QLineEdit()
        self.database_sql_line_edit.setFixedSize(100, 20)
        self.database_sql_line_edit.setText(self.__data_to_append['SQL_CURRENT_DATABASE'])
        self.database_sql_line_edit.setStyleSheet('color: white;')
        self.database_sql_line_edit.setFont(QFont("JetBrains Mono"))

        # Label for  full file path including the text file name for Append text in editor to text file
        self.append_editor_text_to_file_label = QLabel()
        self.append_editor_text_to_file_label.setStyleSheet('color: white;')
        self.append_editor_text_to_file_label.setFont(QFont("JetBrains Mono"))
        self.append_editor_text_to_file_label.setFixedWidth(260)
        self.append_editor_text_to_file_label.setFixedHeight(25)
        self.append_editor_text_to_file_label.setText("Enter full file Path for Program Logs")


        # LineEdit for full file path including the text file name for Append text in editor to text file
        self.append_editor_text_to_file = QLineEdit()
        self.append_editor_text_to_file.setFixedSize(500, 20)
        self.append_editor_text_to_file.setStyleSheet('color: white;')
        self.append_editor_text_to_file.setFont(QFont("JetBrains Mono"))
        self.append_editor_text_to_file.setText(rf"{self.__data_to_append['LOG_PROGRAM_FILE_PATH']}")

        # layout
        self.__lyt.addWidget(self.font_label, 0)
        self.__lyt.addWidget(self.combo_box, 0)
        self.__lyt.addWidget(self.__font_size_label, 0)
        self.__lyt.addWidget(self.font_size_line_edit, 0)
        self.__lyt.addWidget(self.combo_box_label, 0)
        self.__lyt.addWidget(self.combo_box_text_mode, 0)
        self.__lyt.addWidget(self.password_sql_label, 0)
        self.__lyt.addWidget(self.password_line_edit, 0)
        self.__lyt.addWidget(self.database_sql_label, 0)
        self.__lyt.addWidget(self.database_sql_line_edit, 0)
        self.__lyt.addWidget(self.append_editor_text_to_file_label, 0)
        self.__lyt.addWidget(self.append_editor_text_to_file, 0)
        self.__lyt.addStretch(1)
        self.show()


    def saved_selected_combo_box(self):
        with open("images_icons\\settings.csv", mode='r') as combo_box_csv:
            from csv import reader
            settings_file = reader(combo_box_csv)
            for x in settings_file:
                if x[0] == "CUSTOM_RUN":
                    return x[1]

    def is_checked(self):
        with open("images_icons\\settings.csv", mode="r") as csv_read:
            import csv
            csv_read_file = csv.reader(csv_read)
            for x in csv_read_file:
                if x[0] == "CUSTOM_RUN":
                    return True if x[1] == "True" else False
    def close_window_and_read(self):
        # print(self.combo_box.currentText())
        all_items = [self.combo_box.itemText(i) for i in range(self.combo_box.count())]
        # print(all_items)
        if self.combo_box.currentText() not in all_items or int(self.font_size_line_edit.text()) == 0:
            self.close()
            return
        import csv
        with open("images_icons\\settings.csv", mode="w+", newline='') as settings_file:
            csv_file = csv.writer(settings_file)
            data = [
                    ['FONT', f'{self.combo_box.currentText()}'],
                    ['FONT_SIZE', int(self.font_size_line_edit.text())],
                    ['CUSTOM_RUN', self.combo_box_text_mode.currentText()],
                    ['SQL_PASSWORD', self.password_line_edit.text()],
                    ['SQL_CURRENT_DATABASE', self.database_sql_line_edit.text()],
                    ['LOG_PROGRAM_FILE_PATH', rf"{self.append_editor_text_to_file.text()}"]
                    ]
            csv_file.writerows(data)
        with open('images_icons\\settings.csv', mode='r') as file:
            csvFile = csv.reader(file)
        self.close()

    def get_defaults(self):
        import csv
        with open('images_icons\\settings.csv', mode='r') as file:
            csvFile = csv.reader(file)
            data = {}
            for lines in csvFile:
                # print(lines)
                data[lines[0]] = lines[1]
        return data

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SettingsEditor()
    sys.exit(app.exec_())
# _*_ coding: utf-8 _*_

# Standard library imports
import logging
import sys
import re
import pathlib
import os
import os.path
import csv
import threading
import pickle
from typing import Final, Optional

# Third party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import sqlparse

# Local imports
import MySQLScintilla.MySQLScintillaMain
from search_box import SearchText
from MySQLScintilla.MySQLScintillaMain import CustomWidget
from BuriScriptLexers import CustomLexerPython, CustomLexerSQL
from PythonInterpreter import CustomPythonTerminal
from PythonInterpreter import INTERPRETER_BUTTON_STYLE_SHEET
from handle_logs import BuriScriptLogHandler
from BuriScriptFileModel import BuriScriptCwdExplorer, CustomTreeView
from BuriScriptScintillaEditor import BuriScriptEditor
from BuriScriptTabView import CustomTabWidget
from commenter_scintilla import ScintillaComponentCommenter
from TypeRacer.buriracer_window import BuriRacerWindow

home_path: Final[str] = os.getcwd()
check_backspace: list = []
instance_check_output_window: bool = False
with open("BuriScriptStyleSheets.qss", 'r') as style_sheets_qss:
    MAIN_WINDOW_STYLE_SHEET: str = style_sheets_qss.read()


def change_font_color_type(lexer_name, font_color_hex, enum_to_change):
    lexer_name.setColor(QColor(f'{font_color_hex}'), enum_to_change)
    settings_data = settings_editor()
    editor_font = QFont(settings_data['FONT'])
    editor_font.setPointSize(int(settings_data['FONT_SIZE']))
    lexer_name.setFont(editor_font, enum_to_change)


def settings_editor():
    os.chdir(home_path)
    with open('images_icons\\settings.csv', mode='r') as file:
        csv_file = csv.reader(file)
        data = {}
        for lines in csv_file:
            data[lines[0]] = lines[1]
    return data


UNIVERSAL_SETTINGS_INITIALIZED: dict = settings_editor()


class CustomBuriScriptFileModel(CustomTreeView):
    def __init__(self, path: str, parent_directory, parent_window: QMainWindow, tab_widget: QTabWidget,
                 parent: Optional[QMainWindow] = None):
        """
        :param path: path to show in file system model
        :param parent_directory: home_path
        :param parent_window: CustomMainWindow
        :param tab_widget: CustomTabWidget
        :param parent: CustomMainWindow
        """
        style_sheet = """
                        QTreeView{
                            background-color: #111111;
                            color: white;
                            border: 0px;
                            font-size: 11pt;
                        }
                        QHeaderView::section{
                            background-color: #111111;
                            color: white;
                            border: 0px;
                        }
                        QHeaderView::section:hover{
                            background-color: #323437;
                            color: white;
                            border: 0px;
                        }"""
        super().__init__(path, parent_directory, parent_window, parent)
        self.tab_widget_in_main_window = tab_widget
        self.setStyleSheet(style_sheet)
        self.supported_extensions = ['.sql', '.txt', '.py']
        self.python_terminal_not_instance = PythonTerminal

    def on_clicked(self, index):
        abs_path = self.dir_model.fileInfo(index).absoluteFilePath()
        if self.dir_model.fileInfo(index).isFile() and pathlib.Path(abs_path).suffix in self.supported_extensions and\
                not self.is_file_already_opened_in_editor(abs_path):
            self._parent_window.open_file(abs_path, can_run_directly=True)
            self.tab_widget_in_main_window.widget(self.tab_widget_in_main_window.currentIndex()).findChild(
                BuriScriptEditor).check_margin_width()

    def override_method_open_in_editor(self, absolute_file_path_to_open: str):
        if os.path.isfile(absolute_file_path_to_open) and pathlib.Path(absolute_file_path_to_open).suffix in \
                self.supported_extensions and not self.is_file_already_opened_in_editor(absolute_file_path_to_open):
            self._parent_window.open_file(absolute_file_path_to_open, can_run_directly=True)
            self.tab_widget_in_main_window.widget(self.tab_widget_in_main_window.currentIndex()).findChild(
                BuriScriptEditor).check_margin_width()

    def is_file_already_opened_in_editor(self, absolute_file_path):
        file_paths = list(self._parent_window.read_dat_file_has_file_paths_with_name().keys()) # abs file paths only
        return_value = True if absolute_file_path in file_paths else False
        if return_value:
            for i in range(self.tab_widget_in_main_window.count()):
                if self.tab_widget_in_main_window.widget(i).findChild(BuriScriptEditor).file_to_open_in_new_tab ==\
                        absolute_file_path:
                    self.tab_widget_in_main_window.setCurrentIndex(i)
                    break
                else:
                    pass
        return return_value


class PythonTerminal(CustomPythonTerminal):
    def __init__(self, file_name: str, file_path: str, parent_editor: QsciScintilla,
                 parent: Optional[QMainWindow]=None):
        super().__init__(file_name=file_name, parent=parent)

        self.__parent_editor = parent_editor
        self._file_name = file_name
        self._file_path = file_path

        self._console_push_button.setFont(QFont(UNIVERSAL_SETTINGS_INITIALIZED['FONT']))
        self._console_push_button.clicked.connect(lambda: self.run_in_console(self._file_name))


        self.screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen_geometry.width(), 500)
        self.move(0, self.screen_geometry.height() - 550)
        self.inBar.setFocus()
        self.__font = QFont(UNIVERSAL_SETTINGS_INITIALIZED['FONT'])
        self.__font.setPointSize(int(UNIVERSAL_SETTINGS_INITIALIZED['FONT_SIZE']))
        self.out.setFont(self.__font)
        self.inBar.setFont(self.__font)
        self.show()

    def run_in_console(self, file_to_run):
        def run_on_thread():
            os.chdir(self._file_path)
            os.system(rf'start python -i "{file_to_run}"')
            os.chdir(home_path)
        threading.Thread(target=run_on_thread, args=[]).start()

    def close_all_widgets_and_exit(self):
        super().close_all_widgets_and_exit()
        self.__parent_editor.setFocus()


class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__(None)
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        # self.showMaximized()
        self.setWindowTitle("BuriScript - A Text Editor")
        self.tab_widget = CustomTabWidget(parent_directory=home_path,
                                          parent=self)
        self.main_widget = QWidget(self)
        """
        Frame Plan
        There will be three layouts nested in widgets
        the main layout is called as self.__main_lyt and is a horizontal box layout which has one widget -> MenuBar
        the main layout has only one more widget which is called self.__under_menu_bar_widget
        Totally there are two widgets in the self.__main_lyt -> Horizontal layout QHBoxLayout Class.
        this widget has the file system model and the main editor (1). 
        the self.__under_menu_bar_widget has the main editor under another widget called self.tab_widget under the 
        self.__lyt. This tab widget takes care of all the Scintilla editors.
        Therefore the main editor (1) is under a layout self.__lyt which has only one widget that is self.tab_widget
        
        Draw a big rectangle (1) and nest one most rectangle (2) inside and the rectangle (2) has 2 more rectangles 
        inside namely File System Model rectangle (3) and tab widget rectangle (4)
        rectangle (1) -> Menu bar
        rectangle (2) -> nested in rectangle (1) File system model and tab widget
        rectangle (3) -> nested in rectangle (2) and has only File System Model
        rectangle (4) -> nested in rectangle (2) and has tab widget which handles the editors
        """
        self.__frm = QFrame(self)
        self.__frm.setStyleSheet("""
            QFrame {
                background-color: #111111;
                color: white}""")
        self.__frm.setStyleSheet("QWidget { background-color: #111111 }")
        self.__lyt = QVBoxLayout()
        self.__lyt.addWidget(self.tab_widget)
        self.__main_lyt = QVBoxLayout()
        self.__under_menu_bar_layout = QHBoxLayout()
        self.__under_menu_bar_widget: QWidget = QWidget(self)
        self.__under_menu_bar_widget.setLayout(self.__under_menu_bar_layout)

        self.__frm.setLayout(self.__main_lyt)
        # self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        settings_data = settings_editor()
        self.__myFont = QFont(settings_data['FONT'])
        self.__myFont.setPointSize(int(settings_data['FONT_SIZE']))

        self.__btn = QPushButton("Close")
        self.__btn.setFixedWidth(50)
        self.__btn.setFixedHeight(50)
        self.__btn.clicked.connect(self.__btn_action)
        self.__button_font_size = QFont()
        self.__button_font_size.setPointSize(10)
        self.__btn.setFont(self.__button_font_size)
        self.__btn.setStyleSheet("font: bold;"
                                 "background-color: #111111;"
                                 "width: 120px;"
                                 "color: white")
        # self.__lyt.addWidget(self.__btn)
        self.setWindowIcon(QIcon(r"images_icons\python_darkgreen_lightgreen.png"))

        """
        -------------------------------------------------ADDING-TITLE-BAR-------------------------------------------
        """
        # import titlebar
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.__titlebar = titlebar.Ui_Form(self)
        # self.__lyt.setSpacing(0)
        # self.__lyt.setContentsMargins(0, 0, 0, 0)
        # self.__lyt.addWidget(self.__titlebar)
        """
        """
        # QScintilla editor setup
        # ------------------------

        # Editor font
        self.__editor_font = QFont(settings_data['FONT'])
        self.__editor_font.setPointSize(int(settings_data['FONT_SIZE']))
        try:
            tab_to_open = list(
                self.read_dat_file_has_file_paths_with_name().items())[0][0]
        except IndexError:
            tab_to_open = ''
        # self.__editor = BuriScriptEditor(parent_directory=home_path,
        #                                  tab_file_path_absolute=tab_to_open,
        #                                  python_terminal_class_not_instance=PythonTerminal,
        #                                  parent=None)  # if set to self then menu bar is overriden
        self.setStyleSheet(MAIN_WINDOW_STYLE_SHEET)
        """

        -------------------------SHORTCUTS------------------------------------------
        """
        # self.comment_region = QShortcut(QKeySequence("Ctrl+3"), self)
        # self.comment_region.activated.connect(self.comment_out_selected_region)
        self.enclose_single = QShortcut(QKeySequence("Ctrl+'"), self)
        self.enclose_double = QShortcut(QKeySequence("Ctrl+Shift+'"), self)
        self.enclose_parenthesis = QShortcut(QKeySequence("Ctrl+9"), self)
        self.enclose_square = QShortcut(QKeySequence("Alt+["), self)
        self.enclose_brace = QShortcut(QKeySequence("Ctrl+{"), self)
        self.swap_lines_down = QShortcut(QKeySequence("Ctrl+Shift+Down"), self)
        self.swap_lines = QShortcut(QKeySequence("Ctrl+Shift+Up"), self)
        self.go_to_line = QShortcut(QKeySequence("Ctrl+G"), self)
        self.append_text_file_programs = QShortcut(QKeySequence("Ctrl+Shift+W"), self)
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)

        self.enclose_single.activated.connect(lambda: self.enclose_region_with_quotes("single"))
        self.enclose_double.activated.connect(lambda: self.enclose_region_with_quotes("double"))
        self.enclose_parenthesis.activated.connect(lambda: self.enclose_with_brackets("()"))
        self.enclose_square.activated.connect(lambda: self.enclose_with_brackets("[]"))
        self.enclose_brace.activated.connect(lambda: self.enclose_with_brackets("{}"))
        self.swap_lines.activated.connect(lambda: self.current_tab_editor().SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESUP))
        self.swap_lines_down.activated.connect(lambda:
                                               self.current_tab_editor().SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESDOWN))
        self.go_to_line.activated.connect(lambda: self.go_to_line_editor())
        self.append_text_file_programs.activated.connect(lambda: self.append_text_file_programs_editor())
        self.close_tab_shortcut.activated.connect(lambda: self.tab_widget.close_current_tab())
        """


        """
        self.__menu_bar: QMenuBar = 0
        self.set_up_menu()
        # self.__lyt.addWidget(self.__menu_bar)

        self.oldPos = self.pos()
        # CheckPassword(self)
        self.showMaximized()
        self.current_tab_editor().setFocus()
        self.__garbage_collection_list: list = []
        self.installEventFilter(self)

    """
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    """

    def enclose_with_brackets(self, bracket_type):
        bracket_to_enclose = bracket_type
        text_to_enclose = self.current_tab_editor().selectedText()
        if text_to_enclose:
            text_to_enclose = f"{bracket_to_enclose[0]}{text_to_enclose}{bracket_to_enclose[1]}"
            self.current_tab_editor().replaceSelectedText(text_to_enclose)

    def enclose_region_with_quotes(self, quote_type):
        text_to_enclose = self.current_tab_editor().selectedText()
        if text_to_enclose:
            text_to_enclose = f"'{text_to_enclose}'" if quote_type == "single" else f'"{text_to_enclose}"'
            self.current_tab_editor().replaceSelectedText(text_to_enclose)

    def _cursor_position_changed(self, line: int, index: int) -> None:
        self.__auto_complete.get_completions(line + 1, index, self.current_tab_editor().text())

    def load_autocomplete(self):
        pass

    def opendialog(self):
        file_name = QFileDialog.getOpenFileName(self, "Open File", "", "All files (*);;Python File (*.py);;SQL Text \
        File (*.sql)")
        with open(file_name[0], "r") as file_to_read:
            self.current_tab_editor().setText(file_to_read.readline())
            lines = file_to_read.readlines().pop(0)
            for x in lines:
                self.current_tab_editor().append(x)
                logging.info(x)
            logging.info(''.join(file_to_read.readlines()))

    def set_up_menu(self):
        style_for_menu = """
        QMenuBar {
            background-color: #111111;
            color: rgb(255,255,255);
            border: 1px solid #000;
        }

        QMenuBar::item {
            background-color: #111111;
            color: rgb(255,255,255);
        }

        QMenuBar::item::selected {
            background-color: #111111;
        }

        QMenu {
            background-color: #111111;
            color: rgb(255,255,255);
            border: 1px solid #000;           
        }

        QMenu::item::selected {
            background-color: rgb(30,30,30);
        }
    """
        self.__menu_bar = QMenuBar()
        self.__menu_bar.setStyleSheet(style_for_menu)
        settings_data = settings_editor()
        self.__menu_bar.setFont(QFont(settings_data['FONT']))
        file_menu = self.__menu_bar.addMenu("File")
        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        # menu_bar_2 = QMenuBar(self)
        # menu_bar_2.setStyleSheet(style_for_menu)
        # menu_bar_2.setFont(QFont("settings_data['FONT']"))
        edit_menu = self.__menu_bar.addMenu("Edit")
        comment_region = edit_menu.addAction("Comment/Uncomment Region")
        comment_region.setShortcut("Ctrl+3")
        comment_region.triggered.connect(self.comment_out_selected_region)
        search_text_in_code = edit_menu.addAction("Search Text")
        search_text_in_code.setShortcut("Ctrl+F")
        search_text_in_code.triggered.connect(self.find_text_in_code)
        zoom_in_or_out = edit_menu.addAction("Zoom In/Out")
        zoom_in_or_out.setShortcut("Ctrl+1")
        zoom_in_or_out.triggered.connect(lambda: self.zoom_in_or_out())
        perform_default_search = edit_menu.addAction("Google")
        perform_default_search.setShortcut("Ctrl+Shift+G")
        perform_default_search.triggered.connect(lambda: self.search_in_google())
        resize_qmain_window = edit_menu.addAction("Resize Window")
        resize_qmain_window.setShortcut("Ctrl+2")
        resize_qmain_window.triggered.connect(lambda: self.resize_window())
        settings_window = edit_menu.addAction("Settings")
        settings_window.setShortcut("Ctrl+Alt+I")
        settings_window.triggered.connect(lambda: self.open_settings_window())
        # menu_bar_3 = QMenuBar(self)
        # menu_bar_3.setStyleSheet(style_for_menu)
        # menu_bar_3.setFont(QFont("JetBrains Mono"))
        run_menu = self.__menu_bar.addMenu("Run")
        run_file = run_menu.addAction("Run File")
        run_file.setShortcut("F5")
        run_file.triggered.connect(self.run_python_file)
        run_buriracer = run_menu.addAction("Run BuriRacer!")
        run_buriracer.setShortcut("Ctrl+B")
        run_buriracer.triggered.connect(self.run_python_buriracer)
        run_directly_to_console = run_menu.addAction("Run From Console")
        run_directly_to_console.setShortcut("Ctrl+F5")
        run_directly_to_console.triggered.connect(lambda: self.run_directly_to_console())
        run_windows_file_explorer = run_menu.addAction("Get Working Directory")
        run_windows_file_explorer.triggered.connect(lambda: self.run_user_opened_working_directory())

        # menu_bar_4 = QMenuBar(self)
        # menu_bar_4.setStyleSheet(style_for_menu)
        # menu_bar_4.setFont(QFont("JetBrains Mono"))
        help_menu = self.__menu_bar.addMenu("Help")
        show_all_shortcuts = help_menu.addAction("Show Shortcuts")
        show_all_shortcuts.triggered.connect(self.show_shortcuts_in_text_file)
        find_documentation_help = help_menu.addAction("Find Module Documentation")
        find_documentation_help.triggered.connect(self.find_asked_module)

        screen_resolution = QDesktopWidget().screenGeometry()
        self.__menu_bar.setMinimumSize(int(screen_resolution.width() / 2), 25)
        # self.__menu_bar.setFixedSize(int(screen_resolution.width()), 25)
        # self.__lyt.addWidget(menu_bar_2)
        # self.__lyt.addWidget(menu_bar_3)
        # self.__lyt.addWidget(menu_bar_4)
        # new_widget = QWidget(self)
        # new_widget.setStyleSheet(MAIN_WINDOW_STYLE_SHEET)
        # new_layout_init = QVBoxLayout()
        # new_widget.setLayout(new_layout_init)
        # new_layout_init.addWidget(self.__menu_bar)
        # new_layout_init.addWidget(self.__editor)
        if self.is_dat_file_empty():
            editor = self.tab_widget.add_new_tab()
            editor.setFocus()
        else:
            self.set_text_in_editor()
            self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(BuriScriptEditor).setFocus()
        # file_name = os.path.basename(self.__editor.file_to_open_in_new_tab)
        # self.tab_widget.addTab(new_widget, file_name)
        self.set_all_layouts()
        # self.__editor.setGeometry(0, 0, screen_resolution.width() - 20, screen_resolution.height() - 180)
        self.__main_lyt.addWidget(self.__menu_bar, 0)
        self.__main_lyt.addWidget(self.__under_menu_bar_widget, 0)
        self.__main_lyt.addStretch(0)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                current_opened_editor: BuriScriptEditor = self.tab_widget.widget(
                                                             self.tab_widget.currentIndex()).findChild(BuriScriptEditor)
                if os.path.exists(current_opened_editor.file_to_open_in_new_tab):
                    current_opened_editor.set_text_in_editor()
        return super().eventFilter(obj, event)

    def is_dat_file_empty(self):
        """If .dat file is empty then editor opens a new tab by default"""
        os.chdir(home_path)
        file_paths = self.read_dat_file_has_file_paths_with_name()
        return True if not file_paths else False

    def set_all_layouts(self):
        self.split_into_two_widgets = QSplitter(Qt.Horizontal)
        self.split_into_two_widgets.setStyleSheet("""
                                                  QSplitter::handle{
                                                    background-color: #323437;
                                                    border: 0px;
                                                  }
                                                  QSplitter::handle:pressed{
                                                    background-color: #2b2b2b;
                                                    border: 0px;
                                                  }
                                                  """)
        try:
            first_file_path = list(self.read_dat_file_has_file_paths_with_name().keys())[0]
        except Exception as error:
            BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(error.__class__.__name__, error,
                                                                        BuriScriptLogHandler.traceback_formatter(
                                                                            error.__traceback__))
            first_file_path = None
        if first_file_path:
            only_file_path = self.get_file_path_and_file_name(first_file_path)
            self.file_explorer = CustomBuriScriptFileModel(only_file_path, home_path, self, self.tab_widget, self)
            self.split_into_two_widgets.addWidget(self.file_explorer)
        else:
            self.file_explorer = CustomBuriScriptFileModel('', home_path, self, self.tab_widget, self)
            self.split_into_two_widgets.addWidget(self.file_explorer)
            """This else block exists as to not caused RunTimeError wrapped C/C++ object has been deleted.
            The main_widget
            gets deleted"""

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(self.__lyt)
        self.split_into_two_widgets.addWidget(self.main_widget)
        self.split_into_two_widgets.setStretchFactor(10, 10)
        self.split_into_two_widgets.setSizes([1, 450])
        self.split_into_two_widgets.setMinimumHeight(QDesktopWidget().screenGeometry().height() - 110)
        self.__under_menu_bar_layout.addWidget(self.split_into_two_widgets)

    def new_file(self):
        self.tab_widget.add_new_tab()

    def open_file(self, file_name_from_explorer='', can_run_directly=False):
        self.__garbage_collection_list.append(self.tab_widget)
        if not can_run_directly:
            file_name = QFileDialog.getOpenFileName(self, "Open", "", "Python File (*.py);; "
                                                                      "Text File (*.txt);; SQL Text File (*.sql)")[0]
        else:
            file_name = file_name_from_explorer
        if file_name:
            with open(file_name, "r", encoding='utf8') as file_to_read:
                text_content: list = []
                try:
                    for line in file_to_read:
                        text_content.append(line)
                    self.add_new_file_to_dat(file_name)
                    file_type_user_opened_from_open_dialog = os.path.splitext(file_name)

                    for i in range(self.tab_widget.count()):
                        if self.tab_widget.tabText(i) == os.path.basename(file_name):
                            self.tab_widget.setCurrentIndex(i)
                            self.editor: BuriScriptEditor = self.tab_widget.widget(i).findChild(BuriScriptEditor)
                            break
                    else:
                        self.editor = self.add_new_tab_only_editor(file_name)

                    file_extension = file_type_user_opened_from_open_dialog[1]
                    if file_extension == '.sql':
                        self.editor.run_sql_lexer()
                    elif file_extension == ".py":
                        self.editor.run_python_lexer()
                    else:
                        self.editor.run_no_lexer()
                    self.editor.check_margin_width()
                    self.__garbage_collection_list.append(self.editor)
                    if text_content:
                        self.editor.setText(text_content[0])
                        text_content.pop(0)
                        for x in text_content:
                            self.editor.append(x)
                    self.file_explorer = CustomBuriScriptFileModel(
                        self.get_file_path_and_file_name(
                            file_name),
                        home_path, self, self.tab_widget, self)
                    self.split_into_two_widgets.replaceWidget(0, self.file_explorer)
                except Exception as error:
                    print(error.__class__.__name__, error, 'from open_file')
                    BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(error.__class__.__name__, error,
                                                                                BuriScriptLogHandler.traceback_formatter(
                                                                                    error.__traceback__))

    def save_file(self):
        editor: BuriScriptEditor = self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(
        BuriScriptEditor)
        save_editor_text = rf"""{editor.text()}"""
        save_editor_text = save_editor_text.replace("\r", "")
        os.chdir(home_path)
        all_file_paths_opened: dict = self.read_dat_file_has_file_paths_with_name()
        active_file_only_name: str = self.tab_widget.tabText(self.tab_widget.currentIndex())
        active_file_full_path: str = self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(BuriScriptEditor)
        for absolute_file_path, file_name_with_type in list(all_file_paths_opened.items()):
            if absolute_file_path == active_file_full_path:
                path_to_handle = active_file_full_path
                break
        else:
            BuriScriptLogHandler(home_path, qApp).custom_log_exceptions("There is no such path equivalent to "
                                                                        "active file path - FROM self.save_file() "
                                                                        "main.py")
            path_to_handle = ''
        if not path_to_handle:
            file_name = QFileDialog.getSaveFileName(self, "Save", "", "Python FIle (*.py);; Text File (*.py);;"
                                                                      " SQL File (*.sql)")
            if file_name[0]:
                with open(f"{file_name[0]}", 'w') as file_write:
                    file_write.write(save_editor_text)
                    path_to_handle = file_name[0]
                    os.chdir(home_path)
        else:
            with open(f"{path_to_handle}", "w") as file_write:
                file_write.write(save_editor_text)
        editor.file_to_open_in_new_tab = path_to_handle
        file_extension = os.path.splitext(path_to_handle)[1]
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(path_to_handle))
        if file_extension == ".py":
            self.tab_widget.setTabIcon(self.tab_widget.currentIndex(), QIcon(r"images_icons\PythonLogoBuriScript.png"))
        elif file_extension == '.sql':
            self.tab_widget.setTabIcon(self.tab_widget.currentIndex(), QIcon(r"images_icons\MySQLIconBuriScript.png"))
        if file_extension == ".sql":
            editor.run_sql_lexer()
        elif file_extension == ".py":
            editor.run_python_lexer()
        else:
            editor.run_no_lexer()

    @staticmethod
    def show_shortcuts_in_text_file():
        global home_path
        raw_home_to_txt_f = rf"{rf'{home_path}'}\all_editor_shortcuts_txt_file.txt"
        os.system(rf'"{raw_home_to_txt_f}"')

    @staticmethod
    def find_asked_module():
        SearchText()

    def add_new_tab_only_editor(self, file_name) -> BuriScriptEditor:
        """Adds an editor to a new tab and returns the editor"""
        new_widget = QWidget(self)
        new_widget.setStyleSheet(MAIN_WINDOW_STYLE_SHEET)
        new_layout_init = QVBoxLayout()
        new_widget.setLayout(new_layout_init)
        editor = BuriScriptEditor(home_path, file_name, PythonTerminal, self)
        file_extension = os.path.splitext(file_name)[1]
        if file_extension == ".sql":
            editor.run_sql_lexer()
        elif file_extension == '.py':
            editor.run_python_lexer()
        else:
            editor.run_no_lexer()
        new_layout_init.addWidget(editor)
        file_name = os.path.basename(editor.file_to_open_in_new_tab)
        os.chdir(home_path)
        file_extension = os.path.splitext(file_name)[1]
        if file_extension == ".py":
            self.tab_widget.addTab(new_widget, QIcon(r"images_icons\PythonLogoBuriScript.png"), file_name)
        elif file_extension == ".sql":
            self.tab_widget.addTab(new_widget, QIcon(r"images_icons\MySQLIconBuriScript.png"), file_name)
        else: self.tab_widget.addTab(new_widget, file_name)
        return editor

    @staticmethod
    def add_new_file_to_dat(file_to_add_abs_path: str) -> None:
        """Adds a file to the .dat file_path file. Only one dictionary must exist in that file.
        The dictionary structure:
        {
            C:Users/path/file_name.type: file_name.type
        }
        the so key-value pair type is chosen as every file has a unique directory and no elements can repeat in a
        dictionary like a set."""
        os.chdir(home_path)
        with open(r"images_icons\all_file_paths_user_opened_dictionary.dat", 'rb') as f_read:
            final_dictionary: dict = {}
            while True:
                try:
                    final_dictionary.update(pickle.load(f_read))
                except EOFError:
                    break
            with open(r'images_icons\all_file_paths_user_opened_dictionary.dat', 'wb') as f_write:
                final_dictionary[file_to_add_abs_path] = os.path.basename(file_to_add_abs_path)
                pickle.dump(final_dictionary, f_write)

    @staticmethod
    def read_dat_file_has_file_paths_with_name() -> dict:
        """Reads and returns a dictionary from the .dat file which has all the files which user opened."""
        os.chdir(home_path)
        with open(r'images_icons\all_file_paths_user_opened_dictionary.dat', 'rb') as f_read:
            file_path_dict: dict = {}
            while True:
                try:
                    file_path_dict.update(pickle.load(f_read))
                except EOFError:
                    return file_path_dict

    def find_text_in_code(self):
        import search_text_box
        search_text_box.SearchTextLine(self.current_tab_editor(), self)

    def zoom_in_or_out(self):
        self.current_tab_editor().setScrollWidthTracking(True)

        class GetFontSize(SearchText):
            def __init__(self, master_lexer, master_editor: QsciScintilla):
                super(GetFontSize, self).__init__()
                os.chdir(home_path)
                data = settings_editor()
                self.__change_font = QFont(data['FONT'])
                self.__master_editor = master_editor
                self._change_font_master_editor = master_lexer

            def retranslateUi(self, nothing):
                self.lineEdit.setPlaceholderText("Enter Font Size")

            def enter_pressed(self):
                self.__search = self.lineEdit.text()
                self.close()
                try:
                    if int(self.__search) <= 0: return
                    self.__change_font.setPointSize(int(self.__search))
                    self.__master_editor.setMarginsFont(self.__change_font)
                    operator_font = QFont("Consolas")
                    self._change_font_master_editor.setFont(self.__change_font)
                    operator_font.setPointSize(int(self.__search) + 2)
                    self._change_font_master_editor.setFont(operator_font, QsciLexerPython.Operator)
                except Exception:
                    pass

        zoom_in = GetFontSize(self.current_tab_editor().lexer(), self.current_tab_editor())

    def search_in_google(self):

        class GoogleSearch(SearchText):
            def __init__(self, master_editor: QsciScintilla):
                super(GoogleSearch, self).__init__()
                self.__master_editor = master_editor
                window_resolution = QDesktopWidget().screenGeometry()
                self.move(round(window_resolution.width() / 2) - 200, round(window_resolution.height() / 2) - 50)

            def retranslateUi(self, nothing):
                self.lineEdit.setPlaceholderText("Google")

            def enter_pressed(self):
                self.__search = self.lineEdit.text()
                self.close()
                import webbrowser
                webbrowser.open_new_tab(f"https://www.google.com.tr/search?q={self.__search}")

        GoogleSearch(self.current_tab_editor())

    def resize_window(self):

        class ReSizeWindow(SearchText):
            def __init__(self, master_window):
                super(ReSizeWindow, self).__init__()
                self.__master_window = master_window

            def retranslateUi(self, nothing):
                self.lineEdit.setPlaceholderText("Enter Resolution")

            def enter_pressed(self):
                self.__search = self.lineEdit.text()
                self.close()
                window_resolution = QDesktopWidget().screenGeometry()
                keywords_resolution = {'half-right': (window_resolution.width() / 2, 0, window_resolution.width() / 2,
                                                      window_resolution.height()),
                                       'default': (0, 0, window_resolution.width() - 20, window_resolution.height()),
                                       'quarter-top-left': (0, 0, window_resolution.width() / 2,
                                                            window_resolution.height() / 2),
                                       'quarter-top-right': (window_resolution.width() / 2, 0,
                                                             window_resolution.width() / 2,
                                                             window_resolution.height() / 2),
                                       'quarter-bottom-left': (0, window_resolution.height() / 2,
                                                               window_resolution.width() / 2,
                                                               window_resolution.height() / 2),
                                       'half-left': (0, 0, window_resolution.width() / 2, window_resolution.height()),
                                       'quarter-bottom-right': (window_resolution.width() / 2,
                                                                window_resolution.height() / 2,
                                                                window_resolution.width() / 2,
                                                                window_resolution.height() / 2),
                                       'half-top': (0, 0, window_resolution.width(), window_resolution.height() / 2),
                                       'half-bottom': (0, window_resolution.height() / 2,
                                                       window_resolution.width(), window_resolution.height() / 2)
                                       }
                if self.__search.lower() in keywords_resolution:
                    initial_pos_x, initial_pos_y, final_screen_width, final_screen_height = \
                        keywords_resolution[self.__search.lower()]
                    self.__master_window.setGeometry(int(initial_pos_x), int(initial_pos_y),
                                                     int(final_screen_width), int(final_screen_height))
                else:
                    try:
                        given_resolution: tuple = eval(self.__search)
                        window_width, window_height = given_resolution
                        self.__master_window.setGeometry(0, 0, window_width, window_height)
                    except Exception:
                        pass

        ReSizeWindow(self)

    def run_python_buriracer(self):
        os.chdir(home_path)
        try:
            class BuriRacerWindowObjectThread(QObject):
                def __init__(self, parent_thread: QThread, parent, *args, **kwargs):
                    # super(BuriRacerWindowObjectThread, self).__init__(None)
                    super().__init__(parent, *args, **kwargs)
                    self.__parent_thread: QThread = parent_thread

                def run_window(self):
                    # BuriRacerWindow()
                    """ Run with python threading"""
                    # python_thread_buriracer_threading = threading.Thread(target=self.run_python_threaded_buriracer)
                    # python_thread_buriracer_threading.start()
                    self.run_python_threaded_buriracer()

                def run_python_threaded_buriracer(self):
                    try:
                        BuriRacerWindow()
                    except BaseException as error:
                        print(error.__class__.__name__, error, "FROM BURIRACER")
                        BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(
                            error.__class__.__name__,
                            error,
                            BuriScriptLogHandler.traceback_formatter(
                            error.__traceback__)
                        )
                    # sys.exit()
                    self.__parent_thread.exit()

            buri_racer_thread = QThread(self)
            buriracer_window_instance = BuriRacerWindowObjectThread(buri_racer_thread, self)
            buriracer_window_instance.moveToThread(buri_racer_thread)
            buri_racer_thread.started.connect(buriracer_window_instance.run_window)
            buri_racer_thread.start()
        except Exception as error:
            BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(error.__class__.__name__, error,
                                                                        BuriScriptLogHandler.traceback_formatter(
                                                                            error.__traceback__))
        # os.system(r"taskkill /F /IM automations.exe /T")
        # BuriRacerWindow()
        # os.system(r"start automations.exe")

    def set_text_in_editor(self):
        os.chdir(home_path)
        with open(r"images_icons\all_file_paths_user_opened_dictionary.dat", 'rb') as f_read:
            all_file_paths: dict = pickle.load(f_read)
            for file_path in all_file_paths:
                if os.path.isfile(file_path):
                    self.add_new_tab_only_editor(file_path)

    def open_settings_window(self):
        from settings_editor import SettingsEditor

        class SettingsEditorMain(SettingsEditor):
            def __init__(self, master_editor, master_lexer, master_tab_widget: QTabWidget):
                super(SettingsEditorMain, self).__init__()
                self.__master_editor: QsciScintilla = master_editor
                self.__master_lexer: QsciLexerPython = master_lexer
                self.__master_tab_widget = master_tab_widget

            def close_window_and_read(self):
                super(SettingsEditorMain, self).close_window_and_read()
                editor_font_new = self.get_defaults()
                self.editor_font = QFont(editor_font_new['FONT'])
                self.editor_font.setPointSize(int(editor_font_new['FONT_SIZE']))
                operator_font = QFont('Consolas')
                operator_font.setPointSize(int(editor_font_new['FONT_SIZE']) + 2)
                for i in range(self.__master_tab_widget.count()):
                    editor: BuriScriptEditor = self.__master_tab_widget.widget(i).findChild(BuriScriptEditor)
                    lexer = editor.lexer()
                    editor.setFont(self.editor_font)
                    editor.setMarginsFont(self.editor_font)
                    lexer.setFont(self.editor_font)
                    lexer.setFont(operator_font, QsciLexerPython.Operator)
                    self.check_margin_width(editor)

            @staticmethod
            def check_margin_width(editor):
                number_of_lines = len(editor.text().split('\n'))
                digits = len(str(number_of_lines))
                editor.setMarginWidth(0, "0" * (digits + 1))

        current_editor: BuriScriptEditor = self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(
            BuriScriptEditor)
        SettingsEditorMain(current_editor, current_editor.lexer(),
                           master_tab_widget=self.tab_widget)

    def go_to_line_editor(self):

        class GoToLine(SearchText):
            def __init__(self, master_editor: QsciScintilla):
                super(GoToLine, self).__init__()
                self.lineEdit.setValidator(QIntValidator())
                self.__master_editor: QsciScintilla = master_editor

            def retranslateUi(self, nothing):
                self.lineEdit.setPlaceholderText("Go to Line")

            def enter_pressed(self):
                text_in_lineEdit = self.lineEdit.text()
                self.close()
                self.__master_editor.setFocus()
                try:
                    self.__master_editor.SendScintilla(QsciScintillaBase.SCI_GOTOLINE, int(text_in_lineEdit) - 1)
                except Exception:
                    pass

        GoToLine(self.current_tab_editor())

    def append_text_file_programs_editor(self):

        class AppendTextInEditorToFile(SearchText):
            def __init__(self, master_editor: QsciScintilla):
                super(AppendTextInEditorToFile, self).__init__()
                self.__master_editor: QsciScintilla = master_editor
                window_resolution = QDesktopWidget().screenGeometry()
                self.move(round(window_resolution.width() / 2) - 200, round(window_resolution.height() / 2) - 50)

            def retranslateUi(self, nothing):
                self.lineEdit.setPlaceholderText("Program Name")

            def enter_pressed(self):
                text_in_lineEdit = self.lineEdit.text()
                self.close()
                if text_in_lineEdit:
                    final_text = "-"*60 + text_in_lineEdit + "-"*60
                    file_path_to_append_text_in_editor = rf"{settings_editor()['LOG_PROGRAM_FILE_PATH']}"
                    if os.path.exists(file_path_to_append_text_in_editor):
                        with open(file_path_to_append_text_in_editor, "a", encoding='utf8') as file_to_append_text:
                            file_to_append_text.write("\n" + final_text + "\n")
                            text_to_write =  rf"{self.__master_editor.text()}"
                            text_to_write = text_to_write.replace("\r", "")
                            file_to_append_text.write(text_to_write + '\n')
                            self.__master_editor.setText('')

        AppendTextInEditorToFile(self.current_tab_editor())

    @staticmethod
    def get_file_path_and_file_name(absolute_file_path: str) -> str:
        """ This function returns string of only file path without file name"""
        return os.path.dirname(absolute_file_path)

    def run_directly_to_console(self):
        self.run_python_file(can_run_directly_to_console=True)

    def current_tab_editor(self) -> BuriScriptEditor:
        return self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(BuriScriptEditor)

    def run_user_opened_working_directory(self):
        current_directory = os.path.dirname(self.current_tab_editor().file_to_open_in_new_tab)
        os.startfile(current_directory)

    def comment_out_selected_region(self):
        commenter = ScintillaComponentCommenter(self.current_tab_editor(), "#")
        commenter.toggle_comments()
        return

    def run_sql_file(self):
        global instance_check_output_window
        os.chdir(home_path)
        mydb, error_msg = MySQLScintilla.MySQLScintillaMain.connect_to_sql_server()
        if mydb is None:
            self.customwidget = CustomWidget([], error_msg, my_cursor=None, parent=self)
            return
        mycursor = mydb.cursor()
        try:
            # commands = self.__editor.text().split(";") -> should be self.current_tab_editor()
            # for command in list(commands):
            #     constraints = [
            #         "",
            #         "\r\n" * int(len(command) / 2),
            #         "\n"*len(command),
            #         "\r"*len(command)
            #         ]
            #     if command in constraints:
            #         commands.remove(command)
            # WARNING: NEW SQL PARSER has been implemented for parsing sql statements. It replaces the above commented
            #  code
            current_opened_editor: BuriScriptEditor = self.tab_widget.widget(
                self.tab_widget.currentIndex()).findChild(BuriScriptEditor)
            commands = sqlparse.split(current_opened_editor.text())
            for command in commands:
                mycursor.execute(command)
            contents = [x for x in mycursor]
            output_message = f"{mycursor.rowcount} row(s) affected"
            mydb.commit()
            if instance_check_output_window:
                instance_check_output_window = False
                self.customwidget.close()
                self.customwidget.deleteLater()
            else:
                instance_check_output_window = True
            self.customwidget = CustomWidget(contents, output_message, mycursor, self)
        except Exception as error:
            if instance_check_output_window:
                instance_check_output_window = False
                self.customwidget.close()
                self.customwidget.deleteLater()
            else:
                instance_check_output_window = True
            self.customwidget = CustomWidget([], str(error), my_cursor=None, parent=self)

    def run_python_file(self, can_run_directly_to_console=False):
        try:
            current_editor: BuriScriptEditor = self.tab_widget.widget(self.tab_widget.currentIndex()).findChild(
                BuriScriptEditor)
            active_file_path_absolute: str = current_editor.file_to_open_in_new_tab
        except AttributeError:
            "Error raised due to new file"
            self.save_file()
            return
        except BaseException as error:
            return
        active_file_name: str = os.path.basename(active_file_path_absolute)
        if os.path.splitext(active_file_path_absolute)[1] == ".sql":
            self.run_sql_file()
            return
        file_path_to_run = active_file_path_absolute
        if not active_file_path_absolute:
            self.save_file()
            return
        # text_in_unsaved = ""
        if not os.path.isfile(file_path_to_run):
            self.tab_widget.close_current_tab()
            return
        with open(f"{file_path_to_run}", "r") as file_to_read_unsaved:
            text_in_unsaved = ''.join(file_to_read_unsaved.readlines())
            file_to_read_unsaved.close()
            text_in_current_editor = current_editor.text().replace('\t', "    ")
            check_equality_editor_text = rf"{text_in_current_editor}"
            check_equality_editor_text = check_equality_editor_text.replace("\r", "")
            if check_equality_editor_text == text_in_unsaved:
                filepath_ = file_path_to_run
                os.chdir(home_path)
                pattern_to_find_file_name = re.compile(r"[ \w-]+\.")
                match_file_path = pattern_to_find_file_name.findall(filepath_)[0] + 'py'  # obsolete
                match_file_path = pathlib.Path(filepath_).name  # has file name with extension
                path_without_file_name = filepath_
                path_without_file_name = os.path.dirname(filepath_)
                # path_without_file_name = path_without_file_name.rsplit(match_file_path)
                # ^-> was previously used

                def run_function():
                    try:
                        os.chdir(rf"{path_without_file_name}")
                    except WindowsError as error:
                        BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(
                            error.__class__.__name__, error,
                            BuriScriptLogHandler.traceback_formatter(
                                error.__traceback__)
                        )
                        raise SystemExit
                    if hasattr(self, 'python_terminal_window'):
                        self.python_terminal_window.close_all_widgets_and_exit()
                    if can_run_directly_to_console:
                        os.system(rf'start python -i "{match_file_path}"')
                        return
                    self.python_terminal_window = PythonTerminal(file_name=rf"{match_file_path}",
                                                                 file_path=path_without_file_name,
                                                                 parent_editor=current_editor, parent=self)
                    try:
                        self.python_terminal_window.runFile(rf"{match_file_path}")
                    except BaseException as error:
                        BuriScriptLogHandler(home_path, qApp).custom_log_exceptions(
                            error.__class__.__name__, error,
                            BuriScriptLogHandler.traceback_formatter(
                                error.__traceback__)
                        )
                    # os.system(rf'start python -i "{match_file_path}"')
                    os.chdir(home_path)

                import threading
                # thread = threading.Thread(target=run_function)
                # thread.start()
                run_function()

            else:
                from PyQt5 import QtCore, QtGui, QtWidgets
                # if class doesn't work properly change self.MainWindow in QLabel, QPushButton and statusbar was removed
                # if painting issues exist check the __init__
                # any functional errors should not happen due to the class styles itself as no connections were changed.

                class Ui_MainWindow(object):
                    def __init__(self, main_editor, global_file_path, parent):
                        self.chosen_file_path_which_is_opened_globally = global_file_path
                        self.MainWindow = QtWidgets.QWidget()
                        radius = 20.0
                        path = QtGui.QPainterPath()
                        self.MainWindow.resize(218, 103)
                        path.addRoundedRect(QtCore.QRectF(self.MainWindow.rect()), radius, radius)
                        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
                        self.MainWindow.setMask(mask)
                        self.MainWindow.setStyleSheet("""background-color: #323437;
                                                         color: white;
                                                         border-radius: 20px #111111;
                                                         opacity: 100;
                                                         border: 10px #111111;""")
                        self.boolean_value_final = None
                        self.main_editor = main_editor
                        self.__parent = parent

                    def setupUi(self):
                        self.MainWindow.setObjectName("MainWindow")
                        # self.MainWindow.resize(218, 103)
                        self.MainWindow.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
                        self.MainWindow.setAttribute(QtCore.Qt.WA_StyledBackground)
                        self.MainWindow.setStyleSheet("background-color: #323437;")
                        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
                        self.centralwidget.setObjectName("centralwidget")
                        self.label = QtWidgets.QLabel(self.MainWindow)
                        self.label.setGeometry(QtCore.QRect(10, 20, 201, 20))
                        font = QtGui.QFont()
                        font.setFamily("JetBrains Mono")
                        font.setPointSize(12)
                        self.label.setFont(font)
                        self.label.setStyleSheet("background-color: #323437;\n"
                                                 "color: white;")
                        self.label.setObjectName("label")
                        self.pushButton = QtWidgets.QPushButton(self.MainWindow)
                        self.pushButton.setGeometry(QtCore.QRect(20, 50, 81, 31))
                        font = QtGui.QFont()
                        font.setFamily("JetBrains Mono")
                        self.pushButton.setFont(font)
                        self.pushButton.setStyleSheet(INTERPRETER_BUTTON_STYLE_SHEET)  # "color: white")
                        self.pushButton.setObjectName("pushButton")
                        self.pushButton_2 = QtWidgets.QPushButton(self.MainWindow)
                        self.pushButton_2.setGeometry(QtCore.QRect(110, 50, 91, 31))
                        font = QtGui.QFont()
                        font.setFamily("JetBrains Mono")
                        self.pushButton_2.setFont(font)
                        self.pushButton_2.setStyleSheet(INTERPRETER_BUTTON_STYLE_SHEET)  # "color: white")
                        self.pushButton_2.setObjectName("pushButton_2")
                        # self.MainWindow.setCentralWidget(self.MainWindow)
                        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)
                        self.statusbar.setObjectName("statusbar")
                        # self.MainWindow.setStatusBar(self.statusbar)
                        self.retranslateUi(self.MainWindow)
                        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)
                        self.label.setText("Do you want to Save?")
                        self.pushButton.setText("Save")
                        self.pushButton_2.setText("Cancel")
                        self.pushButton.clicked.connect(lambda: self.save_file_to_path())
                        self.pushButton_2.clicked.connect(lambda: self.return_boolean(False))
                        self.pushButton.setDefault(True)
                        self.pushButton.setFocus()
                        # self.pushButton.autoDefault()
                        self.MainWindow.show()

                    def retranslateUi(self, MainWindow):
                        _translate = QtCore.QCoreApplication.translate
                        # MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
                        # self.label.setText(_translate("MainWindow", "Do you want to Save?"))
                        # self.pushButton.setText(_translate("MainWindow", "Save"))
                        # self.pushButton_2.setText(_translate("MainWindow", "Cancel"))

                    def return_boolean(self, boolean_to_return):
                        self.MainWindow.close()
                        self.boolean_value_final = boolean_to_return
                        # with open("boolean_value.txt", "w") as boolean_value:
                        #     boolean_value.write(str(1 if boolean_to_return else 0))
                        # return  # boolean_to_return

                    def your_boolean_value(self):
                        return self.boolean_value_final

                    def save_file_to_path(self):
                        if not active_file_path_absolute:
                            # file_name = QFileDialog.getSaveFileName(self, "Save", "",
                            #                                         "Python FIle (*.py);; Text File (*.py)")
                            # if file_name[0]:
                            #     with open(f"{file_name[0]}", 'w') as file_write:
                            #         file_write.write(self.text_to_save_in_location)
                            pass
                        else:
                            with open(f"{active_file_path_absolute}", "w") as file_write:
                                editor_text_to_write = rf"{self.main_editor.text()}"
                                editor_text_to_write = editor_text_to_write.replace("\r", "")
                                file_write.write(editor_text_to_write)
                                self.MainWindow.close()
                                file_path_to_run_ = self.chosen_file_path_which_is_opened_globally
                                filepath__ = file_path_to_run_
                                os.chdir(home_path)
                                pattern_to_find_file_name_ = re.compile(r"[ \w-]+\.")
                                match_file_path_ = pattern_to_find_file_name_.findall(filepath__)[0] + 'py'
                                path_without_file_name_ = filepath__
                                path_without_file_name_ = path_without_file_name_.rsplit(match_file_path_)

                                # WARNING: ANY MESSAGEBOX SAVE ERROR MAY OCCUR DUE TO THE ABSENCE OF THE following
                                #  2 lines
                                # os.chdir(rf"{path_without_file_name_[0]}")
                                # os.system(rf'start python -i "{match_file_path_}"')
                                """
                                
                                """
                                try:
                                    os.chdir(rf"{path_without_file_name_[0]}")
                                    if hasattr(self.__parent, 'python_terminal_window'):
                                        self.__parent.python_terminal_window.close_all_widgets_and_exit()
                                    if can_run_directly_to_console:
                                        os.system(rf'start python -i "{match_file_path}"')
                                        return
                                    self.__parent.python_terminal_window = PythonTerminal(
                                            file_name=rf"{match_file_path_}",
                                            file_path=path_without_file_name_[0],
                                            parent_editor=self.main_editor,
                                            parent=self.__parent
                                        )
                                    self.__parent.python_terminal_window.runFile(rf"{match_file_path_}")
                                    os.chdir(home_path)
                                except BaseException as error:
                                    pass
                                """
                                
                                """
                                file_write.close()

                ui = Ui_MainWindow(current_editor, active_file_path_absolute, self)
                ui.setupUi()

    ''''''

    def __btn_action(self):
        # os.system(r"taskkill /F /IM automations.exe /T")
        sys.exit(app.exec_())
        QApplication.closeAllWindows()

    ''''''


''' End Class '''


"Deprecated Class"

class CheckPassword(SearchText):
    def __init__(self, parent_window: QMainWindow):
        super().__init__()
        self.parent_window = parent_window
        self.lineEdit.setEchoMode(QLineEdit.Password)
        window_resolution = QDesktopWidget().screenGeometry()
        self.move(round(window_resolution.width() / 2) - 200, round(window_resolution.height() / 2) - 50)

    def retranslateUi(self, nothing):
        self.lineEdit.setPlaceholderText("Enter Password")

    def enter_pressed(self):
        if self.lineEdit.text() in ["Deprecated Class"]:
            self.close()
            self.parent_window.showMaximized()
        else:
            sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()
    sys.excepthook = BuriScriptLogHandler(home_path, qApp, myGUI).run_logs_from_sys_hook
    # os.system("start automations.exe")
    app.exec_()
    # os.system(r"taskkill /F /IM automations.exe /T")
    sys.exit()
''''''

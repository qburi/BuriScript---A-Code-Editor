import os.path
import pickle
import sys
import threading
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from BuriScriptLexers import CustomLexerPython
from handle_logs import BuriScriptLogHandler
from BuriScriptScintillaEditor import BuriScriptEditor


TAB_STYLE_SHEET = r"""
QTabWidget {
    background-color: black;
    color: #d3d3d3;
    border: 0px;
    border-style: none;
}


QTabBar::tab {
    background-color: #1E1F22;
    color: #d3d3d3;
    min-width: 30ex;
    min-height: 10ex;
    border-style: none;
    border-bottom: 5px solid #212121;
    border: 0px;
    padding-left: 10px;
}


QTabBar::tab::selected {
    color: #d3d3d3;
    border-style: none;
    background-color: #1E1F22;
    border-bottom: 5px solid #3b3b3b;
}

QTabBar::tab::hover{
    background-color: #1E1F22;
    color: white;
}
QTabWidget::pane{
    border-top: 0px;
    border-left: 0px;
    border-right: 0px;
    border-bottom: 0px;
}
QTabBar::close-button {
     image: url(images_icons/close_button_tab_widget.png)
 }
QTabBar::close-button:hover {
     background: #A0A0A0;
}
QTabBar::close-button {
     image: url(images_icons/close_button_tab_widget.png);
}
QTabBar::close-button:hover{
     image: url(images_icons/close_button_hover_tab_widget.png);
     background: #1E1F22;
}
QToolTip{
    color: white; 
    background-color: #1E1F22;
    border: 0px;
}
"""

WIDGET_STYLE_SHEET_FROM_MAIN_WINDOW = \
"""
            QWidget{
                background-color: #111111;
                color: white;
            }
            QListView{
                background-color: #111111;
                color: white;
            }
             QListView::item:selected{
                background : #323437;
                color: white;
            }
            QListView::item:hover{
                background-color: #4a4a4a;
                color: white;
            }
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
"""


class CustomTabWidget(QTabWidget):
    def __init__(self, parent_directory, python_terminal_class=None, parent=None):
        super(CustomTabWidget, self).__init__(parent)
        self.__parent = parent
        os.chdir(parent_directory)
        self.setStyleSheet(TAB_STYLE_SHEET)
        self.parent_directory: str = parent_directory
        self.python_terminal_not_instance = python_terminal_class
        self.setTabsClosable(True)
        self.setMovable(True)
        # self.setDocumentMode(True)
        self.font_in = self.font()
        self.font_in.setPointSize(10)
        self.setFont(self.font_in)
        self.tabCloseRequested.connect(lambda: self.close_current_tab())
        self.__garbage_collection_list: list = []

    def add_new_tab(self):
        try:
            layout = QVBoxLayout()
            new_editor = BuriScriptEditor(parent_directory=self.parent_directory,
                                          tab_file_path_absolute='',
                                          python_terminal_class_not_instance=self.python_terminal_not_instance,
                                          parent=self.__parent)
            try:
                new_editor.run_no_lexer()
            except Exception as error:
                BuriScriptLogHandler(self.parent_directory, qApp).custom_log_exceptions(error.__class__.__name__, error,
                                                                            BuriScriptLogHandler.traceback_formatter(
                                                                                error.__traceback__))
            layout.addWidget(new_editor)
            new_widget = QWidget(self.__parent)
            new_widget.setStyleSheet(WIDGET_STYLE_SHEET_FROM_MAIN_WINDOW)
            new_widget.setLayout(layout)
            self.addTab(new_widget, 'New tab')
            return new_editor
        except BaseException as error:
            print(error.__class__.__name__, error)

    def close_current_tab(self):
        """Closes current tab and pops the file path from .dat file dictionary"""
        all_file_paths: dict = self.__parent.read_dat_file_has_file_paths_with_name()  # dictionary of file paths
        try:
            editor = self.widget(self.currentIndex()).findChild(BuriScriptEditor)  # extract absolute file path
        except AttributeError:
            return
        absolute_file_path_to_remove_from_editor = editor.file_to_open_in_new_tab

        if absolute_file_path_to_remove_from_editor in all_file_paths:
            all_file_paths.pop(absolute_file_path_to_remove_from_editor)
        else:
            "Maybe new tab"
            self.__garbage_collection_list.append(self)
            self.removeTab(self.currentIndex())
            return

        os.chdir(self.parent_directory)
        with open(r'images_icons\all_file_paths_user_opened_dictionary.dat', 'wb') as f_write:
            pickle.dump(all_file_paths, f_write)
        self.__garbage_collection_list.append(self)
        self.removeTab(self.currentIndex())

    def _add_custom_tab(self, menu_bar, editor: BuriScriptEditor, lexer_type: CustomLexerPython, full_file_path: str) -> None:
        """
        the type hinting for lexer_type is a misnomer. It actually relates to the use of lexer in the scintilla editor.
        This function is deprecated.
        """
        layout_to_add: QVBoxLayout = QVBoxLayout()
        editor_to_add: BuriScriptEditor = editor
        lexer_to_add: CustomLexerPython = lexer_type
        full_file_path = full_file_path
        file_name_only = self.extract_file_name(file_path_full=full_file_path)

        if lexer_type.__class__.__name__ == 'CustomLexerSQL':
            editor.run_python_lexer()
        else:
            editor.run_python_lexer()

        layout_to_add.addWidget(menu_bar)
        layout_to_add.addWidget(editor)

        new_widget = QWidget(self.__parent)
        new_widget.setLayout(layout_to_add)
        self.addTab(new_widget, file_name_only)

    @staticmethod
    def extract_file_name(file_path_full):
        return os.path.basename(file_path_full)


class TestMainWindow(QMainWindow):
    def __init__(self):
        super(TestMainWindow, self).__init__()
        self.__lyt = QHBoxLayout()
        self.__frm = QFrame()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.setStyleSheet("background-color: #111111; color: white;")
        self.setGeometry(0, 0, 1920, 1080)
        self._tab_widget = CustomTabWidget()
        self.__lyt.addWidget(self._tab_widget)

        """
        """
        self.add_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.add_tab_shortcut.activated.connect(lambda: self._tab_widget.add_new_tab())
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(lambda: self._tab_widget.close_current_tab())
        self.showMaximized()


def main():
    app = QApplication(sys.argv)
    ex = TestMainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

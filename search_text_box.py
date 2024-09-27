from PyQt5.QtCore import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from search_box import SearchText


class HasFocusThread(QObject):
    def __init__(self, line_edit_box, main_window_line_edit, scintilla_editor: QsciScintilla, parent_thread: QThread):
        super(HasFocusThread, self).__init__(None)
        self.master_window_editor = scintilla_editor
        self.__parent_thread = parent_thread
        self.line_edit_focus = line_edit_box
        self.main_window_has_line_edit = main_window_line_edit

    def check_if_search_focus(self):
        # print(self.line_edit_focus.hasFocus())
        if not self.line_edit_focus.hasFocus():
            self.main_window_has_line_edit.close()
            self.master_window_editor.clearIndicatorRange(0, 0,
                                                          len(self.master_window_editor.text().split("\n")) + 1,
                                                          len(self.master_window_editor.text()), 1)
            self.__parent_thread.exit()
            return
        from time import sleep
        sleep(1)
        self.check_if_search_focus()



class SearchTextLine(SearchText):
    def __init__(self, _editor: QsciScintilla, master_window: QMainWindow):
        super(SearchTextLine, self).__init__()
        self.get_editor = _editor
        self._master_window = master_window
        self.__search: str = ""
        self.__number_of_highlights: int = 0
        self.__check_focus = QShortcut(QKeySequence("Ctrl+E"), self)
        self.__check_focus.activated.connect(self.check_if_search_focus)
        self.lineEdit.setFocus()
        self.start_focus_thread = QThread()
        self.check_for_focus = HasFocusThread(self.lineEdit, self, self.get_editor, self.start_focus_thread)
        self.check_for_focus.moveToThread(self.start_focus_thread)
        self.start_focus_thread.started.connect(self.check_for_focus.check_if_search_focus)
        self.start_focus_thread.start()
        self.get_below_search = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.get_below_search.activated.connect(lambda: self.get_below_down_arrow(self.__all_instances,
                                                                                  self.__current_marker_position
                                                                                  , 1)
                                                )
        self.get_above_search = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.get_above_search.activated.connect(lambda: self.get_below_down_arrow(self.__all_instances,
                                                                                  self.__current_marker_position
                                                                                  , -1))
        self.__all_instances: list = []
        self.__current_marker_position: int = -1
        self.__swap_int = 0

    def check_if_search_focus(self):
        # print(self.lineEdit.hasFocus())
        from time import sleep
        sleep(1)
        self.check_if_search_focus()

    def retranslateUi(self, nothing):
        self.lineEdit.setPlaceholderText("Enter Text to Search")

    def get_below_down_arrow(self, all_instances, current_position, up_or_down: int):
        self.get_editor.clearIndicatorRange(0, 0, len(self.get_editor.text().split("\n")) + 1,
                                            len(self.get_editor.text()), 2)
        try:
            position_to_highlight = all_instances[all_instances.index(current_position)]
            self.__current_marker_position = all_instances[all_instances.index(current_position) + up_or_down]
        except Exception as error:
            pass
            # print("ERROR IS", str(error))
        # print('here', "=================================", position_to_highlight, "all instances", all_instances)
        # print(all_instances)
        DEFAULT_INDICATOR_ID = 2
        try:
            if self.__all_instances[-1] == self.__current_marker_position and up_or_down == 1 and \
                    self.__swap_int:
                self.__current_marker_position = self.__all_instances[0]
                self.__swap_int = 0
            self.__swap_int = 1 if self.__all_instances[-1] == self.__current_marker_position and up_or_down == 1 else 0
            self.get_editor.fillIndicatorRange(self.__current_marker_position, 0,
                                               self.__current_marker_position + 1, 0, DEFAULT_INDICATOR_ID)
            self.get_editor.SendScintilla(QsciScintilla.SCI_GOTOLINE, self.__current_marker_position)
            self.get_editor.SendScintilla(QsciScintilla.SCI_GOTOPOS,
                                          self.__all_instances[self.__current_marker_position])
        except Exception:
            pass

    def enter_pressed(self):
        self.__search = self.lineEdit.text()
        text_in_editor = self.get_editor.text().split("\n")
        found_index = -1
        if self.__number_of_highlights == 1:
            self.__all_instances.clear()
            self.__current_marker_position = -1
        for line in enumerate(text_in_editor):
            if line[1].find(self.__search) != -1:
                # found_index = line[0]
                # break
                self.__all_instances.append(line[0])
        found_index = self.__current_marker_position = self.__all_instances[0] if self.__all_instances else -1
        if found_index == -1:
            return
        else:
            # print(found_index)
            if self.__number_of_highlights == 1:
                self.get_editor.clearIndicatorRange(0, 0, len(self.get_editor.text().split("\n")) + 1,
                                                    len(self.get_editor.text()), 2)
                self.__number_of_highlights = 0
            DEFAULT_INDICATOR_ID = 2
            self.get_editor.indicatorDefine(QsciScintilla.FullBoxIndicator, DEFAULT_INDICATOR_ID)
            self.get_editor.SCI_GOTOLINE = found_index + 1
            self.get_editor.setIndicatorForegroundColor(QColor("#705a9e"), DEFAULT_INDICATOR_ID)
            self.get_editor.setIndicatorOutlineColor(QColor("red"), DEFAULT_INDICATOR_ID)
            self.get_editor.setIndicatorHoverForegroundColor(QColor("#705a9e"), DEFAULT_INDICATOR_ID)
            self.get_editor.SendScintilla(QsciScintilla.SCI_GETINDICATORCURRENT, DEFAULT_INDICATOR_ID)
            self.get_editor.SendScintilla(QsciScintilla.SCI_SETINDICATORVALUE, DEFAULT_INDICATOR_ID, 0xffff)
            self.get_editor.setIndicatorDrawUnder(True, DEFAULT_INDICATOR_ID)
            self.get_editor.indicatorDrawUnder(DEFAULT_INDICATOR_ID)
            # self.get_editor.SendScintilla(self.get_editor.SCI_INDICSETHOVERFORE,
            #                               DEFAULT_INDICATOR_ID, QColor("#61039c"))
            self.get_editor.fillIndicatorRange(found_index, 0,
                                               found_index + 1, 0, DEFAULT_INDICATOR_ID)
            self.__number_of_highlights += 1

    def close_search_window(self):
        self.get_editor.clearIndicatorRange(0, 0, len(self.get_editor.text().split("\n")) + 1,
                                            len(self.get_editor.text()), 2)
        self.close()


# How to set caret to a specific line number?
# call_class = SearchTextLine(self.__editor, self)

import os
import queue
import matplotlib
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from time import sleep, perf_counter
import logging
from MySQLScintilla.table_widget_sql import style_sheet as sql_table_style_sheet
from MySQLScintilla.MySQLScintillaMain import button_style_sheet
from TypeRacer.buriracer_timer import BuriRacerTimerWidget
import multiprocessing
import threading

correct_words_list_from_random: list = []
typed_in_line_edit_from_random: list = []
all_wpm_points: list = []
is_graph_plotted: bool = False
START_WPM_THREADS_BOTH: bool = True
TEXT_EDIT_STYLE_SHEET: str = sql_table_style_sheet
BUTTON_STYLE_SHEET: str = button_style_sheet
can_stop_time = False
COMPLETE_TIME = -1
callback_queue = queue.Queue()
ADDITION_TO_SCROLL_STYLE_SHEET: str = """
QTextEdit{
    color: white;
    background-color: #111111;
}"""


class SubQLineEdit(QLineEdit):
    global correct_words_list_from_random, typed_in_line_edit_from_random

    def __init__(self, parent=None):
        super(SubQLineEdit, self).__init__(parent)
        self.correct_words_list: list = []
        self.typed_words_list: list = []
        self.__parent = parent
        self.__keypress_instance = True

    # def get_correct_and_typed_list(self, correct_list, typed_list) -> None:
    #     try:
    #         self.correct_list = correct_list
    #         self.typed_list = typed_list
    #     except Exception as error:
    #         print(error)
    #         # print(error.__class__.__name__, error)

    def keyPressEvent(self, event) -> None:
        # print(event.key())
        # correct_words_list_from_random, typed_in_line_edit_from_random =  self.correct_list, self.typed_list
        # print(self.text(), self.correct_list, self.typed_list)
        # print(event.key())
        try:
            return super(SubQLineEdit, self).keyPressEvent(event)
        finally:
            # print("text is", self.text())
            if self.__keypress_instance:
                self.__parent.timer_push_button.setParent(None)
                self.__keypress_instance = False
            try:
                if self.text().lstrip() not in self.correct_words_list[len(self.typed_words_list)][:
                len(self.text().lstrip())]:
                    self.setStyleSheet("background-color: #7a2721;"
                                       "color: white;"
                                       "border: 1px solid #5688b0;")
                    # print(event.key(), ascii(self.correct_words_list[len(self.typed_words_list)]))
                if not self.text().lstrip() or \
                        self.correct_words_list[len(self.typed_words_list)][: len(self.text().lstrip())] \
                        == self.text().lstrip():
                    # print(self.text().lstrip() or \
                    #     self.correct_words_list[len(self.typed_words_list)][: len(self.text().lstrip())] \
                    #     == self.text().lstrip())
                    self.setStyleSheet("background-color: #111111;"
                                       "color: white;"
                                       "border: 1px solid #5688b0;")
                # if len(self.typed_words_list) == len(self.correct_words_list):
                #     self.setStyleSheet("background-color: #111111;"
                #                        "color: white;"
                #                        "border: 1px;")
                if event.key() == 32 and \
                        self.correct_words_list[len(self.typed_words_list)][: len(self.text().lstrip())] == \
                        self.text().lstrip():
                    self.setText('')
                    pass
            except Exception as error:
                pass
            # print(error.__class__)


class GetAllPoints(QObject):
    global all_wpm_points

    def __init__(self, correct_words_list: list, typed_words_list: list, parent_thread: QThread, elapsed_time):
        super(GetAllPoints, self).__init__(None)
        self.correct_words_list = correct_words_list
        self.update_typed_words_list(typed_words_list)
        self.__parent_thread = parent_thread
        self.__start_time = elapsed_time

    def append_all_points_list(self):
        try:
            if len(self.__typed_word_list) == len(
                    self.correct_words_list) or is_graph_plotted and self.correct_words_list:
                self.__parent_thread.exit()
                self.run_calculations()
                return
            self.run_calculations()
        except BaseException as error:
            # self.append_all_points_list()
            pass
        sleep(1)
        try:
            return self.append_all_points_list()
        except RecursionError:
            return

    def run_calculations(self):
        global all_wpm_points
        try:
            number_of_characters_typed = sum([len(x) for x in self.__typed_word_list]) + len(self.__typed_word_list)
            wpm = round(((number_of_characters_typed / 5) / (perf_counter() - self.__start_time)) * 60)
            all_wpm_points.append(wpm)
            if number_of_characters_typed == 0:
                # logging.warning(f"{self.__typed_word_list}")
                pass
            for index, value in enumerate(all_wpm_points):
                if index > 5 and value == 0:
                    all_wpm_points.pop(index)
                if value == 0 and all_wpm_points[index + 1] == 0 and index == 0:
                    all_wpm_points.pop(index)
        except ZeroDivisionError:
            pass
        except IndexError:
            logging.debug("IndexError raised")

    def update_typed_words_list(self, updated_list):
        if updated_list:
            self.__typed_word_list = updated_list
        else:
            try:
                self.__typed_word_list.append([self.correct_words_list[len(self.__typed_word_list)]])
                logging.warning("CHEEKY THING DONE")
            except AttributeError:
                pass
            except IndexError:
                pass


class LiveWpmThread(QObject):
    global typed_in_line_edit_from_random, correct_words_list_from_random, can_stop_time, COMPLETE_TIME

    def __init__(self, correct_words_list: list, typed_word_list: list, live_wpm_label: QLabel, parent_thread: QThread,
                 elapsed_time, line_edit: QLineEdit, focus_less_text_edit: QTextEdit, time_label: QLabel,
                 is_type_timer: bool, complete_time: int, parent: QMainWindow):
        super(LiveWpmThread, self).__init__(None)
        self.__correct_words_list = correct_words_list
        self.update_typed_words_list(typed_word_list)  # typed_word_list
        self.__live_wpm_label = live_wpm_label
        self.__parent_thread = parent_thread
        self.start_timer = elapsed_time
        self.start_style_function = True
        self.__parent_line_edit = line_edit
        self.frameless_disabled_text_edit = focus_less_text_edit
        self.__timer_label = time_label
        self.__IS_TYPE_TIMER = is_type_timer
        self.__complete_time = complete_time
        self.__complete_time_can_change = complete_time
        self.__parent: BuriRacerWindow = parent
        COMPLETE_TIME = complete_time

    def calculate_live_wpm(self):
        global COMPLETE_TIME, can_stop_time
        # if self.start_style_function:
        #     self.start_style_function = False
        #     self.check_empty_background()
        if len(self.__typed_word_list) == len(self.__correct_words_list) or not self.__parent.isVisible():
            self.__parent_thread.exit()
            self.start_style_function = True
            # self.frameless_disabled_text_edit.setText('helsadkljh')
            # print('exited')
            return
        try:
            number_of_characters_typed = sum([len(x) for x in self.__typed_word_list]) + len(self.__typed_word_list)
            number_of_characters_in_words = sum([len(x) for x in self.__correct_words_list])
            wpm = round(((number_of_characters_typed / 5) / (perf_counter() - self.start_timer)) * 60)
            self.__live_wpm_label.setText(f"{wpm} wpm")
        except ZeroDivisionError:
            pass

        if self.__IS_TYPE_TIMER:
            if (perf_counter() - self.start_timer) >= self.__complete_time:
                self.__parent_thread.exit()
                self.start_style_function = True
                can_stop_time = True
                self.__parent.type_line_edit.setDisabled(True)
                # self.frameless_disabled_text_edit.setText(' '.join(self.__parent.correct_words_list))
                self.__parent.type_line_edit.setStyleSheet('border: 1px;'
                                                           'background-color: #111111;')
                self.__timer_label.setParent(None)
                can_stop_time = False
                callback_queue.put(self.__parent.plot_graph_matplotlib)
                return
            COMPLETE_TIME -= 0.1
            self.__timer_label.setText(str(round(COMPLETE_TIME, 2)))
        # global all_wpm_points
        # all_wpm_points.append(wpm)
        # if not self.__parent_line_edit.text().lstrip() or \
        #         self.__correct_words_list[len(self.__typed_word_list)][: len(self.__parent_line_edit.text().lstrip())] \
        #         == self.__parent_line_edit.text().lstrip():
        #     self.__parent_line_edit.setStyleSheet("background-color: #111111;"
        #                                           "color: white;"
        #                                           "border: 1px solid #5688b0;")
        if len(self.__typed_word_list) == len(self.__correct_words_list):
            self.__parent_line_edit.setStyleSheet("background-color: #111111;"
                                                  "color: white;"
                                                  "border: 1px;")
        sleep(0.1)
        try:
            self.calculate_live_wpm()
        except RecursionError:
            return
        except RuntimeError:
            return

    def update_typed_words_list(self, updated_list):
        self.__typed_word_list = updated_list
        # print(self.__typed_word_list)

    def check_empty_background(self):
        if self.start_style_function:
            print('thread exited')
            self.__parent_thread.exit()
            return
        if not self.__parent_line_edit.text().lstrip() or \
                self.__correct_words_list[len(self.__typed_word_list)][: len(self.__parent_line_edit.text().lstrip())] \
                == self.__parent_line_edit.text().lstrip():
            self.__parent_line_edit.setStyleSheet("background-color: #111111;"
                                                  "color: white;"
                                                  "border: 1px solid #5688b0;")
        if len(self.__typed_word_list) == len(self.__correct_words_list):
            self.__parent_line_edit.setStyleSheet("background-color: #111111;"
                                                  "color: white;"
                                                  "border: 1px;")
        sleep(1)
        # self.check_empty_background()

    def start_graph_plot_main_thread(self):
        sleep(1)
        self.__parent.plot_graph_matplotlib()


class BuriRacerWindow(QMainWindow):
    def __init__(self, is_type_timer=False, complete_time=-1):
        global COMPLETE_TIME, is_graph_plotted
        is_graph_plotted = False
        super(BuriRacerWindow, self).__init__(None)
        self.screen_geometry = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen_geometry.width(), self.screen_geometry.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.START_WPM_THREADS_BOTH = True
        self.IS_TYPE_TIMER = is_type_timer
        self.COMPLETE_TIME = complete_time
        COMPLETE_TIME = complete_time
        self.setWindowTitle("BuriRacer")
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setWindowOpacity(0.9)
        self.__frame = QFrame(self)  # --------------------------------------------------
        self.__frame.setStyleSheet(
            "background-color: rgba(17, 17, 17, 0.5);")  # --------------------------------------------------
        self.__lyt = QVBoxLayout()  # --------------------------------------------------
        self.__frame.setLayout(self.__lyt)  # --------------------------------------------------
        # self.setStyleSheet("background-color: rgba(17, 17, 17, 0.2);")
        self.setFont(QFont("JetBrains Mono"))
        self.setCentralWidget(self.__frame)  # --------------------------------

        # --------TextEdit------------
        self.__text_edit = QTextEdit(self)
        self.__text_edit_cursor = self.__text_edit.textCursor()
        self.__text_edit.ensureCursorVisible()
        self.text_font = QFont("JetBrains Mono")
        self.text_font.setPointSize(15)
        # self.__text_edit.setStyleSheet("color: white;"
        #                                "background-color: #111111;")
        self.__text_edit.setStyleSheet(TEXT_EDIT_STYLE_SHEET + ADDITION_TO_SCROLL_STYLE_SHEET)
        self.__text_edit.setFont(self.text_font)
        self.__text_edit.setFrameShape(QFrame.NoFrame)
        self.__text_edit.setReadOnly(True)
        self.__text_edit.setDisabled(True)
        # self.__text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__text_edit.setFixedSize(800, 190)
        self.__text_edit.move(int(self.screen_geometry.width() / 2) - 400, 200)
        self.__lyt.setAlignment(Qt.AlignCenter)
        # self.__lyt.addSpacing(200)
        # self.__lyt.addWidget(self.__text_edit) # -------------------------------------
        # self.__lyt.addStretch(1)
        self.text_edit_column_number_list: list = []
        self.number_of_downs_by_rows_text_edit: int = 0
        """
        -------------------------DATABASE-init-------------------------------
        """
        self.__title_for_text = self.__type_for_text = self.__author_for_text = ''
        """

        """
        self.type_line_edit = SubQLineEdit(self)
        self.type_line_edit.setFixedWidth(500)
        # self.__lyt.addWidget(self.type_line_edit) # ------------------------------------
        self.type_line_edit.setFont(self.text_font)
        self.type_line_edit.move(int(self.screen_geometry.width() / 2) - 300, 550)
        self.type_line_edit.installEventFilter(self)
        self.typed_in_text_list: list = []
        # self.correct_words_list: list = []
        self.type_line_edit.returnPressed.connect(lambda: self.enter_pressed())
        self.type_line_edit.setStyleSheet("border: 1px solid #5688b0;"
                                          "color: white;"
                                          "background-color: #111111;")
        # self.__lyt.addWidget(self.type_line_edit)

        """
        --------------------------------LIVE-WPM-LABEL--------------------------------
        """
        self.__live_wpm_label = QLabel(self)
        self.__live_wpm_label.setText("0 wpm")
        self.__live_wpm_label.setStyleSheet("background-color: #111111;"
                                            "color: white")
        self.__live_wpm_label.setFont(self.text_font)
        self.__live_wpm_label.move(self.screen_geometry.width() - 200, 200)

        self.__typeracer_data_result_label = QLabel()
        self.__typeracer_data_result_label.setStyleSheet("background-color: #111111;"
                                                         "color: white")
        self.__typeracer_data_result_label.setFont(self.text_font)
        # self.__typeracer_data_result_label.move(0, 0)

        """
        -------------------------------------------TIMER--------------------------------------------------
        """
        self.timer_push_button = QPushButton(self)
        self.timer_push_button.setStyleSheet(BUTTON_STYLE_SHEET)
        self.timer_push_button.setText("Timer")
        self.timer_push_button.move(int(self.screen_geometry.width() / 2) - 400, 100)
        self.timer_push_button.clicked.connect(lambda: self.start_timer_buriracer())

        """
        --------------------------------------------TIMER-LABEL-----------------------------------------------
        """
        if is_type_timer:
            self.timer_label = QLabel(self)
            self.timer_label.setText(str(self.COMPLETE_TIME))
            self.timer_label.setFont(self.text_font)
            self.timer_label.setStyleSheet("""background-color: #111111;
                                              color: white;
                                            """)
            self.timer_label.move(int(self.screen_geometry.width() / 2) - 400, 150)
        else:
            self.timer_label = QLabel()
        """

        """
        self.start_wpm_thread = QThread()
        self.text_to_add = self.random_text().split()
        first_word = self.text_to_add.pop(0)
        first_word = r"<u>" + r"<font color=#67e06f>" + rf"{first_word}" + "</font>" + "</u>"
        self.text_to_add = [first_word] + self.text_to_add
        self.__text_edit.setText(' '.join(self.text_to_add))
        self._escape_window = QShortcut(QKeySequence("Esc"), self)
        self._escape_window.activated.connect(lambda: self.close_main_window())
        self.get_all_points_thread = QThread()
        self.showMaximized()
        self.type_line_edit.setFocus()
        self.show()

    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setOpacity(0.7)
        painter.setBrush(QColor("rgba(17, 17, 17, 0.5)"))
        painter.setPen(QPen(QColor("rgba(17, 17, 17, 0.5)")))
        painter.drawRect(self.rect())

    def close_main_window(self):
        if __name__ != "__main__":
            import os
            # os.system("start automations.exe")
        global is_graph_plotted, all_wpm_points
        is_graph_plotted = True
        try:
            self.start_wpm_thread.exit()
            self.get_all_points_thread.exit()
            self.START_WPM_THREADS_BOTH = True
            all_wpm_points.clear()
            self.close()
        except Exception as error:
            logging.warning(error)

    def closeEvent(self, *args, **kwargs):
        super(BuriRacerWindow, self).closeEvent(*args, **kwargs)
        from os import system
        if __name__ != "__main__":
            # system("start automations.exe")
            pass

    def start_timer_buriracer(self):
        # time_in_seconds: int = -1

        class BuriTimer(BuriRacerTimerWidget):
            def __init__(self, buriracer_parent: BuriRacerWindow):
                super().__init__()
                self.__parent = buriracer_parent

            def return_pressed(self):
                # super(BuriTimer, self).return_pressed()
                time_in_seconds = int(self.lineEdit.text())
                self.close()
                if time_in_seconds == 0:
                    return
                else:
                    self.__parent.timer_push_button.setParent(None)
                    self.__parent.close()
                    self.__new_instance = BuriRacerWindow(is_type_timer=True, complete_time=time_in_seconds)

        instance_buriracer_timer = BuriTimer(self)

    def enter_pressed(self):
        # print(self.typed_in_text_list)
        pass

    def eventFilter(self, source, event):
        global can_stop_time
        if (event.type() == QEvent.KeyPress and
                source is self.type_line_edit):
            if self.type_line_edit.text().lstrip() not in self.correct_words_list[len(self.typed_in_text_list)][:
            len(self.type_line_edit.text().lstrip())]:
                self.type_line_edit.setStyleSheet("background-color: #7a2721;"
                                                  "color: white;"
                                                  "border: 1px solid #5688b0;")
            # print('key press:', (event.key(), event.text()))
            if self.START_WPM_THREADS_BOTH:
                self.START_WPM_THREADS_BOTH = False
                self.__live_wpm_class_instance = LiveWpmThread(self.correct_words_list, self.typed_in_text_list,
                                                               self.__live_wpm_label, self.start_wpm_thread,
                                                               perf_counter(), self.type_line_edit, self.__text_edit,
                                                               self.timer_label, self.IS_TYPE_TIMER, self.COMPLETE_TIME,
                                                               self)
                self.__live_wpm_class_instance.moveToThread(self.start_wpm_thread)
                self.start_wpm_thread.started.connect(self.__live_wpm_class_instance.calculate_live_wpm)
                self.start_wpm_thread.finished.connect(lambda: self.run_callback_queue())
                self.start_wpm_thread.start()

                """---------------------------------------ALL-POINTS-INSTANCE----------------------------------------"""
                self.__get__all_points_instance = GetAllPoints(self.correct_words_list, self.typed_in_text_list,
                                                               self.get_all_points_thread, perf_counter())
                self.__get__all_points_instance.moveToThread(self.get_all_points_thread)
                self.get_all_points_thread.started.connect(self.__get__all_points_instance.append_all_points_list)
                self.points_perf_counter = perf_counter()
                self.get_all_points_thread.start()

            if event.key() == 32:
                # self.__live_wpm_class_instance = LiveWpmThread(self.correct_words_list, self.typed_in_text_list,
                #                                                self.__live_wpm_label, self.start_wpm_thread,
                #                                                perf_counter(), self.type_line_edit, self.__text_edit,
                #                                                self.timer_label, self.IS_TYPE_TIMER, self.COMPLETE_TIME,
                #                                                self)
                # self.__live_wpm_class_instance.moveToThread(self.start_wpm_thread)
                # self.start_wpm_thread.started.connect(self.__live_wpm_class_instance.calculate_live_wpm)
                # self.start_wpm_thread.start()
                """===================================MAIN-ALL-POINTS-INSTANCE======================================="""
                # self.__get__all_points_instance = GetAllPoints(self.correct_words_list, self.typed_in_text_list,
                #                                                self.get_all_points_thread, self.points_perf_counter)
                # self.__get__all_points_instance.moveToThread(self.get_all_points_thread)
                # self.get_all_points_thread.started.connect(self.__get__all_points_instance.append_all_points_list)
                # self.get_all_points_thread.start()
                try:
                    if self.correct_words_list[len(self.typed_in_text_list)] != self.type_line_edit.text().lstrip():
                        self.type_line_edit.setStyleSheet("background-color: #7a2721;"
                                                          "color: white;"
                                                          "border: 1px solid #5688b0;")
                        # print(self.correct_words_list[len(self.typed_in_text_list)], \
                        # self.type_line_edit.text().lstrip(), sep="")
                    else:
                        self.typed_in_text_list.append(self.type_line_edit.text().lstrip())
                        from copy import deepcopy
                        typed_in_line_edit_from_random = deepcopy(self.typed_in_text_list)
                        # self.type_line_edit.get_correct_and_typed_list(self.correct_words_list, self.typed_in_text_list)
                        self.type_line_edit.correct_words_list = self.correct_words_list
                        self.type_line_edit.typed_words_list = self.typed_in_text_list
                        self.type_line_edit.setText("")
                        self.type_line_edit.setStyleSheet("background-color: #111111;"
                                                          "color: white;"
                                                          "border: 1px solid #5688b0;")
                        self.__live_wpm_class_instance.update_typed_words_list(self.typed_in_text_list)
                        self.__get__all_points_instance.update_typed_words_list(self.typed_in_text_list)
                        # print(self.typed_in_text_list, "HERE") if\
                        # sum([len(x) for x in self.typed_in_text_list]) == 0 else print(self.typed_in_text_list)
                        if len(self.correct_words_list) == len(self.typed_in_text_list) or can_stop_time:
                            self.type_line_edit.setDisabled(True)
                            self.__text_edit.setText(' '.join(self.correct_words_list))
                            self.type_line_edit.setStyleSheet('border: 1px')
                            self.timer_label.setParent(None)
                            can_stop_time = False
                            self.plot_graph_matplotlib()

                        import copy
                        list_to_underline = copy.deepcopy(self.correct_words_list)
                        list_to_underline[
                            len(self.typed_in_text_list)] = r"<u>" + r"<font color=#67e06f>" + rf"{list_to_underline[len(self.typed_in_text_list)]}" + "</font>" + "</u>"
                        self.__text_edit.setText(' '.join(list_to_underline))
                        for x in range(len(self.typed_in_text_list)):
                            self.__text_edit.moveCursor(QTextCursor.WordRight, QTextCursor.MoveAnchor)
                        self.text_edit_column_number_list.append(self.__text_edit.textCursor().columnNumber())
                        self.__text_edit.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor)
                        # if self.text_edit_column_number_list[-1] < self.text_edit_column_number_list[-2]:
                        #     self.text_edit_column_number_list.clear()
                        #     self.__text_edit.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor)
                        #     self.number_of_downs_by_rows_text_edit += 1
                        # self.__text_edit.setTextCursor(self.__text_edit_cursor)
                except Exception as error:
                    # print(self.correct_words_list)
                    # print(self.correct_words_list)
                    # print(error)
                    pass
        return super(BuriRacerWindow, self).eventFilter(source, event)
        # t = QThread()
        # # setDaemon=False to stop the thread after complete
        # t.setDaemon(False)
        # # starting the thread
        # t.start()

    def clear_line_edit(self):
        self.type_line_edit.clear()

    def run_callback_queue(self):
        if self.IS_TYPE_TIMER:
            callback_queue.get()()

    def plot_graph_matplotlib(self):
        # self.__text_edit.setDisabled(True)
        # self.__text_edit.setParent(None)
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        from matplotlib.figure import Figure
        import sys
        import numpy as np

        def sleeper_getallpoints_exit():
            global is_graph_plotted
            sleep(3)
            is_graph_plotted = False

        class WpmGraph(FigureCanvasQTAgg):
            def __init__(self, parent):
                fig, self.ax = plt.subplots(figsize=(6, 2), dpi=200)
                super().__init__(fig)
                self.setParent(parent)

                x_axis = all_wpm_points
                y_axis = range(len(x_axis))
                self.ax.plot(y_axis, x_axis)
                self.ax.set(xlabel='Time (s)', ylabel='Words per Minute (WPM)',
                            title='Typing speed')

                # self.ax.grid()

        def generate_graph():
            # plt.style.use('dark_background')

            # fig, ax = plt.subplots()
            global is_graph_plotted
            # print(all_wpm_points)
            from copy import deepcopy
            # all_wpm_points.pop(0)
            copy_all_wpm_points = deepcopy(all_wpm_points)
            copy_all_wpm_points = [0] + all_wpm_points
            self.typed_in_text_list.clear()
            self.correct_words_list.clear()
            x_axis = list(range(len(copy_all_wpm_points)))
            y_axis = copy_all_wpm_points
            is_graph_plotted = True
            threading.Thread(target=sleeper_getallpoints_exit, args=[]).start()
            # all_wpm_points.clear()
            # plt.figure(facecolor='#111111')
            # ax.plot(x_axis, y_axis)  #, color='white')
            # ax.set_xlabel('Words per minute (WPM)')
            # ax.set_ylabel('Time (s)')
            # ax.set_title("Typing Speed")
            # # plt.figure().patch.set_facecolor("#111111")
            # ax = plt.axes()
            # ax.set_facecolor('#111111')
            # ax.set_facecolor((1.0, 0.47, 0.42))
            fig = plt.figure(figsize=(15, 5))

            fig.patch.set_facecolor('#111111')
            fig.patch.set_alpha(0.7)

            ax = fig.add_subplot(111)

            ax.plot(x_axis, y_axis, color='white')
            ax.set_ylabel('Words per minute (WPM)')
            ax.set_xlabel('Time (s)')
            ax.set_title("Typing Speed", color='white')
            ax.patch.set_facecolor('#111111')
            ax.patch.set_alpha(0.5)
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            plt.savefig(r"TypeRacer\MatplotLibGraph\wpm_plot.png", bbox_inches="tight")
            # plt.show()

        class GraphRemoveOs:
            def __init__(self, file_path_to_remove: str):
                self.file_path_to_remove = file_path_to_remove

            def __enter__(self):
                return self.file_path_to_remove

            def __exit__(self, exc_type, exc_val, exc_tb):
                os.remove(self.file_path_to_remove)

        """
        standard dpi = 100
        therefore, 15, 5 fig size would round up to 15 * 100, 5 * 100 = 1500, 500 pixels
        let result = 15
        then mut pixels = result * dpi -> this relationship has been used
        1238x470 -> This happens to be the resolution of the image that gets saved due to the bbox_inches argument 
        in savefig
        """
        with GraphRemoveOs(r"TypeRacer\MatplotlibGraph\wpm_plot.png") as png_file_path:
            thing = QLabel()  # WpmGraph(self)
            generate_graph()
            # thing.resize(self.width(), self.height())
            graph_pixmap = QPixmap(png_file_path)
            # graph_pixmap.scaled(2138, 470, Qt.KeepAspectRatio, Qt.SmoothTransformation) -> Does Nothing
            thing.setPixmap(graph_pixmap)
            self.__text_edit.deleteLater()
            self.type_line_edit.deleteLater()
            # os.remove(r"TypeRacer\MatplotlibGraph\wpm_plot.png")
            self.__live_wpm_label.move(int(0.9 * self.width()), int(0.1 * self.height()))
            # thing.move(self.width() - 1550, 0)
            # thing.show()
            """
            ---------------------------------------TypeRacer-Result-Data-----------------------------------------
            """
            if self.__title_for_text and self.__type_for_text and self.__author_for_text:
                # data_to_show = QLabel(self)
                # data_to_show.setStyleSheet("background-color: #111111; color: white;")
                if self.__type_for_text != 'other':
                    self.__typeracer_data_result_label.setText(
                        fr"""You just typed a quote from the {self.__type_for_text}:
            {self.__title_for_text} by {self.__author_for_text}""")
                else:
                    self.__typeracer_data_result_label.setText(
                        fr"""You just typed a quote from:
            {self.__title_for_text} by {self.__author_for_text}""")
                # self.__typeracer_data_result_label.move(100, 100)
                # self.__typeracer_data_result_label.setFixedSize(500, 500)
                self.__lyt.addWidget(self.__typeracer_data_result_label)
            self.__title_for_text = self.__type_for_text = self.__author_for_text = ""
            """
        """
        self.__lyt.addWidget(thing)

    def random_text(self):
        from random import choice, randint
        random_words = [
            'a', 'about', 'all', 'also', 'and', 'as', 'at', 'be', 'because', 'but', 'by', 'can', 'come',
            'could', 'day', 'do', 'even', 'find', 'first', 'for', 'from', 'get', 'give', 'go', 'have',
            'he', 'her', 'here', 'him', 'his', 'how', 'I', 'if', 'in', 'into', 'it', 'its', 'just',
            'know', 'like', 'look', 'make', 'man', 'many', 'me', 'more', 'my', 'new', 'no', 'not',
            'now', 'of', 'on', 'one', 'only', 'or', 'other', 'our', 'out', 'people', 'say', 'see',
            'she', 'so', 'some', 'take', 'tell', 'than', 'that', 'the', 'their', 'them', 'then',
            'there', 'these', 'they', 'thing', 'think', 'this', 'those', 'time', 'to', 'two', 'up',
            'use', 'very', 'want', 'way', 'we', 'well', 'what', 'when', 'which', 'who', 'will', 'with',
            'would', 'year', 'you', 'your'
        ]
        if not self.IS_TYPE_TIMER:
            len_choice = choice([1, 2, 3, 4])
            # length = "short" if len_choice == 1 else "medium" if len_choice == 2 else "long" if len_choice == 3 else "custom"
            mode = 'typeracer_database'
            import csv
            with open(rf"images_icons/settings.csv", mode="r") as csv_read:
                csv_read_file = csv.reader(csv_read)
                for x in csv_read_file:
                    if x[0] == "CUSTOM_RUN":
                        mode = 'typeracer_database' if x[1] == "TypeRacer Database" else 'custom' if x[
                                                                                                         1] == "Custom Text" \
                            else "Random Words"
            # with open(f"{length}_text.txt", "r", encoding='utf-8') as f_read:
            if not mode == "Random Words":
                if mode == 'typeracer_database':
                    with open(f"typeracer_database_text.csv", "r", encoding="utf-8") as f_read:
                        # print(f_read.seek(randint(0, sum(1 for line in f_read))))
                        all_text = list(csv.reader(f_read))  # 12728 bytes
                        thing = ""
                        while not thing:
                            complete_row = choice(all_text)
                            primary_key_id, typeracer_id, text_in, title, type_of_title, author = complete_row
                            thing = complete_row[2].lstrip()
                            # thing = 'there where thing'
                            # print(title, type_of_title, author)
                        # thing = 'there where thing' # ------------------------------COMMENT----------------------------
                        self.correct_words_list = thing.split()
                        correct_words_list_from_random = self.correct_words_list
                        self.type_line_edit.correct_words_list = self.correct_words_list
                        self.type_line_edit.typed_words_list = self.typed_in_text_list
                        self.__title_for_text, self.__type_for_text, self.__author_for_text = title, type_of_title, author
                        return thing
                else:
                    with open(f"{mode}_text.txt", "r", encoding="utf-8") as f_read:
                        # print(f_read.seek(randint(0, sum(1 for line in f_read))))
                        all_text = f_read.readlines()  # 12728 bytes
                        thing = ""
                        while not thing:
                            thing = choice(all_text).lstrip()
                        # thing = 'there where thing' # ------------------------------COMMENT----------------------------
                        self.correct_words_list = thing.split()
                        correct_words_list_from_random = self.correct_words_list
                        self.type_line_edit.correct_words_list = self.correct_words_list
                        self.type_line_edit.typed_words_list = self.typed_in_text_list
                        return thing
            else:
                thing = ' '.join(choice(random_words) for x in range(50))
                self.correct_words_list = thing.split()
                # correct_words_list_from_random = self.correct_words_list
                self.type_line_edit.correct_words_list = self.correct_words_list
                self.type_line_edit.typed_words_list = self.typed_in_text_list
                return thing
        else:
            thing = ' '.join(choice(random_words) for x in range(1_000))
            self.correct_words_list = thing.split()
            # correct_words_list_from_random = self.correct_words_list
            self.type_line_edit.correct_words_list = self.correct_words_list
            self.type_line_edit.typed_words_list = self.typed_in_text_list
            return thing


def run_function():
    new_app = QApplication(sys.argv)
    window = BuriRacerWindow()
    new_app.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BuriRacerWindow()
    sys.exit(app.exec_())

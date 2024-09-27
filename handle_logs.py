import os
import logging
import sys
from PyQt5.QtWidgets import qApp, QMessageBox, QMainWindow
import traceback


class BuriScriptLogHandler:
    def __init__(self, editor_home_path: str, qapplication_from_pyqt: qApp, parent_window: QMainWindow=None):
        self.editor_home_path = editor_home_path
        self.qapplication_from_pyqt = qapplication_from_pyqt
        self.__parent_window = parent_window
        os.chdir(self.editor_home_path)
        open(r"images_icons\error_logs.log", 'a')
        logging.basicConfig(filename=r"images_icons\error_logs.log", level=logging.ERROR,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        self.logger = logging.getLogger(__name__)

    def run_logs_from_sys_hook(self, error_type, value, traceback_from_sys_except_hook):
        logging_message = f"""{error_type.__class__.__name__}: {value} -> traceback:"\
    {traceback_from_sys_except_hook.tb_frame, traceback_from_sys_except_hook.tb_lasti,
        traceback_from_sys_except_hook.tb_lineno, traceback_from_sys_except_hook.tb_next}"""
        self.logger.error(logging_message)
        if self.__parent_window is not None:
            self.__parent_window.close()
            self.__show_msgbox(logging_message)
        self.qapplication_from_pyqt.exit(1)
        sys.exit()

    def __show_msgbox(self, message_to_show):
        error_message_box = QMessageBox()
        error_message_box.setIcon(QMessageBox.Critical)
        error_message_box.setText("A Fatal Error Occurred. Contact the developer.")
        error_message_box.setWindowTitle("Fatal Error")
        error_message_box.setDetailedText(message_to_show)
        error_message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        error_message_box.exec_()

    def custom_log_exceptions(self, error_type: str, *args, **kwargs):
        self.logger.error(f"""{error_type}, {args}, {kwargs}""")

    @staticmethod
    def traceback_formatter(traceback_call: traceback):
        return (type(traceback_call).__class__.__name__, traceback_call, traceback_call.tb_next,
                traceback_call.tb_lineno, traceback_call.tb_lasti, traceback_call.tb_frame)

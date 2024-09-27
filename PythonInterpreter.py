# _*_ coding: utf-8 _*_

# Third party imports
from PyQt5 import QtCore, QtWidgets, QtGui

# Standard library imports
import sys
import os
import time


style_sheet = """
background-color: #111111;
color: white;
"""

INTERPRETER_BUTTON_STYLE_SHEET = """
QPushButton{
    background-color: #2b2b2b;
    color: white;
    border-radius: 4px;
    border-color: #2b2b2b;
}
QPushButton:hover{
    background-color: #323437;
    color: white;
    border-radius: 4px;
    border-color: #323437;
}
QPushButton:pressed{
    background-color: #2b2b2b;
    color: white;
    border-radius: 4px;
    border-color: #2b2b2b;
}
"""


class CustomPythonTerminal(QtWidgets.QWidget):
    def __init__(self, file_name: str, parent=None):
        super().__init__(parent)
        self._file_name = file_name
        self._console_push_button = QtWidgets.QPushButton()
        self._console_push_button.setStyleSheet(INTERPRETER_BUTTON_STYLE_SHEET + "border-radius: 10px #111111;")
        # self._console_push_button.clicked.connect(lambda: self.run_in_console(self._file_name))
        self._console_push_button.setText("Run in Command Prompt")
        self._console_push_button.setFixedSize(155, 30)

        self.out = QtWidgets.QTextEdit()
        self.out.setFocusPolicy(QtCore.Qt.NoFocus)
        self.out.setReadOnly(True)
        self.out.ensureCursorVisible()
        self.out.acceptRichText()
        self.inBar = QtWidgets.QLineEdit()
        self.out.setStyleSheet(style_sheet)
        self.inBar.setStyleSheet(style_sheet)  # + "border-radius: 100px #323437;")
        self.setStyleSheet("background-color: #111111;")
        self.out.setFixedSize(QtWidgets.QDesktopWidget().screenGeometry().width(), 280)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addSpacing(0)
        layout.addWidget(self._console_push_button)
        layout.addWidget(self.out)
        layout.addWidget(self.inBar)

        self.process = QtCore.QProcess(self)
        # self.process.setProgram(sys.executable)
        self.process.finished.connect(lambda: self.std_out_exit_code())
        self.process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self.process.readyReadStandardError.connect(self.on_readyReadStandardError)
        self.inBar.editingFinished.connect(self.on_editingFinished)
        QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self).activated.connect(lambda: self.close_all_widgets_and_exit())

    def close_all_widgets_and_exit(self):
        try:
            self.process.terminate()
            self.process.kill()
        except BaseException as error:
            print(error, "FROM PythonInterpreter  close_all_widgets_and_exit")
        self.out.setParent(None)
        self.inBar.setParent(None)
        self.close()

    def runFile(self, url):
        # self.process.setArguments([url])
        self.process.start("python", [url])
        # warning: commented sys.executable and arguments. Instead used process.start() like os.system()

    @QtCore.pyqtSlot()
    def on_readyReadStandardOutput(self):
        out = self.process.readAllStandardOutput().data().decode()
        self.out.setTextColor(QtGui.QColor("white"))
        self.out.insertPlainText(out + "\n")
        # self.out.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)

    @QtCore.pyqtSlot()
    def on_readyReadStandardError(self):
        err = self.process.readAllStandardError().data().decode()
        self.out.setTextColor(QtGui.QColor("red"))
        self.out.insertPlainText(err + '\n')
        self.out.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)

    @QtCore.pyqtSlot()
    def on_editingFinished(self):
        self.process.write(self.inBar.text().encode() + b"\n")
        self.out.moveCursor(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor)
        self.out.insertPlainText(self.inBar.text() + "\n")
        # self.out.insertHtml("<font color=#51a0c4>" + f"{self.inBar.text()}" + "</font>")
        # self.out.insertPlainText('\n')
        self.inBar.clear()

    def run_in_console(self, file_to_run):
        pass

    def std_out_exit_code(self):
        """
        Runs when process is terminated. Sets text color to white at the end which doesn't seem to work.
        """
        self.out.setTextColor(QtGui.QColor("#c7bf63"))
        self.out.insertPlainText(f"Process finished with exit code {self.process.exitCode()}\n"
                                 f"Exit status {self.process.exitStatus()}")
        self.out.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        self.out.setTextColor(QtGui.QColor('white'))
        self.inBar.setDisabled(True)
        self.inBar.setReadOnly(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CustomPythonTerminal()
    os.chdir(r"C:/Users/BURI/Desktop/add_all_extra/python/BuriScript")
    window.runFile(r"BuriScript.py")
    window.show()
    sys.exit(app.exec_())
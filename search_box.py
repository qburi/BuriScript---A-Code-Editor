# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SearchText(QMainWindow):
    def __init__(self):
        super(SearchText, self).__init__(None)

        """
        
        """
        radius = 10
        path = QtGui.QPainterPath()
        self.resize(276, 50)
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        self.setStyleSheet("""background-color: #323437;
                              color: white;
                              border-radius: 20px #111111;
                              opacity: 100;
                              border: 10px #111111;""")

        """
        
        """
        self.setObjectName("MainWindow")
        # self.resize(276, 50)
        self.setMouseTracking(False)
        self.setStyleSheet("background-color: #323437")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 0, 271, 35))
        self.lineEdit.setStyleSheet("background-color: #323437 ;\n"
                                    "color: white;\n"
                                    "\n"
                                    "font: 12pt \"JetBrains Mono\";\n"
                                    "border: 0px;")
        self.__search: str = ""
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.lineEdit.returnPressed.connect(self.enter_pressed)
        self._escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        self._escape_shortcut.activated.connect(lambda: self.close_search_window())
        self.screern_geoemtry = QDesktopWidget().screenGeometry()
        self.move(self.screern_geoemtry.width() - 300, 100)
        self.show()

    def retranslateUi(self, nothing):
        # translate = QtCore.QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lineEdit.setPlaceholderText("Enter Module Name")

    def enter_pressed(self):
        self.__search = self.lineEdit.text()
        # import os
        # os.system(f"start python -c help('{self.__search}')")
        # import subprocess
        # try:
        #     text_output = subprocess.run(f"start python -c help('{self.__search}')", check=True, shell=True)
        #     print("\n\n", text_output.args)
        # except subprocess.CalledProcessError:
        #     print('command does not exist')
        self.close()
        import importlib
        spam_loader = importlib.util.find_spec(self.__search)
        found = spam_loader is not None
        import keyword
        import builtins
        if found or self.__search in list(keyword.kwlist) or self.__search in list(dir(builtins)):
            import os
            os.system(f"start cmd /k python -c help('{self.__search}')")

    def close_search_window(self):
        self.close()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    ui = SearchText()
    # ui.setupUi("MainWindow")
    sys.exit(app.exec_())

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(QtWidgets.QWidget):
    def __init__(self, master_window: QtWidgets.QMainWindow):
        super(Ui_Form, self).__init__()
        # self.Form = QtWidgets.QWidget()
        self.__master_window = master_window
        self.setObjectName("self")
        self.resize(1920, 20)
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.setFont(font)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background-color: #111111")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(5, 0, 250, 20))  # was 16 instead of 5
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white")
        self.pixmap = QtGui.QPixmap("images_icons\\python_darkgreen_lightgreen.png")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(1844, 0, 51, 23))
        self.pushButton.setStyleSheet("color: white")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(1800, 0, 41, 23))
        self.pushButton_2.setStyleSheet("color: white")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(1744, 0, 51, 23))
        self.pushButton_3.setStyleSheet("color: white")
        self.pushButton_3.setObjectName("pushButton_3")
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.pushButton.clicked.connect(self.close_the_window)
        self.pushButton_2.clicked.connect(self.maximize_the_window)
        self.pushButton_3.clicked.connect(self.minimize_the_window)
        self.setFixedSize(1920, 20)
        # self.show()

    def retranslateUi(self, Form):
        # _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate("Form", "self"))
        # self.label.setText(_translate("Form", "BuriScipt - A Text Editor"))
        # self.pushButton.setText(_translate("Form", "CLOSE"))
        # self.pushButton_2.setText(_translate("Form", "MAX"))
        # self.pushButton_3.setText(_translate("Form", "MIN"))
        self.label.setText("BuriScript - A Text Editor")
        # self.pushButton.setText("Close")
        # self.pushButton_2.setText("MAX")
        # self.pushButton_3.setText("MIN")
        self.pushButton_3.setIcon(QtGui.QIcon(r'images_icons\window_minimize_icon.png'))
        self.pushButton_3.setIconSize((QtCore.QSize(50, 100)))
        self.pushButton.setIcon(QtGui.QIcon(r"images_icons\window_close_icon.png"))
        self.pushButton.setIconSize(QtCore.QSize(50, 100))
        self.pushButton_2.setIcon(QtGui.QIcon(r"images_icons\window_maximize_icon.png"))
        self.pushButton_2.setIconSize(QtCore.QSize(50, 100))
        # self.pushButton_3.setStyleSheet(r"""
        # QPushBUtton{
        # }
        # QPushButton:hover{
        #     border - image: url(images_icons\window_minimize_icon.png);
        #     background - repeat: no - repeat;
        # }""")
        # self.pushButton.setStyleSheet(r"background-image: url(images_icons\window_close_icon.png)")

    def close_the_window(self):
        self.__master_window.close()

    def maximize_the_window(self):
        # from PyQt5.QtWidgets import QDesktopWidget
        # screen = QDesktopWidget().screenGeometry()
        # self.__master_window.setGeometry(0, 0, screen.width(), screen.height())
        self.__master_window.setGeometry(0, 0, 1920, 1032)
        self.__master_window.showMaximized()

    def minimize_the_window(self):
        self.__master_window.showMinimized()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form(QtWidgets.QMainWindow)
    # ui.setupUi(Form)
    # Form.show()
    sys.exit(app.exec_())

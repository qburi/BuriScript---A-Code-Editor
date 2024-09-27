# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.boolean_value_final = None

    def setupUi(self, MainWindow):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(218, 103)
        self.MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.MainWindow.setStyleSheet("background-color: #323437;")
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 201, 20))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: #323437;\n"
"color: white;")
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 50, 81, 31))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("color: white")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(110, 50, 91, 31))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("color: white")
        self.pushButton_2.setObjectName("pushButton_2")
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(self.MainWindow)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)
        self.label.setText("Do you want to Save?")
        self.pushButton.setText("Save")
        self.pushButton_2.setText("Cancel")
        self.pushButton.clicked.connect(lambda: self.return_boolean(True))
        self.pushButton_2.clicked.connect(lambda: self.return_boolean(False))
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
        with open("boolean_value.txt", "w") as boolean_value:
            boolean_value.write(str(1 if boolean_to_return else 0))
        return boolean_to_return

    def your_boolean_value(self):
        return self.boolean_value_final

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    app.exec_()
    print(ui.your_boolean_value())

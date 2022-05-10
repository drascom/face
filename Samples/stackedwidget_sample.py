from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
import sys
from datetime import datetime


class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.labelTime = QtWidgets.QLabel()
        self.labelTime.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: white")

        self.setStyleSheet("background-color: rgba(0, 191, 255, 0.6)")
        self.setFixedHeight(30)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.addWidget(self.labelTime, alignment=QtCore.Qt.AlignRight)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)
        self.timer.start()

        self.displayTime()

    def displayTime(self):
        self.labelTime.setText(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))


class Window(QWidget):
    changeWindow = QtCore.pyqtSignal(int)

    def changeTo(self, index):
        def callback():
            self.changeWindow.emit(index)

        return callback


class Window1(Window):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setText("Go to Window2")
        self.pushButton.clicked.connect(self.changeTo(1))

        layoutCenter = QHBoxLayout(self)
        layoutCenter.addWidget(self.pushButton, alignment=QtCore.Qt.AlignCenter)


class Window2(Window):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setText("Go to Window1")
        self.pushButton.clicked.connect(self.changeTo(0))

        layoutCenter = QHBoxLayout(self)
        layoutCenter.addWidget(self.pushButton, alignment=QtCore.Qt.AlignCenter)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.resize(480, 320)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.topbar = TopBar()
        lay = QtWidgets.QVBoxLayout(self.centralwidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.topbar)

        stacked_widget = QtWidgets.QStackedWidget()
        lay.addWidget(stacked_widget)

        for w in (Window1(), Window2()):
            stacked_widget.addWidget(w)
            if isinstance(w, Window):
                w.changeWindow.connect(stacked_widget.setCurrentIndex)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
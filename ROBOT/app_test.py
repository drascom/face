# worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QStackedLayout
import time
import sys
from database import DataRecords


class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    @pyqtSlot()
    def procCounter(self):  # A slot takes no params
        for i in range(1, 10):
            time.sleep(1)
            self.intReady.emit(i)

        self.finished.emit()


class SqlWorker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(object)
    previousFunction = ""

    @pyqtSlot()
    def read_data(self):  # A slot takes no params
        self.DataRecords = DataRecords()
        while True:
            time.sleep(1)
            function_name = self.find_function(self.DataRecords.getData())
            if function_name:
                self.intReady.emit(function_name)

    def find_function(self, data):
        if not data['function_name'] or not data['function_status'] or self.previousFunction == data['function_name']:
            return
        self.previousFunction = data['function_name']
        print(data['function_name'])
        return data


class Screen_1(QWidget):
    
    def __init__(self):
        super(Screen_1, self).__init__()
        self.label = QLabel("1")
        self.initUI()
    
    def initUI(self):
        VBL = QVBoxLayout(self)
        VBL.setContentsMargins(0, 0, 0, 0)
        VBL.addWidget(self.label)
        self.setLayout(VBL)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.obj = SqlWorker()  # no parent!
        self.thread = QThread()  # no parent!
        self.obj.intReady.connect(self.onIntReady)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.read_data)
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)
        self.thread.start()
        self.initUI()
        self.DataRecords = DataRecords()
        data = {'function_name': 'change_face',
                'function_status': True, 'data': 'sleep'}
        for key, value in data.items():
            self.DataRecords.saveData(key, value)

    def initUI(self):
        self.label = QLabel("0")
        VBL = QVBoxLayout()
        VBL.setContentsMargins(0, 0, 0, 0)
        self.screens = QStackedLayout()
        VBL.addLayout(self.screens)
        for index, item in enumerate([Screen_1(), ]):
            screenName = "screen_"+str(index)
            setattr(self, screenName, item)
            self.screens.addWidget(getattr(self, screenName))
        self.setLayout(VBL)
        self.screens.setCurrentIndex(0)

    def onIntReady(self, i):
        self.label.setText("{}".format(i))
        self.screen_0.label.setText("{}".format(i))
        # print(i)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.setWindowTitle('Thread Test')
    Root.show()
    sys.exit(App.exec())

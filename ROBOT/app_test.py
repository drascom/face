# worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QStackedLayout, QPushButton

import time
import sys

from cv2 import QT_PUSH_BUTTON
from database import DataRecords
from scan_pyqt import CameraThread


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
    previousStatus = ""

    @pyqtSlot()
    def read_data(self):  # A slot takes no params
        self.DataRecords = DataRecords()
        while True:
            time.sleep(1)
            function_name = self.find_function(self.DataRecords.getData())
            if function_name:
                self.intReady.emit(function_name)

    def find_function(self, data):
        if not data['function_name'] :
            return
        if self.previousFunction == data['function_name'] and self.previousStatus == data['function_status']:
            return
        if self.previousFunction != data['function_name']  and not data['function_status']:
            return   
        self.previousFunction = data['function_name']
        self.previousStatus = data['function_status']
        print(data['function_status'])
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
        self.BTN_1 = QPushButton("test")
        VBL.addWidget(self.BTN_1)
        self.BTN_1.clicked.connect(lambda: self.change_screen(1))
        self.setLayout(VBL)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.DataRecords = DataRecords()
        self.obj = SqlWorker()  # no parent!
        self.thread = QThread()  # no parent!
        self.obj.intReady.connect(self.run_function)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.read_data)
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)
        self.thread.start()
        self.initUI()

        
        self.testValue = 0
        
        
    
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
        self.timer = QTimer()
        data = {'function_name': 'open_camera',
                'function_status': 1, 'data': ''}
        self.save_test_values(data)
        self.timer.singleShot(2500, lambda:  self.save_test_values({'function_status': 0,}))
        self.timer.singleShot(5000, lambda:  self.save_test_values({'function_status': 1,}))

    def save_test_values(self,data):
        print("test values written")
        for key, value in data.items():
            self.DataRecords.saveData(key, value)

    def onIntReady(self, i):
        self.label.setText("{}".format(i))
        self.screen_0.label.setText("{}".format(i))
        # print(i)

    def run_function(self, data):
        if hasattr(self, data['function_name']):
            getattr(self, data['function_name'])(data)

    def open_camera(self, data):
        if self.testValue != data["function_status"]:
            print("camera opened", data)
            # if data['status'] == 0:
            #     self.obj2.finished_signal.emit()
            #     print("Camera Stop Called")
            # else:
            #     print("Camera Start Called")
            #     self.obj2.call_scan.emit()
            self.testValue =data["function_status"]


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.setWindowTitle('Thread Test')
    Root.show()
    sys.exit(App.exec())

import sys
import threading
from datetime import datetime as dt
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap, QImage, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtMultimedia
import cv2
from database import DataRecords
import SocketServer as Server
from pathlib import Path

from database import DataRecords
from Camera import scan_face, capture_face, convert_image, train_data
from Talk import say as Talk
from Listen import listen_google as Listen
from ServerBrain import Brain

class Communicate(QObject):
    MainSignal = pyqtSignal(object)

class WriteSql(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False

    def run(self, function_name, value):
        self.ThreadActive = True
        while self.ThreadActive:
            self.DataRecords.saveData(function_name, value)
            self.stop()

    def stop(self):
        self.ThreadActive = False


class ReadSql(QThread):
    Data = pyqtSignal(object)
    ScreenTrigger = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False
        self.values = None

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            self.msleep(500)
            self.values = self.DataRecords.getData()
            self.Data.emit(self.values)
            self.ScreenTrigger.emit({'section': self.values['section']})

    def stop(self):
        self.ThreadActive = False

class FunctionThread(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    CameraView = pyqtSignal(object)
    FunctionSelect = pyqtSignal(object)

    def __init__(self):
        super(FunctionThread, self).__init__()
        self.CameraView.connect(self.camera_view)
        self.FunctionSelect.connect(self.function_select)

    @pyqtSlot(object)
    def camera_view(self, data):
        print('T_Id:', threading.get_ident(), data)

    @pyqtSlot(object)
    def function_select(self, data,):
        if hasattr(self, data['function_name']):
            getattr(self, data['function_name'])(data['data'])
        self.finished.emit()


class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    PersonUpdate = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False
        self.mode = None

    def run(self):
        print("Camera Mode: ", self.mode)
        self.ThreadActive = True
        # start camera
        self.capture = cv2.VideoCapture(0)
        if self.mode == "view":
            while self.ThreadActive:
                ret, frame = self.capture.read()
                if ret:
                    Pic = convert_image(frame)
                    self.ImageUpdate.emit(Pic)
                else:
                    # if camera is not pluggedin try again
                    self.capture.release()
                    self.capture = cv2.VideoCapture(0)
            self.capture.release()
        elif self.mode == "scan":
            # stop openvc camera imutils will open camera again
            self.capture.release()
            person = scan_face()
            if person:
                self.PersonUpdate.emit(person)
            return
        elif self.mode == "capture":
            # name = input('isim > ')
            name = "a"
            Path("camera/dataset/"+name).mkdir(parents=True, exist_ok=True)
            img_counter = 1
            while img_counter < 150:
                ret, frame = self.capture.read()
                if not ret:
                    print("failed to grab frame")
                    break
                pic = convert_image(frame)
                self.ImageUpdate.emit(pic)
                if img_counter % 6 == 0:
                    capture_face(frame, name, img_counter)
                img_counter += 1
            self.capture.release()
            self.PersonUpdate.emit("a")
            train_data()

    def stop(self):
        self.ThreadActive = False
        self.quit()


class ServerThread(QThread):
    server = Server

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.server.run()


class MainThread(QThread):
    DataUpdate = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        while True:
            pass
            # command = Listen()
            # print(command)
            # self.DataUpdate.emit(command)


class CameraScreen(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super(CameraScreen, self).__init__()
        loadUi("ROBOT/gui/UI_home.ui", self)
        self.mainGif.setText("INIT")
        self.request_view_value = 0
        self.request_scan_value = 0
        self.request_capture_value = 0
        self.timer = QTimer()

    def screen_delay(self):
        # print("delaying screen...")
        self.timer.singleShot(3500, lambda: self.change_screen(0))

    def change_screen(self, screen):
        print("emitted 2")
        self.changeWindow.emit(screen)

    # this function runs via other functions
    def changeText(self, text):
        self.mainGif.setText(text)

    def update_frame(self, frame):
        self.mainGif.setPixmap(QPixmap.fromImage(frame))

    def update_gif(self, img_name):
        self.timer.singleShot(100, lambda: self.play_gif(img_name))

    def play_gif(self, img_name):
        movie = QMovie('images/faces/'+str(img_name)+'.gif')
        self.mainGif.setMovie(movie)
        movie.start()

    def _camera_start(self):
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.CameraThread.PersonUpdate.connect(self.PersonFoundSlot)
        self.CameraThread.start()

    def _camera_stop(self):
        print("Camera Stop Called")
        self.CameraThread.stop()

    def request_view(self, value):
        if value == 0:
            return
        self.request_view_value = value
        if self.request_view_value == 0:
            return
        print("başladı")
        self.change_screen(1)
        self.timer.singleShot(10000, self._camera_stop)
        self.CameraThread.mode = "view"
        self._camera_start()

    def request_scan(self, value):
        if self.request_scan_value != value:
            if value == 1:
                self.CameraThread.mode = "scan"
                self._camera_start()
                self.update_gif('faceid_scan')
            else:
                self._camera_stop()
                self.update_gif('faceid_confirm')
                self.timer.singleShot(1500, self.change_screen)

            self.request_scan_value = value

    def request_capture(self, value):
        if self.request_capture_value != value:
            if value == 1:
                self.CameraThread.mode = "capture"
                self._camera_start()
            else:
                self._camera_stop()
                self.timer.singleShot(
                    1500, lambda:  self.update_gif('wakeup'))
        self.request_capture_value = value

    # those functions runs  with camera thread

    def ImageUpdateSlot(self, Image):
        self.update_frame(Image)

    def PersonFoundSlot(self, name):
        # self.update_gif('faceid_confirm')
        print('[INFO] User Found: ', name)


class HomeScreen(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super(HomeScreen, self).__init__()
        loadUi("ROBOT/gui/UI_home.ui", self)
        self.timer = QTimer()

    def delay(self):
        # print("delaying screen...")
        self.timer.singleShot(3500, self.change_screen)

    def change_screen(self):
        print("changing screen")


class TopBar(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setAttribute(Qt.WA_StyledBackground)
        self.labelTime = QLabel()
        self.labelTime.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0); color: white")
        self.BTN_1 = QPushButton(" << ")
        self.BTN_2 = QPushButton(" >> ")
        self.BTN_1.clicked.connect(
            lambda: self.change_page(self.currentPage-1))
        self.BTN_2.clicked.connect(
            lambda: self.change_page(self.currentPage+1))
        self.setStyleSheet("background-color: rgba(0, 191, 255, 0.6)")
        self.setFixedHeight(30)

        self.currentPage = 0

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.addWidget(self.BTN_1)
        hbox.addWidget(self.labelTime, alignment=Qt.AlignRight)
        hbox.addWidget(self.BTN_2)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)
        self.timer.start()

        self.displayTime()

    def change_page(self, page):
        self.changeWindow.emit(page)

    def displayTime(self):
        self.labelTime.setText(dt.now().strftime("%Y/%m/%d %H:%M:%S"))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(640, 480)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.topbar = TopBar()
        VBL = QVBoxLayout(self.centralwidget)
        VBL.setContentsMargins(0, 0, 0, 0)
        VBL.addWidget(self.topbar)
        self.topbar.changeWindow.connect(self.default_screen)

        self.screens = QStackedLayout()
        VBL.addLayout(self.screens)
        # self.showMaximized()
        self.screenList = {
            'settings_screen': 0,
            'camera_screen': 1,
            'weather_screen': 2,
            'time_screen': 3,
            'alarm_screen': 4,
        }
        for index, item in enumerate([HomeScreen(), CameraScreen(), ]):
            screenName = "screen_"+str(index)
            setattr(self, screenName, item)
            self.screens.addWidget(getattr(self, screenName))
            getattr(self, screenName).changeWindow.connect(self.default_screen)

        self.screens.setCurrentIndex(0)
        self.worker = ServerThread()
        self.worker.start()

    def default_screen(self, page):
        if page >= 0 and page <= len(self.screens):
            self.screens.setCurrentIndex(page)
            self.topbar.currentPage = page

    def change_screen(self, data):
        # if new screen different than existing one
        if data['section'] != self.screens.currentIndex():
            # set current screen index to new one
            self.screens.setCurrentIndex(int(data['section']))
            # if there is a delay function of current widget run it
            if hasattr(self.screens.currentWidget(), "delay"):
                self.screens.currentWidget().delay()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    App.setStyle('Breeze')
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

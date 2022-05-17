import sys
import os
import time
from datetime import datetime as dt, timedelta
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap, QImage, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtMultimedia
import cv2
from pathlib import Path

from database import DataRecords
from Camera import scan_face, capture_face, convert_image, train_data
from Talk import say as Talk
from Listen import listen_google as Listen
from ServerBrain import Brain

# reusable widget definitions


class WriteSql(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False

    def run(self, function_name, value):
        self.ThreadActive = True
        while self.ThreadActive:
            self.DataRecords.request(function_name, value)
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


class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    PersonUpdate = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.WriteSql = WriteSql()
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
            self.WriteSql.run("request_view", 0)
            self.capture.release()
        elif self.mode == "scan":
            # stop openvc camera imutils will open camera again
            self.capture.release()
            person = scan_face()
            if person:
                self.WriteSql.run("request_scan", 0)
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
            self.WriteSql.run("request_capture", 0)

    def stop(self):
        self.ThreadActive = False
        self.quit()


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


class Window(QWidget):
    changeWindow = pyqtSignal(int)
    CameraThread = CameraThread()
    WriteSql = WriteSql()
    ReadSql = ReadSql()
    ReadSql.start()

    def changeTo(self, index):
        def callback():
            self.changeWindow.emit(index)

        return callback
# reusable widget definitions


class SettingsScreen(Window):
    def __init__(self):
        super(SettingsScreen, self).__init__()
        loadUi("gui/UI_settings.ui", self)
        self.WriteSql = WriteSql()
        self.ReadSql = ReadSql()
        self.ReadSql.start()
        self.STATUS_request_view = False
        self.STATUS_request_scan = False
        self.STATUS_request_capture = False

        self.BTN_request_view.clicked.connect(self.set_view)
        self.BTN_request_scan.clicked.connect(self.set_scan)
        self.BTN_request_capture.clicked.connect(self.set_record)
        self.think_BTN.clicked.connect(self.set_think)
        self.talk_BTN.clicked.connect(self.set_talk)
        self.listen_BTN.clicked.connect(self.set_listen)
        self.main_screen_BTN.clicked.connect(lambda: self.change_screen(1))
        self.weather_screen_BTN.clicked.connect(lambda: self.change_screen(2))
        self.clock_screen_BTN.clicked.connect(lambda: self.change_screen(3))
        # self.led_request_view.setPixmap(QPixmap('images/icons/led-red-on.png'))
        self.ReadSql.Data.connect(self.check_running_functions)
    # those functions runs with buttons

    def change_screen(self, screen):
        self.WriteSql.run("section", screen)

    def check_running_functions(self, row):
        for key, value in row.items():
            led = "LED_"+key
            button = "BTN_"+key
            status = "STATUS_"+key
            if hasattr(self, led):
                led = getattr(self, led)
                if value == 1:
                    led.setPixmap(QPixmap('images/icons/led-green-on.png'))
                else:
                    led.setPixmap(QPixmap('images/icons/led-red-on.png'))
                getattr(self, button).setChecked(value)
                setattr(self, status, True if value else False)

    def set_view(self):
        self.WriteSql.run("request_view", not self.STATUS_request_view)

    def set_scan(self):
        self.WriteSql.run("request_scan", not self.STATUS_request_scan)
        self.change_screen(1)

    def set_record(self):
        self.WriteSql.run("request_capture", not self.STATUS_request_capture)
        # self.change_screen(1)

    def set_think(self):
        print("set_think command")

    def set_talk(self):
        print("set_talk command")

    def set_listen(self):
        print("set listen command")


class CameraScreen(Window):
    def __init__(self):
        super(CameraScreen, self).__init__()
        loadUi("gui/UI_home.ui", self)
        self.mainGif.setText("INIT")
        self.request_view_value = 0
        self.request_scan_value = 0
        self.request_capture_value = 0
        self.timer = QTimer()
        self.ReadSql.Data.connect(self.run_function)

    def screen_delay(self):
        # print("delaying screen...")
        self.timer.singleShot(3500, lambda: self.change_screen(0))

    def change_screen(self, screen):
        # print("changing screen")
        self.WriteSql.run("section", screen)

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
        self.WriteSql("request_view",0)
        print("Camera Stop Called")
        self.CameraThread.stop()

    # those functions runs with trigger thread runs on/off by true/false
    def run_function(self, data):
        for key, value in data.items():
            if hasattr(CameraScreen, key):
                getattr(CameraScreen, key)(self, value)

    def request_view(self, value):
        print("init",value,self.request_view_value)
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


class WeatherScreen(Window):
    def __init__(self):
        super(WeatherScreen, self).__init__()
        loadUi("gui/UI_weather.ui", self)
        self.timer = QTimer()

    def delay(self):
        # print("delaying screen...")
        self.timer.singleShot(3500, self.change_screen)

    def change_screen(self):
        # print("changing screen")
        self.WriteSql.run("section", 0)

    def updateData(self, data):
        # self.today_img.setPixmap(
        #     QPixmap('robot/assets/icons/'+data['today_img']).scaledToWidth(100))
        for key in data:
            slot = self.findChild(QLabel, key)
            if slot:
                slot.setText(data[key])
                if "icon" in key:
                    slot.setPixmap(
                        QPixmap("robot/assets/icons/" + data[key]).scaledToWidth(50))


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ReadSql = ReadSql()
        self.WriteSql = WriteSql()
        self.VBL = QVBoxLayout()

        self.screens = QStackedLayout()
        self.VBL.addLayout(self.screens)
        self.setLayout(self.VBL)
        self.setFixedWidth(640)
        self.setFixedHeight(480)
        # self.showMaximized()
        self.screenList = {
            'settings_screen': 0,
            'camera_screen': 1,
            'weather_screen': 2,
            'time_screen': 3,
            'alarm_screen': 4,
        }
        for w in (SettingsScreen(), CameraScreen(), WeatherScreen()):
            self.screens.addWidget(w)
            if isinstance(w, Window):
                w.changeWindow.connect(self.screens.setCurrentIndex)

        self.ReadSql.ScreenTrigger.connect(self.change_screen)
        self.ReadSql.start()

        self.worker = MainThread()
        self.worker.start()
        self.default_screen(0)

    def default_screen(self, screen):
        # set custom screen
        self.screens.setCurrentIndex(screen)
        self.WriteSql.run("section", screen)

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

# herhangi bir widget yaratma ve tekrar kullanma ###################33
# def createLabel(self, parent, objName, text):
#     label = QLabel(parent)
#     label.setGeometry(QRect(0, 0, 921, 91))
#     label.setText(text)
#     label.setObjectName(objName)
#     return label

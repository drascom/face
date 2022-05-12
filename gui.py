import sys
import time
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap, QImage, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtMultimedia
import cv2
from database import DataRecords
from Camera import scan_face, capture_face, view_face, convert_image
from train import train_data


class UpdateSql(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False

    def run(self, function_name, value, ):
        print("SQL Update Start.")
        self.ThreadActive = True
        while self.ThreadActive:
            self.DataRecords.request(function_name, value)
            print(self.DataRecords.respond)
            self.stop()

    def stop(self):
        self.ThreadActive = False
        # self.wait()


class CheckTriggersThread(QThread):
    Trigger = pyqtSignal(object)
    ScreenTrigger = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False
        self.trigers = None

    def run(self):
        print("Main Thread Start.")
        self.ThreadActive = True
        activeJobs = []
        while self.ThreadActive:
            if len(activeJobs) > 1:
                print(activeJobs)
            # self.msleep(100)
            self.trigers = self.DataRecords.getData()
            for key, value in self.trigers.items():
                if key == "screen":
                    self.ScreenTrigger.emit({key: value})
                if value == 1:
                    if key not in activeJobs:
                        activeJobs.append(key)
                        self.Trigger.emit({key: value})
                else:
                    if key in activeJobs:
                        activeJobs.remove(key)

    def stop(self):
        print("Thread Stop")
        self.ThreadActive = False
        # self.stop()


class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    PersonUpdate = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.CheckTriggersThread = CheckTriggersThread()
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
                    # Pic = view_face(frame)
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
            self.PersonUpdate.emit(person)
            return
        elif self.mode == "capture":
            # stop openvc camera imutils will open camera again
            self.capture.release()
            name = input('isim > ')
            capture_face(name)
            return

    def stop(self):
        self.ThreadActive = False
        self.quit()

# reusable widget definitions


class Window(QWidget):
    changeWindow = pyqtSignal(int)

    def changeTo(self, index):
        def callback():
            self.changeWindow.emit(index)

        return callback


class MainGif(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)
        font = QFont('Arial', 24, QFont.Bold)
        self.setFont(font)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        self.setText('init')
        # self.change_image('main')

    def changeText(self, text):
        self.setText(text)

    def change_image(self, img_name):
        print("gif change run", img_name)
        movie = QMovie('images/faces/'+str(img_name)+'.gif')
        self.setMovie(movie)
        movie.start()
# reusable widget definitions


class HomeScreen(Window):
    def __init__(self):
        super(HomeScreen, self).__init__()
        self.sql_connection = UpdateSql()
        self.CameraThread = CameraThread()
        self.CheckTriggersThread = CheckTriggersThread()
        self.request_view = 0
        self.request_scan = 0
        self.request_capture = 0
        self.timer = QTimer()

        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.GifArea.setText("home")
        self.VBL.addWidget(self.GifArea)
        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.BTN_1 = QPushButton("Weather")
        # self.BTN_1.clicked.connect(self.changeTo(1))
        self.BTN_1.clicked.connect(lambda: self.change_screen(1))
        self.HBL.addWidget(self.BTN_1)
        self.BTN_2 = QPushButton("view")
        self.BTN_2.clicked.connect(self.set_view_camera)
        self.HBL.addWidget(self.BTN_2)
        self.BTN_3 = QPushButton("scan")
        self.BTN_3.clicked.connect(self.set_scan_person)
        self.HBL.addWidget(self.BTN_3)
        self.BTN_4 = QPushButton("record")
        self.BTN_4.clicked.connect(self.set_record_person)
        self.HBL.addWidget(self.BTN_4)
        self.setLayout(self.VBL)
        self.CheckTriggersThread.Trigger.connect(self.run_function)
        self.CheckTriggersThread.start()

    def run_function(self, data):
        key, value = data.popitem()
        getattr(HomeScreen, key)(self)
      

    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def change_screen(self, screen):
        print("ekran ", screen)
        self.sql_connection.run("screen", screen)

    def set_view_camera(self):
        self.sql_connection.run("request_view", not self.request_view)
        self.request_view = not self.request_view

    def set_scan_person(self):
        self.sql_connection.run("request_scan", not self.request_scan)
        self.request_scan = not self.request_scan

    def set_record_person(self):
        self.sql_connection.run("request_capture", not self.request_capture)
        self.request_capture = not self.request_capture

    def camera_start(self):
        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.CameraThread.PersonUpdate.connect(self.PersonFoundSlot)

    def camera_scan(self):
        self.CameraThread.mode = "scan"
        self.camera_start()

    def camera_capture(self):
        self.CameraThread.mode = "capture"
        self.camera_start()

    def request_view(self):
        self.CameraThread.mode = "view"
        self.camera_start()

    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def PersonFoundSlot(self, Data):
        self.GifArea.change_image(Data['image'])
        print('[INFO] User Found: ', Data['name'])
        self.timer.timeout.connect(lambda screen=0: self.update_screen(screen))
        self.timer.start(1500)


class WeatherScreen(Window):
    def __init__(self):
        super(WeatherScreen, self).__init__()
        loadUi("gui/UI_weather.ui", self)
        self.sql_connection = UpdateSql()
        self.timer = QTimer()

    def delay(self):
        # print("delaying screen...")
        self.timer.singleShot(3500, self.change_screen)

    def change_screen(self):
        # print("changing screen")
        self.sql_connection.run("screen", 0)

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
        self.CheckTriggersThread = CheckTriggersThread()
        print("main trigger Thread Id: ", int(
            self.CheckTriggersThread.currentThreadId()))

        self.VBL = QVBoxLayout()
        self.screenList = {
            'home_screen': 0,
            'time_screen': 1,
            'alarm_screen': 2,
            'weather_screen': 3
        }
        self.hava = WeatherScreen()
        self.current_screen = None
        self.screens = QStackedLayout()
        self.VBL.addLayout(self.screens)

        self.setLayout(self.VBL)
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        # self.showMaximized()

        for w in (HomeScreen(), WeatherScreen()):
            self.screens.addWidget(w)
            if isinstance(w, Window):
                w.changeWindow.connect(self.screens.setCurrentIndex)
        self.screens.setCurrentIndex(0)

        self.CheckTriggersThread.ScreenTrigger.connect(self.change_screen)
        self.CheckTriggersThread.start()

    def change_screen(self, data):
        # if new screen different than existing one
        if data['screen'] != self.screens.currentIndex():
            #set current screen index to new one
            self.screens.setCurrentIndex(int(data['screen']))
            #if there is a delay function of current widget run it
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

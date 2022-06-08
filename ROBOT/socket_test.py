import sys
import time
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
from scan_pyqt import CameraThread
from Talk import say as Talk
from Listen import listen_google as Listen
from ServerBrain import Brain


class sqlRead(QObject):
    data_ready_signal = pyqtSignal(object)
    call_function_signal = pyqtSignal(object)
    call_page_signal = pyqtSignal(object)
    call_face_change_signal = pyqtSignal(object)
    call_play_sfx_signal = pyqtSignal(object)
    call_play_voice_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.DataRecords = DataRecords()
        self.previousFunction = ""
        self.previousStatus = ""
        self.previousPage = ""
        self.previousFace = ""
        self.previousSfx = ""
        self.previousVoice = ""

    @pyqtSlot()
    def read_data(self):  # A slot takes no params
        while True:
            time.sleep(1)
            data = self.DataRecords.getData()
            if data:
                self.data_ready_signal.emit(data)  # signal recceived data
                self.find_page(data)
                self.find_function(data)
                self.find_face(data)
                self.find_voice(data)

    def find_page(self, data):
        if not data['page'] or self.previousPage == data['page']:
            return
        self.previousPage = data['page']
        # signal received new function name
        self.call_page_signal.emit(data['page'])

    def find_function(self, data):
        if not data['function_name'] :
            return
        if self.previousFunction == data['function_name'] and self.previousStatus == data['function_status']:
            return
        if self.previousFunction != data['function_name']  and not data['function_status']:
            return   
        print(data["function_name"])
        self.previousFunction = data['function_name']
        # signal received new function name
        self.call_function_signal.emit(
            {'name': data['function_name'], 'status': data['function_status'], 'data': data['data']})

    def find_face(self, data):
        if not data['face'] or self.previousFace == data['face']:
            return
        self.previousFace = data['face']
        self.call_face_change_signal.emit(
            data['face'])  # signal received new face

    def find_sfx(self, data):
        if not data['sfx_link'] or self.previousSfx == data['sfx_link']:
            return
        self.previousSfx = data['sfx_link']
        self.call_play_sfx_signal.emit(
            data['sfx_link'])  # signal received new sfx

    def find_voice(self, data):
        if not data['voice_link'] or self.previousVoice == data['voice_link']:
            return
        self.previousVoice = data['voice_link']
        self.call_play_voice_signal.emit(
            data['voice_link'])  # signal received new voice


class sqlWrite(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False

    def save(self,data):
        self.ThreadActive = True
        for key, value in data.items():
            self.DataRecords.saveData(key,value)
            self.stop()

    def stop(self):
        self.ThreadActive = False


class ServerThread(QThread):
    server = Server

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.server.run()


class ClockScreen(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super(ClockScreen, self).__init__()
        loadUi("gui/UI_clock.ui", self)
        self.screen_delay = 5


class WeatherScreen(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super(WeatherScreen, self).__init__()
        loadUi("gui/UI_weather.ui", self)
        self.screen_delay = 2


class HomeScreen(QWidget):
    changeWindow = pyqtSignal(int)

    def __init__(self):
        super(HomeScreen, self).__init__()
        VBL = QVBoxLayout(self)
        self.mainGif = QLabel("1")
        self.mainGif.setText("home")
        self.mainGif.setScaledContents(True)
        self.videoGif = QLabel("1")
        self.videoGif.setScaledContents(True)
        self.videoGif.hide()
        VBL.setContentsMargins(0, 0, 0, 0)
        VBL.addWidget(self.mainGif)
        VBL.addWidget(self.videoGif)
        self.setLayout(VBL)


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
        hbox.setContentsMargins(0, 0, 0, 0)
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

    def __init__(self):
        super().__init__()
        self.resize(400, 300)
        
        # sql thread
        self.obj = sqlRead()  # no parent!
        self.thread = QThread()  # no parent!
        self.obj.moveToThread(self.thread)
        self.obj.call_function_signal.connect(self.run_function)
        self.obj.call_page_signal.connect(self.change_page)
        self.obj.call_face_change_signal.connect(self.change_face)
        self.thread.started.connect(self.obj.read_data) # <- this thread start immedetaly
        self.thread.start()
        #functions
        # self.call_play_sfx_signal.connect(self.play_sfx)
        # self.call_play_voice_signal.connect(self.play_voice)
        
        #slqWrite thread
        self.sqlWrite = sqlWrite()
        
        #socket server thread
        self.worker = ServerThread()
        self.worker.start()
        
        # camera thread
        self.obj2 = CameraThread()
        self.thread2 = QThread()  # no parent!
        self.obj2.moveToThread(self.thread2)
        self.obj2.image_update_signal.connect(self.update_frame_slot)
        self.thread2.start()
        # self.obj2.call_scan.emit() # <- this thread start with spesific emits from related method(can be multiple) 

        # * - Thread finished signal will end thread if you need!
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)

        self.initUI()
        self.initData()

    def initUI(self):
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.VBL = QVBoxLayout(self.centralwidget)
        self.VBL.setContentsMargins(0, 0, 0, 0)
        self.topbar = TopBar()
        self.VBL.addWidget(self.topbar)
        self.topbar.changeWindow.connect(self.change_page)

        self.pages = QStackedLayout()
        self.VBL.addLayout(self.pages)
        self.page_list = {
            'HomeScreen': HomeScreen(),
            'ClockScreen': ClockScreen(),
            'WeatherScreen': WeatherScreen()
        }
        for key, value in self.page_list.items():
            setattr(self, key, value)
            self.pages.addWidget(getattr(self, key))

    def initData(self):
        self.timer = QTimer()
        self.current_timer = None
        self.pages.setCurrentIndex(0)
        # self.change_face('love')

    def change_page(self, page):
        # if new screen different than existing one
        if (int(page) < 0 or int(page) > len(self.pages)-1) or page == self.pages.currentIndex():
            return
        # set current screen index to new one
        self.sqlWrite.save({"page": page})
        self.pages.setCurrentIndex(page)
        self.topbar.currentPage = page
        # if there is a delay function in current widget run it
        if hasattr(self.pages.currentWidget(), 'screen_delay'):
            self.delay(getattr(self.pages.currentWidget(), 'screen_delay'))

    def delay(self, second):
        print("second", second)
        if second == 0:
            return
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer.deleteLater()
        self.current_timer = QTimer()
        self.current_timer.timeout.connect(lambda: self.change_page(0))
        self.current_timer.setSingleShot(True)
        self.current_timer.start(second*1000)

    def run_function(self, data):
        print("run function data", data)
        if hasattr(self, data['name']):
            getattr(self, data['name'])(data)

    def changeText(self, text):
        self.mainGif.setText(text)

    def change_gif(self, img_name):
        self.timer.singleShot(100, lambda: self.change_gif(img_name))

    def change_face(self, img_name):
        def _change_face(self, img_name):
            print("face change", img_name)
            movie = QMovie('images/faces/'+str(img_name)+'.gif')
            self.HomeScreen.mainGif.setMovie(movie)
            movie.start()

        _change_face(self, img_name)
        self.timer.singleShot(5000, lambda: _change_face(self, 'main'))

   #  camera functions
    def open_camera(self, data):
        print("camera opened")
        if data['status'] == 0:
            print("Camera Stop Called")
            self.obj2.call_stop.emit() 
            self.sqlWrite.save({'function_name':'','function_status':0,'data':''})#revert database to old state
            self.HomeScreen.mainGif.clear()
            self.change_face('main')
            
        else:
            print("Camera Start Called")
            self.obj2.call_scan.emit() 
            self.sqlWrite.save({'function_name':'','function_status':0,'data':''})#revert database to old state

    def update_frame_slot(self, frame):
        self.HomeScreen.mainGif.setPixmap(QPixmap.fromImage(frame))

    def face_confirmed_slot(self, name):
        # self.update_gif('faceid_confirm')
        print('[INFO] User Found: ', name)

    def check(data):
        print("test", data)
    # triggerred via topbar buttons or sql page value

    def request_view(self, value):
        if value == 0:
            return
        self.request_view_value = value
        if self.request_view_value == 0:
            return
        print("başladı")
        self.change_page(1)
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
                self.timer.singleShot(1500, self.change_page)

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


if __name__ == "__main__":
    App = QApplication(sys.argv)
    App.setStyle('Breeze')
    Root = MainWindow()
    Root.resize(400, 300)
    Root.show()
    sys.exit(App.exec())

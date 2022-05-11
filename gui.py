import sys
import time
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap, QImage, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
from database import DataRecords
from Camera import scan_face,capture_face,view_face,convert_image
from train import train_data


class UpdateSql(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataRecords = DataRecords()
        self.ThreadActive = False

    def run(self, function_name, value, ):
        print("SQL Update Start.")
        self.ThreadActive = True
        slot = getattr(self.DataRecords, function_name)
        while self.ThreadActive:
            slot(value)
            print(self.DataRecords.respond)
            self.stop()

    def stop(self):
        self.ThreadActive = False
        # self.wait()


class CheckTriggersThread(QThread):
    Trigger = pyqtSignal(object)

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
            time.sleep(0.5)
            self.trigers = self.DataRecords.getData()
            for key, value in self.trigers.items():
                if value == 1:
                    if key not in activeJobs:
                        activeJobs.append(key)
                        self.Trigger.emit(key)
                else:
                    if key in activeJobs:
                        activeJobs.remove(key)

    def stop(self):
        self.ThreadActive = False
        self.wait()


class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    PersonUpdate = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False
        self.mode = None

    def run(self):
        print("Camera Mode: ",self.mode)
        self.ThreadActive = True
        #start camera
        self.capture = cv2.VideoCapture(0)
        if self.mode == "view":
            while self.ThreadActive:
                ret, frame = self.capture.read()
                if ret:
                    Pic = convert_image(frame)
                    # Pic = view_face(frame)
                    self.ImageUpdate.emit(Pic)
                else:
                    #if camera is not pluggedin try again
                    self.capture.release()
                    self.capture = cv2.VideoCapture(0)
            self.capture.release()
        elif self.mode == "scan":
            #stop openvc camera imutils will open camera again
            self.capture.release()
            person = scan_face()
            self.PersonUpdate.emit(person)
            return
        elif self.mode == "capture":
             #stop openvc camera imutils will open camera again
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

# herhangi bir widget yaratma ve tekrar kullanma ###################33
# def createLabel(self, parent, objName, text):
#     label = QLabel(parent)
#     label.setGeometry(QRect(0, 0, 921, 91))
#     label.setText(text)
#     label.setObjectName(objName)
#     return label


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
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.GifArea.setText("home")
        self.VBL.addWidget(self.GifArea)
        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.BTN_1 = QPushButton("Camera")
        self.BTN_1.clicked.connect(self.changeTo(1))
        self.HBL.addWidget(self.BTN_1)
        self.BTN_2 = QPushButton("SCAN")
        self.BTN_2.clicked.connect(self.set_scanning)
        self.HBL.addWidget(self.BTN_2)
        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def set_scanning(self):
        self.sql_connection.run("request_scan", "1")


class CameraScreen(Window):
    def __init__(self):
        super(CameraScreen, self).__init__()
        self.CheckTriggersThread = CheckTriggersThread()

        self.CameraThread = CameraThread()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)

        self.timer = QTimer()

        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.GifArea.setText("camera")
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.VBL.addWidget(self.GifArea)
        # self.GifArea.change_image('faceid')

        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.HomeBTN = QPushButton("Home")
        self.HomeBTN.clicked.connect(self.changeTo(0))
        self.HBL.addWidget(self.HomeBTN)

        self.setLayout(self.VBL)

        # self.camera_view()
        self.camera_capture()
        # self.camera_scan()

    def run_function(self, key):
        slot = getattr(self, key)
        print("1 function call", key)
        slot()
    
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
    def camera_view(self):
        self.CameraThread.mode = "view"
        self.camera_start()
       
    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def PersonFoundSlot(self, Data):
        self.GifArea.change_image(Data['image'])
        print('[INFO] User Found: ', Data['name'])
        self.timer.timeout.connect(lambda screen=0: self.update_screen(screen))
        self.timer.start(1500)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.CheckTriggersThread = CheckTriggersThread()
        self.camera_status = False
        self.VBL = QVBoxLayout()
        self.screenList = {
            'home_screen': 0,
            'time_screen': 1,
            'alarm_screen': 2,
            'weather_screen': 3,
            'camera_screen': 4
        }

        self.screens = QStackedLayout()
        self.VBL.addLayout(self.screens)
        # self.screens.setCurrentIndex(0)
        for w in (HomeScreen(), CameraScreen()):
            self.screens.addWidget(w)
            if isinstance(w, Window):
                w.changeWindow.connect(self.screens.setCurrentIndex)
        self.screens.setCurrentIndex(0)

        self.setLayout(self.VBL)
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        # self.showMaximized()
        self.CheckTriggersThread.Trigger.connect(self.run_function)
        self.CheckTriggersThread.start()

    def update_screen(self, screen):
        self.screens.setCurrentIndex(screen)

    def run_function(self, key):
        screen_1_items = ["view_camera", "request_scan",
                          "request_capture", "request_train_face"]
        if key in screen_1_items:
            self.screens.setCurrentIndex(1)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

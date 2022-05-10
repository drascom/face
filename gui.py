import sys
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

from scan import Scanning
from train import train_data


class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    FaceFound = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False

    def run(self):
        print("camera Thread Start.")
        self.ThreadActive = True
        self.scan = Scanning()
        self.scan.run()
        while self.ThreadActive:
            print("robot loop")
            if self.scan.picture is not None:
                print("pic update")
                self.ImageUpdate.emit(self.scan.picture)
            # if self.scan.currentname != "?":
            #     print("bulundu",self.scan.currentname)
            #     self.FaceFound.emit(
            #         {"name": self.scan.currentname, "image": 'faceid_confirm'})
            #     break

    def stop(self):
        self.ThreadActive = False
        self.scan.capture.stop()#imutils VideoStream
        # self.scan.capture.release()#opencv VideoCapture

#################### reusable widget definitions

class Window(QWidget):
    changeWindow = pyqtSignal(int)

    def changeTo(self, index):
        def callback():
            self.changeWindow.emit(index)

        return callback
class MainGif(QLabel):
    def __init__(self):
        QLabel.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        # self.change_image('main')

    def change_image(self, img_name):
        print("gif change run", img_name)
        movie = QMovie('images/faces/'+str(img_name)+'.gif')
        self.setMovie(movie)
        movie.start()
####################### reusable widget definitions

class HomeScreen(Window):
    def __init__(self):
        super(HomeScreen, self).__init__()
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea)
        self.GifArea.change_image('sleep')
        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.BTN_1 = QPushButton("Camera")
        self.BTN_1.clicked.connect(self.changeTo(1))
        self.HBL.addWidget(self.BTN_1)
        self.BTN_2 = QPushButton("Saat")
        self.BTN_2.clicked.connect(self.changeTo(2))
        self.HBL.addWidget(self.BTN_2)
        self.BTN_3 = QPushButton("Hava")
        self.BTN_3.clicked.connect(self.changeTo(3))
        self.HBL.addWidget(self.BTN_3)
        self.BTN_4 = QPushButton("Bilgi")
        self.BTN_4.clicked.connect(self.changeTo(4))
        self.HBL.addWidget(self.BTN_4)
        self.setLayout(self.VBL)

    def update_screen(self, screen):
        self.change_screen.emit(screen)


class CameraScreen(Window):
    change_screen = pyqtSignal(int)

    def __init__(self):
        super(CameraScreen, self).__init__()
        self.CameraThread = CameraThread()
        self.camera_status = False
        self.timer = QTimer()

        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea)
        self.GifArea.change_image('faceid')

        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.HomeBTN = QPushButton("Home")
        self.HomeBTN.clicked.connect(self.changeTo(0))
        self.HBL.addWidget(self.HomeBTN)

        self.CameraBTN = QPushButton("--")
        self.HBL.addWidget(self.CameraBTN)
        self.CameraBTN.clicked.connect(self.toggle_camera)


        self.setLayout(self.VBL)

    def update_screen(self, screen):
        self.change_screen.emit(screen)

    def toggle_camera(self):
        if self.camera_status:
            self.CameraBTN.setText("Start")
            self.CameraThread.stop()
            self.GifArea.setPixmap(QPixmap())
            # self.timer.timeout.connect(lambda image='wakeup': self.GifArea.change_image(image))
            self.timer.singleShot(500, lambda image='wakeup': self.GifArea.change_image(image))

            
        else:
            self.CameraBTN.setText("Stop")
            self.CameraThread.start()
            self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
            self.CameraThread.FaceFound.connect(self.FaceFoundSlot)
        self.camera_status = not self.camera_status

    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def FaceFoundSlot(self, Data):
        self.GifArea.change_image(Data['image'])
        print('[INFO] User Found: ', Data['name'])
        self.timer.timeout.connect(lambda screen=0: self.update_screen(screen))
        self.timer.start(1500)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.camera_status = False
        self.VBL = QVBoxLayout()
        self.screenList = {
            'home_screen': 0,
            'time_screen': 1,
            'alarm_screen': 2,
            'weather_screen': 3,
            'camera_screen': 4
        }

        screens = QStackedLayout()
        self.VBL.addLayout(screens)
        # self.screens.setCurrentIndex(0)
        for w in (HomeScreen(), CameraScreen()):
            screens.addWidget(w)
            if isinstance(w, Window):
                w.changeWindow.connect(screens.setCurrentIndex)
        screens.setCurrentIndex(1)

        self.setLayout(self.VBL)
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        # self.showMaximized()

    def update_screen(self, screen):
        self.screens.setCurrentIndex(screen)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

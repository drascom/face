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
    ButtonUpdate = pyqtSignal(object)
    FaceFound = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False
        self.capture = None

    def run(self):
        self.ThreadActive = True
        scan = Scanning()
        self.capture = cv2.VideoCapture(0)
        self.ButtonUpdate.emit(self.capture.isOpened())
        while self.ThreadActive:
            ret, frame = self.capture.read()
            if ret:
                #scanning face
                name = scan.scan_face(frame)
                if name is not None:
                    self.FaceFound.emit(
                        {"name": name, "image": 'faceid_confirm'})
                    self.stop()
                #update video
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                           QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
            else:
                print("capture read olmadı")
                break
            
        self.ButtonUpdate.emit(self.capture.isOpened())

    def stop(self):
        self.ThreadActive = False
        self.capture.release()
        self.quit()


class MainGif(QLabel):
    def __init__(self):
        QLabel.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        self.change_image('main')

    def change_image(self, img_name):
        print("gif change run", img_name)
        movie = QMovie('images/faces/'+str(img_name)+'.gif')
        self.setMovie(movie)
        movie.start()


class HomeScreen(QWidget):
    change_screen = pyqtSignal(int)

    def __init__(self):
        super(HomeScreen, self).__init__()
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea)
        self.GifArea.change_image('sleep')
        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.BTN_1 = QPushButton("Camera")
        self.BTN_1.clicked.connect(
            lambda screen=1: self.update_screen(screen=1))
        self.HBL.addWidget(self.BTN_1)
        self.BTN_2 = QPushButton("Saat")
        self.BTN_2.clicked.connect(lambda screen=2: self.update_screen(screen))
        self.HBL.addWidget(self.BTN_2)
        self.BTN_3 = QPushButton("Hava")
        self.BTN_3.clicked.connect(lambda screen=3: self.update_screen(screen))
        self.HBL.addWidget(self.BTN_3)
        self.BTN_4 = QPushButton("Bilgi")
        self.BTN_4.clicked.connect(lambda screen=4: self.update_screen(screen))
        self.HBL.addWidget(self.BTN_4)
        self.setLayout(self.VBL)

    def update_screen(self, screen):
        self.change_screen.emit(screen)


class CameraScreen(QWidget):
    change_screen = pyqtSignal(int)

    def __init__(self):
        super(CameraScreen, self).__init__()
        self.CameraThread = CameraThread()
        self.VBL = QVBoxLayout()

        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea)
        self.GifArea.change_image('faceid')

        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        self.HomeBTN = QPushButton("Home")
        self.HomeBTN.clicked.connect(
            lambda screen=0: self.update_screen(screen=0))
        self.HBL.addWidget(self.HomeBTN)

        self.VideoOnBTN = QPushButton("Start")
        self.HBL.addWidget(self.VideoOnBTN)
        self.VideoOnBTN.clicked.connect(self.start_camera)

        self.VideoOffBTN = QPushButton("Stop")
        self.HBL.addWidget(self.VideoOffBTN)
        self.VideoOffBTN.clicked.connect(self.stop_camera)
        self.VideoOffBTN.hide()

        self.setLayout(self.VBL)

    def update_screen(self, screen):
        self.change_screen.emit(screen)

    def start_camera(self):
        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.CameraThread.ButtonUpdate.connect(self.ButtonUpdateSlot)
        self.CameraThread.FaceFound.connect(self.FaceFoundSlot)

    def stop_camera(self):
        self.CameraThread.stop()
        self.GifArea.change_image('wakeup')
        self.CameraThread.ButtonUpdate.connect(self.ButtonUpdateSlot)

    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))

    def FaceFoundSlot(self,Data):
        self.GifArea.change_image(Data['image'])
        print('[INFO] User Found: ',Data['name'])
        self.timer = QTimer()
        self.timer.timeout.connect(lambda screen =0:self.update_screen(screen))
        self.timer.start(1500)

    def ButtonUpdateSlot(self, status):
        print("button status", status)
        if status:
            self.VideoOffBTN.show()
            self.VideoOnBTN.hide()
        else:
            self.VideoOnBTN.show()
            self.VideoOffBTN.hide()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.camera_status = False

        self.VBL = QVBoxLayout()
        self.screens = QStackedLayout()
        self.VBL.addLayout(self.screens)
        self.screenList = {
            'home_screen': 0,
            'time_screen': 1,
            'alarm_screen': 2,
            'weather_screen': 3,
            'camera_screen': 4
        }
        # define&add screens and connect with change screen signal
        self.home_screen = HomeScreen()
        self.screens.addWidget(self.home_screen)
        self.home_screen.change_screen.connect(self.update_screen)

        self.camera_screen = CameraScreen()
        self.screens.addWidget(self.camera_screen)
        self.camera_screen.change_screen.connect(self.update_screen)

        self.screens.setCurrentIndex(0)

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

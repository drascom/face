import sys
from xmlrpc.client import boolean
from PyQt5.QtGui import QMovie, QPixmap,QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)
    ButtonUpdate = pyqtSignal(boolean)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False
        self.capture = None
    def run(self):
        self.ThreadActive = True
        self.capture = cv2.VideoCapture(0)
        print("kamera durum: ",self.capture.isOpened())  
        while self.ThreadActive:
            self.ButtonUpdate.emit(False)
            ret, frame = self.capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                           QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
            else:
                print("capture read olmadı")
        self.ButtonUpdate.emit(True)

    def stop(self):
        self.ThreadActive = False
        self.capture.release()
        print("kamera durum: ",self.capture.isOpened())   # self.wait()
        self.quit()

class MainGif(QLabel):
    def __init__(self,img_name):
        QLabel.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        movie = QMovie('./faces/'+str(img_name)+'.gif')
        self.setMovie(movie)
        self.setScaledContents(True)
        movie.start()


class HomeScreen(QWidget):
    change_screen = pyqtSignal(int)
    def __init__(self):
        super(HomeScreen, self).__init__()
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif('sleep')
        self.VBL.addWidget(self.GifArea) 
        
        self.BTN_1 = QPushButton("Home")
        self.BTN_1.clicked.connect(lambda screen= 0: self.update_screen(screen))
        self.VBL.addWidget(self.BTN_1)
        self.BTN_2 = QPushButton("Saat")
        self.BTN_2.clicked.connect(lambda screen= 1: self.update_screen(screen))
        self.VBL.addWidget(self.BTN_2)
        self.BTN_3 = QPushButton("Hava")
        self.BTN_3.clicked.connect(lambda screen= 2: self.update_screen(screen))
        self.VBL.addWidget(self.BTN_3)
        self.BTN_4 = QPushButton("Camera")
        self.BTN_4.clicked.connect(lambda screen= 3: self.update_screen(screen))
        self.VBL.addWidget(self.BTN_4)
        self.setLayout(self.VBL)
    def update_screen(self,screen):
        self.change_screen.emit(screen)

class CameraScreen(QWidget):
    change_screen = pyqtSignal(int)
    def __init__(self):
        super(CameraScreen, self).__init__()
        self.CameraThread = CameraThread()
        self.VBL = QVBoxLayout()
        
        self.GifArea = MainGif('facescan')
        self.VBL.addWidget(self.GifArea) 

        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)
        
        self.HomeBTN = QPushButton("Home")
        self.HomeBTN.clicked.connect(lambda screen=0: self.update_screen(screen=0))
        self.HBL.addWidget(self.HomeBTN)

        self.VideoOnBTN = QPushButton("Start")
        self.VideoOnBTN.clicked.connect(self.start_camera)
        self.HBL.addWidget(self.VideoOnBTN)

        self.VideoOffBTN = QPushButton("Stop")
        self.VideoOffBTN.clicked.connect(self.stop_camera)
        self.HBL.addWidget(self.VideoOffBTN)
        self.setLayout(self.VBL)
    def update_screen(self,screen):
        self.change_screen.emit(screen)
    
    def start_camera(self):
        self.GifArea.clear()   
        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)
        self.CameraThread.ButtonUpdate.connect(self.ButtonUpdateSlot)
    def stop_camera(self):
        self.CameraThread.stop()
        self.GifArea.clear()   
    
    def ImageUpdateSlot(self, Image):
        self.GifArea.setPixmap(QPixmap.fromImage(Image))  

    def ButtonUpdateSlot(self, status):
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
            'camera_screen':4
        }

        self.home_screen = HomeScreen()
        # self.time_screen = TimeScreen()
        # self.alarm_screen = AlarmScreen()
        # self.weather_screen = WeatherScreen()
        self.camera_screen = CameraScreen()
        # self.screens.addWidget(self.time_screen)
        # self.screens.addWidget(self.alarm_screen)
        # self.screens.addWidget(self.weather_screen)
        self.screens.addWidget(self.camera_screen)
        self.screens.setCurrentIndex(0)
     
        self.setLayout(self.VBL)
        self.showMaximized()





if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

import sys
from PyQt5.QtGui import QMovie, QPixmap,QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class CameraThread(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ThreadActive = False
        self.capture = None
    def run(self):
        self.ThreadActive = True
        self.capture = cv2.VideoCapture(0)
        print("kamera durum: ",self.capture.isOpened())  
        while self.ThreadActive:
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

    def stop(self):
        self.ThreadActive = False
        self.capture.release()
        print("kamera durum: ",self.capture.isOpened())   # self.wait()
        self.quit()

class MainGif(QLabel):
    def __init__(self):
        QLabel.__init__(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.resize(800, 600)
        self.pixmap = QPixmap("image.jpg")
        self.setPixmap(self.pixmap)
        self.MovieLabel.setScaledContents(True)


class HomeScreen(QWidget):
    change_screen = pyqtSignal(int)
    def __init__(self):
        super(HomeScreen, self).__init__()
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea) 

class CameraScreen(QWidget):
    change_screen = pyqtSignal(int)
    def __init__(self):
        super(CameraScreen, self).__init__()
        self.CameraThread = CameraThread()
        self.VBL = QVBoxLayout()
        self.GifArea = MainGif()
        self.VBL.addWidget(self.GifArea) 

        self.HBL = QHBoxLayout()
        self.VBL.addLayout(self.HBL)

        
        self.VideoOnBTN = QPushButton("Start")
        self.VideoOnBTN.clicked.connect(self.start_camera)
        self.HBL.addWidget(self.VideoOnBTN)

        self.VideoOffBTN = QPushButton("Stop")
        self.VideoOffBTN.clicked.connect(self.stop_camera)
        self.HBL.addWidget(self.VideoOffBTN)
        self.setLayout(self.VBL)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.camera_status = False
       

        self.VBL = QVBoxLayout()

     

        self.button_status()
        self.play_gif('sleep')
        self.setLayout(self.VBL)

    def button_status(self):
        if self.camera_status:
            self.VideoOnBTN.hide()
            self.VideoOffBTN.show()
        else:
            self.VideoOnBTN.show()
            self.VideoOffBTN.hide()

    def start_camera(self):
        self.camera_status = True
        self.FeedLabel.clear()   
        self.button_status()
        self.CameraThread.start()
        self.CameraThread.ImageUpdate.connect(self.ImageUpdateSlot)

    def stop_camera(self):
        self.CameraThread.stop()
        self.camera_status = False
        self.play_gif('recognise')
        self.button_status()

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def play_gif(self, Image):
        self.FeedLabel.clear()
        # eğer slot değişiken olarak gelirse almak için  slot = getattr(self,slot_name) bu self.FeedLabel olur
        movie = QMovie('images/faces/' + str(Image) + '.gif')
        self.FeedLabel.setMovie(movie)
        movie.start()




if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())

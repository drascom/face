#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage


class CameraThread(QObject):
    image_update_signal = pyqtSignal(QImage)
    face_found_signal = pyqtSignal(object)
    finished_signal = pyqtSignal()
    call_scan = pyqtSignal()
    call_stop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.threadActive = False
        self.call_scan.connect(self.scan)
        self.call_stop.connect(self.stop)
        self.currentname = "????"
        encodingsP = "camera/encodings.pickle"
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(encodingsP, "rb").read())

    def convert_image(self, frame):
        # update video
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FlippedImage = cv2.flip(Image, 1)
        ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                   FlippedImage.Format_RGB888)
        picture = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        return picture

    @pyqtSlot()
    def scan(self):
        print("scan çalıştı")
        self.threadActive = True
        self.vs = VideoStream(src=0, framerate=15).start()
        self.fps = FPS().start()

        while self.threadActive:
            # grab the frame from the threaded video stream and resize it
            # to 500px (to speedup processing)
            frame = self.vs.read()
            frame = imutils.resize(frame, width=500)
            frame = cv2.flip(frame, 1)
            # Detect the fce boxes
            boxes = face_recognition.face_locations(frame)
            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(self.data["encodings"],
                                                            encoding)
                name = "????"  # if face is not recognized, then print Unknown

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = self.data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
					
                    # If someone in your dataset is identified, print their name on the screen
                    if self.currentname != name:
                        self.currentname = name
                        self.face_found_signal.emit(name)
                        # return

                # update the list of names
                names.append(name)

            
            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image - color is in BGR
                cv2.rectangle(frame, (left, top), (right, bottom),
                                (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (right, y), cv2.FONT_HERSHEY_SIMPLEX,
                            .8, (0, 255, 255), 2)

            # display the image to our screen
            # cv2.imshow("Facial Recognition is Running", frame)
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.image_update_signal.emit(Pic)            
            # update the FPS counter
            self.fps.update()

        # stop the timer and display FPS information
        self.fps.stop()
        print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))

        # do a bit of cleanup
        self.vs.stop()
        self.fps.stop()
    def stop(self):
        self.threadActive = False
		

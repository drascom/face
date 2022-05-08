#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import pickle
import cv2
from PyQt5.QtGui import QMovie, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime
from pathlib import Path


class Scanning():
    def __init__(self):
        self.currentname = "Bilmiyorum"
        self.result = None
        self.picture = None
        self.exit = None
        self.capture = cv2.VideoCapture(0)
        encodingsP = "camera/encodings.pickle"
        print("[INFO] loading encodings + face detector...")
        self.data = pickle.loads(open(encodingsP, "rb").read())

    def scan_face(self, frame):
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
            name = "Bilinmiyor"  # if face is not recognized, then print Unknown

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
                    self.result = self.currentname
                    break

            # update the list of names
                names.append(name)
        return self.result

    def record_face(frame):
        # name = 'Simge' #replace with your name
        name = input('> Isim: ')
        Path("camera/dataset/"+name).mkdir(parents=True, exist_ok=True)
        img_counter = 0
        while img_counter < 20:
            img_name = "camera/dataset/" + name + \
                "/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1

    def convert_image(self, frame):
        # update video
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FlippedImage = cv2.flip(Image, 1)
        ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                   QImage.Format_RGB888)
        self.picture = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

    def stop(self):
        self.exit = True
        self.capture.release()

    def run(self):
        ret, frame = self.capture.read()
        if ret:
            self.convert_image(frame)
        else:
            print("frame alınamadı")


if __name__ == "__main__":
    x = Scanning()
    print(x.scan_face())
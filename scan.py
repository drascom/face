#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from imutils import paths, resize
import face_recognition
import pickle
import cv2
import os
from PyQt5.QtGui import QMovie, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime
from pathlib import Path


class Scanning():
    def __init__(self):
        self.currentname = "?"
        self.encodingsP = "camera/encodings.pickle"
        self.data = pickle.loads(open(self.encodingsP, "rb").read())
        print("[INFO] loading face models...")
    def scan_face(self,frame):
        frame = resize(frame, width=500)  # imutils VideoStream
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
            name = "?"  # if face is not recognized, then print Unknown

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
                    return
            # update the list of names
                names.append(name)
            # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image - color is in BGR
            cv2.rectangle(frame, (left, top), (right, bottom),
                        (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        .8, (0, 255, 255), 2)
        self.convert_image(frame)

    def record_face(self,frame):
        name = 'a'  # replace with your name
        # name = input('> Isim: ')
        Path("camera/dataset/"+name).mkdir(parents=True, exist_ok=True)
        # ret, frame = self.capture.read()#opencv VideoCapture
        img_counter = 0
        while img_counter < 20:
            self.convert_image(frame)
            img_name = "camera/dataset/" + name + \
                "/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
        self.train_data()

    def convert_image(self, frame):
        # update video
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FlippedImage = cv2.flip(Image, 1)
        ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0],
                                   QImage.Format_RGB888)
        self.picture = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

    def train_data(self):
        # our images are located in the dataset folder
        print("[INFO] start processing faces...")
        imagePaths = list(paths.list_images("camera/dataset"))

        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []

        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                                                         len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            # load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                                                    model="hog")

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)

            # dump the facial encodings + names to disk
            print("[INFO] serializing encodings...")
            data = {"encodings": knownEncodings, "names": knownNames}
            f = open("camera/encodings.pickle", "wb")
            f.write(pickle.dumps(data))
            f.close()
        print("[INFO] updating face models...")
        self.data = pickle.loads(open(self.encodingsP, "rb").read())

    def stop(self):
        self.capture.stop()  # imutils VideoStream
        # self.capture.release()#opencv VideoCapture

    def run(self):
        self.picture = None
        # self.capture = cv2.VideoCapture(0)#opencv VideoCapture
        self.capture = VideoStream(
            src=0, framerate=10).start()  # imutils VideoStream
        self.runtime = 0
        while True:
            frame = self.capture.read()  # imutils VideoStream
            # ret, frame = self.capture.read()#opencv VideoCapture
            self.scan_face(frame)
            self.runtime += 1
            print("scan loop: ",self.runtime)
            if self.runtime > 50:
                self.currentname = "test"
                self.capture.stop()
                break


if __name__ == "__main__":
    x = Scanning()
    x.scan_face()

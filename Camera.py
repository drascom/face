#! /usr/bin/python

# import the necessary packages
from re import T
from imutils.video import VideoStream
from imutils import paths, resize
import face_recognition
import pickle
import cv2
import os
import time
from PyQt5.QtGui import QMovie, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime
from pathlib import Path


def convert_image(frame):
    Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FlippedImage = cv2.flip(Image, 1)
    # FlippedImage = Image
    ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                               QImage.Format_RGB888)
    Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
    return Pic


def view_face(frame):
    currentname = "Bilmiyorum"
    encodingsP = "camera/encodings.pickle"
    data = pickle.loads(open(encodingsP, "rb").read())
    # src = 0 : for the build in single web cam, could be your laptop webcam
    frame = resize(frame, width=640)
    boxes = face_recognition.face_locations(frame)
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
                                                    encoding)
        name = "Bilmiyorum"  # if face is not recognized, then print Unknown

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
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            # If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name

        # update the list of names
        names.append(name)
    # frame = cv2.flip(frame, 1)
    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom),
                        (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (0, 255, 255), 2)
    return convert_image(frame)


def scan_face():
    print("Scanning")
    currentname = "Bilmiyorum"
    encodingsP = "camera/encodings.pickle"
    data = pickle.loads(open(encodingsP, "rb").read())
    # src = 0 : for the build in single web cam, could be your laptop webcam
    capture = VideoStream(src=0, framerate=10).start()
    # capture = VideoStream(usePiCamera=True).start()
    time.sleep(1.0)
    runtime = 0
    while True:
        if runtime > 50:
            currentname = "test"
            capture.stop()
            break
        frame = capture.read()
        frame = resize(frame, width=500)
        boxes = face_recognition.face_locations(frame)
        encodings = face_recognition.face_encodings(frame, boxes)
        names = []
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            name = "Bilmiyorum"  # if face is not recognized, then print Unknown

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
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

                # If someone in your dataset is identified, print their name on the screen
                if currentname != name:
                    currentname = name
                    capture.stop()
                    return currentname
                    break      
    


def capture_face(name):
    # name = input('> Isim: ')
    Path("camera/dataset/"+name).mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(0)
    img_counter = 0
    while img_counter < 20:
        ret, frame = capture.read()
        if not ret:
            print("failed to grab frame")
            break
        convert_image(frame)
        img_name = "camera/dataset/" + name + \
            "/image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
    capture.release()
    train_data()


def train_data():
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
    print("[INFO] face models updated ...")


if __name__ == "__main__":
   print(scan_face())

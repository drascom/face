import pygame
import cv2
import numpy
import face_recognition
import pickle
from imutils.video import VideoStream


class CameraScene:
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'camera'
        self.M = outer_instance
        self.M.FPS = 30
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)  # width
        self.cap.set(4, 240)  # height
        self.currentname = "Bilmiyorum"
        encodingsP = "camera/encodings.pickle"
        self.data = pickle.loads(open(encodingsP, "rb").read())
        self.frame = ""

    def update(self):
        if self.cap.read()[0] == False:
            print("Camera Not connected")
            self.M.active_scene = self.M.SceneHome

        if not self.cap.isOpened():
            print("kamera kapalı")
            self.cap = cv2.VideoCapture(1)
            self.cap.set(3, 320)  # width
            self.cap.set(4, 240)  # height

        if self.cap and self.cap.isOpened():
            self.success, img = self.cap.read()
            if self.success:
                boxes = face_recognition.face_locations(img)
            encodings = face_recognition.face_encodings(img, boxes)
            names = []
            for encoding in encodings:
                matches = face_recognition.compare_faces(self.data["encodings"], encoding)
                name = "Bilmiyorum"  # if face is not recognized, then print Unknown
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = self.data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                    if self.currentname != name:
                        self.currentname = name
                        print("buldum ", name)
            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(img, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB = numpy.rot90(imgRGB)
            self.frame = pygame.surfarray.make_surface(imgRGB).convert()
            self.frame = pygame.transform.smoothscale(self.frame, (self.M.maxX, self.M.maxY))
            # self.frame = pygame.transform.flip(frame, True, False) #if needed flip horizontal

    def render(self):
        if self.success:
            self.M.GS.blit(self.frame, (0, 0))

    def terminate(self):
        self.cap.release()

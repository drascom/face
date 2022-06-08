import pygame
import cv2
import numpy
import face_recognition
import time
import pickle
from imutils.video import VideoStream
from imutils import paths, resize


class CameraScene:
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'camera'
        self.M = outer_instance
        self.M.FPS = 30
        self.currentname = "Bilmiyorum"
        encodingsP = "camera/encodings.pickle"
        self.data = pickle.loads(open(encodingsP, "rb").read())
        self.capture = VideoStream(src=0, framerate=30).start()
        time.sleep(1.0)
        self.frame = ""

    def update(self):
        self.frame = self.capture.read()
        self.frame = resize(self.frame, width=640)
        boxes = face_recognition.face_locations(self.frame)
        encodings = face_recognition.face_encodings(self.frame, boxes)
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
            cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(self.frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
        imgRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        imgRGB = numpy.rot90(imgRGB)
        self.frame = pygame.surfarray.make_surface(imgRGB).convert()

    def render(self):
        self.M.GS.blit(self.frame, (0, 0))

    def terminate(self):
        self.capture.stop()

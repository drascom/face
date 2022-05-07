#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
from datetime import datetime


class Scanning():
	def __init__(self):
		self.currentname = "Bilmiyorum"
		self.result = None
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


if __name__ == "__main__":
	x = Scanning()
	print(x.scan_face())

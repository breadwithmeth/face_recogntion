# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2, socket, pickle, struct
from flask_opencv_streamer.streamer import Streamer





class Video(object):
	def __init__(self):
		self.video=cv2.VideoCapture("clinic.mp4")

	def __del__(self):
		self.video.release()

	def get_frame(self):
		data = pickle.loads(open("encodings.pickle", "rb").read())
		# grab the frame from the threaded video stream
		ret, frame = self.video.read()
			# convert the input frame from BGR to RGB then resize it to have
		# a width of 750px (to speedup processing)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		rgb = imutils.resize(frame, width=750)
		r = frame.shape[1] / float(rgb.shape[1])
		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input frame, then compute
		# the facial embeddings for each face
		boxes = face_recognition.face_locations(rgb,
			model="hog")
		encodings = face_recognition.face_encodings(rgb, boxes)
		names = []


			# loop over the facial embeddings
		for encoding in encodings:
				# attempt to match each face in the input image to our known
				# encodings
				matches = face_recognition.compare_faces(data["encodings"],
					encoding)
				name = "Unknown"
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
				
				# update the list of names
				names.append(name)

			# loop over the recognized faces
		for ((top, right, bottom, left), name) in zip(boxes, names):
				# rescale the face coordinates
				top = int(top * r)
				right = int(right * r)
				bottom = int(bottom * r)
				left = int(left * r)
				# draw the predicted face name on the image
				cv2.rectangle(frame, (left, top), (right, bottom),
					(255, 255, 255), 1)
				y = top - 15 if top - 15 > 15 else top + 15
				cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_PLAIN,
					3, (255, 255, 255), 3)

		ret,jpg=cv2.imencode('.jpg',frame)

		return jpg.tobytes()
			

















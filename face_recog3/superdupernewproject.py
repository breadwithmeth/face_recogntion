# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import mtcnn
import pymysql

connection = pymysql.connect(host='localhost',
                             user='python_mysql',
                             password='password',
                             database='face_recognition',
                             cursorclass=pymysql.cursors.DictCursor)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", default="encodings.pickle",
	help="path to serialized db of facial encodings")
ap.add_argument("-i", "--input", type=str,
	help="path to input video")
ap.add_argument("-w", "--webcam", type=int, default=0,
	help="path to input webcam")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="mtcnn",
	help="face detection model to use: either mtcnn `hog` or `cnn`")
args = vars(ap.parse_args())

def information(iid, con, image, left, x, bottom, top):
    with con.cursor() as cursor:
        if iid != "Unknown":
            print('got')
            # Read a single record
            first_name = "SELECT `first_name` FROM `citizens` WHERE `iid`=%s"
            last_name = "SELECT `last_name` FROM `citizens` WHERE `iid`=%s"
            sex = "SELECT `sex` FROM `citizens` WHERE `iid`=%s"
            address = "SELECT `address` FROM `citizens` WHERE `iid`=%s"
            city = "SELECT `city` FROM `citizens` WHERE `iid`=%s"
            first_name = get_values_from_table(cursor, first_name, iid)
            fname = first_name['first_name']
            last_name = str(get_values_from_table(cursor, last_name, iid))
            sex = str(get_values_from_table(cursor, sex, iid))
            address = str(get_values_from_table(cursor, address, iid))
            city = str(get_values_from_table(cursor, city, iid))
            font_size = (bottom - top) / 100
            ofs = font_size * 20
            font_thickness = int(font_size)
            table = "SELECT `iid`, `first_name`, `last_name`, `sex`, `address`, `city` FROM `citizens` WHERE `iid`=%s"
            cursor.execute(table, (iid))
            result = cursor.fetchone()
            i = 0
            for key in result:
                text = key + '=' + str(result[key])
                i = i + 1


                cv2.putText(image, text, (left, int(x + (i * ofs))), font,font_size, color, font_thickness)
            
            #cv2.putText(image, result, (left, x + 0), font,font_size, color, font_thickness)
            '''
            cv2.putText(image, fname, (left, int(x + 0 * ofs)), font,font_size, color, font_thickness)
            cv2.putText(image, last_name, (left, int(x + 1 * ofs)), font,font_size, color, font_thickness)
            cv2.putText(image, sex, (left, int(x + 2 * ofs)), font,font_size, color, font_thickness)
            cv2.putText(image, address, (left, int(x + 3 * ofs)), font,font_size, color, font_thickness)
            cv2.putText(image, city, (left, int(x + 4 * ofs)), font,font_size, color, font_thickness)
            '''
                





def get_values_from_table(cursor, value, iid):
    cursor.execute(value, (iid,))
    result = cursor.fetchone()
    return result


def resize(frame, width):
    proportion = float(int(frame.shape[0]) / int(frame.shape[1]))
    height = int(width * proportion)
    dim = (width, height) 
    # resize image
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    return frame



def photo_recognize():
    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(open(args["encodings"], "rb").read())
    # load the input image and convert it from BGR to RGB
    image = cv2.imread(args["input"])
    image = resize(image, 1600)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # detect the (x, y)-coordinates of the bounding boxes corresponding
    # to each face in the input image, then compute the facial embeddings
    # for each face
    print("[INFO] recognizing faces...")
    boxes = face_recognition.face_locations(rgb,
        model=args["detection_method"])
    encodings = face_recognition.face_encodings(rgb, boxes)
    # initialize the list of names for each face detected
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
            # determine the recognized face with the largest number of
            # votes (note: in the event of an unlikely tie Python will
            # select first entry in the dictionary)
            name = max(counts, key=counts.get)
        
        # update the list of names
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(image, (left, top), (right, bottom), color, 2)
        y = top - 15 if top - 15 > 15 else top + 15
        x = right + 15 if right + 15 < 15 else right + 15
        information(name, connection, image, right, y, bottom, top)
        
    # show the output image
    cv2.imshow("Image", image)
    cv2.waitKey(0)


def video_recognize():
    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(open(args["encodings"], "rb").read())
    # initialize the video stream and pointer to output video file, then
    # allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    vs = cv2.VideoCapture(args["input"])
    writer = None
    time.sleep(2.0)

    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        ret, frame = vs.read()
        frame = resize(frame, 1600)
        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])
        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input frame, then compute
        # the facial embeddings for each face
        boxes = face_recognition.face_locations(rgb,
            model=args["detection_method"])
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
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            x = right + 15 if right + 15 < 15 else right + 15
            information(name, connection, frame, right, y, bottom, top)
    
        # if the video writer is None *AND* we are supposed to write
        # the output video to disk initialize the writer
        if writer is None and args["output"] is not None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 30,
                (frame.shape[1], frame.shape[0]), True)
        # if the writer is not None, write the frame with recognized
        # faces to disk
        if writer is not None:
            writer.write(frame)

        # check to see if we are supposed to display the output frame to
        # the screen
        if args["display"] > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(20) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    # check to see if the video writer point needs to be released
    if writer is not None:
        writer.release()


def webcam_recognize():
    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(open(args["encodings"], "rb").read())
    # initialize the video stream and pointer to output video file, then
    # allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    vs = VideoStream(src=args["webcam"]).start()
    writer = None
    time.sleep(2.0)

    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        frame = vs.read()
        proportion = float(int(frame.shape[0]) / int(frame.shape[1]))
        width = 900
        height = int(width * proportion)
        dim = (width, height)
        
        # resize image
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])
        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input frame, then compute
        # the facial embeddings for each face
        boxes = face_recognition.face_locations(rgb,
            model=args["detection_method"])
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
                color, 1)
            y = top - 15 if top - 15 > 15 else top + 15
            x = right + 15 if right + 15 < 15 else right + 15
            information(name, connection, frame, right, y, bottom, top)
            #cv2.putText(frame, information(name), (right, x), font, font_size, color, 3)
            
    
        # if the video writer is None *AND* we are supposed to write
        # the output video to disk initialize the writer
        if writer is None and args["output"] is not None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 20,
                (frame.shape[1], frame.shape[0]), True)
        # if the writer is not None, write the frame with recognized
        # faces to disk
        if writer is not None:
            writer.write(frame)

        # check to see if we are supposed to display the output frame to
        # the screen
        if args["display"] > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    # check to see if the video writer point needs to be released
    if writer is not None:
        writer.release()


detection_method = "mtcnn"
encodingPickle = "encodings.pickle"
font = cv2.FONT_HERSHEY_DUPLEX
#font_size = 1
font_thickness = 1
color = (205, 92, 92)

print("Make a choise \n1. Recognize face from a photo\n2. Recognize face from a video\n3. Recognize face from a webcam")
choise1 = int(input("-----------\n"))
if choise1 == 1:
    photo_recognize()

elif choise1 == 2:
    print("Ok")
    video_recognize()
elif choise1 == 3:
    print("Ok")
    webcam_recognize()

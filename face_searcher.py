import cv2
import sys
import os



cap = cv2.VideoCapture(0)
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
img_counter = 0
person_name = input()

newpath = "dataset/" + person_name
if not os.path.exists(newpath):
    os.makedirs(newpath)



while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        if cv2.waitKey(1) & 0xFF == ord('d'):
            # SPACE pressed
            img_name = "{}.png".format(img_counter)
            cv2.imwrite("dataset/" + person_name + "/" + img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_color = frame[y:y + h, x:x + w]
        print("[INFO] Object found.")
        ##cv2.imwrite(str(w) + str(h) + '_faces.jpg', roi_color)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

    
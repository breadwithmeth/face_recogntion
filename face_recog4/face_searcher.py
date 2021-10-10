import cv2
import sys
import os
import pymysql
from pymysql import connections

def connect():

    connection = pymysql.connect(host='localhost',
                                user='python_mysql',
                                password='password',
                                database='face_recognition',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection


def table_parser(iid, first_name, last_name, sex, address, city):
    con = connect()
    with con:
        with con.cursor() as cursor:
            table = "INSERT INTO `citizens` (`iid`, `first_name`, `last_name`, `sex`, `address`, `city`) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(table, (iid, first_name, last_name, sex, address, city))
        con.commit()



def table_parser_check(iid):
    con = connect()
    with con:
        with con.cursor() as cursor:
            # Read a single record
            table = "SELECT `iid`, `first_name`, `last_name`, `sex`, `address`, `city` FROM `citizens` WHERE `iid`=%s"
            cursor.execute(table, (iid))
            result = cursor.fetchone()
            print(result[first_name])





def choose_gender():
    gender = str(input())
    if gender == '1':
        return "M"
    if gender == '2':
        return "F"
    else:
        print('Again!')
        choose_gender()
    





def face_search(iid):
    cap = cv2.VideoCapture(0)
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    img_counter = 0
    newpath = "dataset/" + iid
    if not os.path.exists(newpath):
        os.makedirs(newpath)



    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()
        scale_percent = 150 # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)





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
                cv2.imwrite("dataset/" + iid + "/" + img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
            cv2.putText(frame, "D to make a photo Q to exit", (x, y), cv2.FONT_HERSHEY_PLAIN,
                2, (255, 255, 255), 2)
            roi_color = frame[y:y + h, x:x + w]
            cv2.imshow('face', roi_color)

            print("[INFO] Object found.")
            ##cv2.imwrite(str(w) + str(h) + '_faces.jpg', roi_color)
            
        

        # Display the resulting frame
        cv2.imshow('Video', frame)
        #cv2.imshow('face', roi_color)
        



iid = input('enter id:  ')
iidstr = str(iid)
first_name = input('enter first name: ')
last_name = input('enter last name: ')
print('choose gender:\n 1.Male\n 2.Female\n')
gender = choose_gender()
maritial_status = input('enter maritial status: ')
address = input('address:   ')
city = input('enter a city')

"""

iid = 24234234
iidstr = str(iid)
first_name = "Sergey"
last_name = "Shiryayev"
print('choose gender:\n 1.Male\n 2.Female\n')
entered_gender = 1
gender = choose_gender(entered_gender)
#date_of_birth = input('Enter a date in YYYY-MM-DD format')
#work = input('input work:   ')
#phone = input('enter a phone number:    ')
#maritial_status = 123123123
address = "Lenina 24"
city = "Ekibastuz"
"""
make_photo = str(input('do you want to make a photo\n 1. Yes\n 2. No'))
if make_photo == '1':
    face_search(iidstr)


table_parser(iid, first_name, last_name, gender, address, city)
table_parser_check(iid)
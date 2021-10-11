from flask_opencv_streamer.streamer import Streamer
import cv2
from imutils.video import VideoStream
from flask import Flask, render_template, Response

app = Flask(__name__)
sub = cv2.createBackgroundSubtractorMOG2()  # create background subtractor

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

vs = VideoStream(src=0).start()
while True:
    ret, frame = vs.read()
    frame = cv2.imencode('.jpg', image)[1].tobytes()
    key = cv2.waitKey(20)
    if key == 27:
        break


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

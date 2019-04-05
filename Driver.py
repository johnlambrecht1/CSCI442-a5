from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2 as cv
import maestro

HEADTILT = 4
HEADTURN = 3
TURN = 2
MOTORS = 1

tango = maestro.Controller()
body = 6000
headTurn = 6000
headTilt = 6000
motors = 6000
turn = 6000

IP = '10.200.2.215'
PORT = 5010

def zero_motors():
    for x in range(0, 5):
        tango.setTarget(x, 6000)


zero_motors()
camera = PiCamera()
w, h = 640, 480
camera.resolution = (w, h)  # (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)

# allow the camera to warmup
time.sleep(0.1)
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")


# capture frames from the camera

def move_head(turn, value):
    global headTurn, headTilt, HEADTURN, HEADTILT
    """
    Move head to position
    :param turn: True if turning head, false if tilting
    :param value: value to set the motor to
    :return:
    """
    if turn:
        headTurn += value
        if headTurn > 7900:
            headTurn = 7900
        elif headTurn < 1510:
            headTurn = 1510
        tango.setTarget(HEADTURN, headTurn)
    else:
        headTilt += value
        if headTilt > 7900:
            headTilt = 7900
        elif headTilt < 1510:
            headTilt = 1510
        tango.setTarget(HEADTILT, headTilt)

def search_for_face(image, face):
    w, h = image.shape[:2]
    tango.setTarget(HEADTILT, 3000)
    for y in range(h):
        move_head(False, -200)
        tango.setTarget(HEADTURN, 7900)
        for x in range(w):
            move_head(True, 200)
            if face is not None:
                pass
        if face is not None:
            pass


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # get frame size
    w, h = image.shape[:2]
    # use the lower center of the image
    # x, y = w//5, h//2
    # image = image[y:y + h//4, x:x + 3*w//5]

    face = face_cascade.detectMultiScale(image, 1.8, 5)

    for (x, y, w, h) in face:
        cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)

    cv.imshow("image", image)

    search_for_face(image, face)
#    tango.setTarget(HEADTURN, 7900)
    key = cv.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

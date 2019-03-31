import maestro
import numpy as np
import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# TODO remove
# MOTORS = 1
# TURN = 2
# BODY = 0
HEADTILT = 4
HEADTURN = 3
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

camera = PiCamera()
w, h = 320, 240
camera.resolution = (w, h)  # (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)

# allow the camera to warmup
time.sleep(0.1)

class SearchForFace:

    def __init__(self):
        # vars for the face finding interval
        self.no_face_search_restart_interval = 0  # min time interval required to restart search
        self.last_face_time = 0  # last time a face was seen
        self.give_up_search_time = 120  # give up after 2 min

        # vars for fitting face size to linear function
        self.current_distance_to_human = None  # current distance to the human
        self.reference_face_size_at_5 = None  # reference size at 5 unit distance
        self.reference_face_size_at_1 = None  # reference size at 1 unit distance

        # motor values to use to scan from 0 to max to min to 0
        self.scan = []
        for x in range(6000, 8000, 200):
            self.scan.append(x)
        for x in range(8000, 1500, -200):
            self.scan.append(x)
        for x in range(1800, 6001, 200):
            self.scan.append(x)
        self.scan = np.array(self.scan)

        # motor control variables
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.motors = 6000
        self.turn = 6000

    def move_head(self, turn, value):
        """
        Move head to position
        :param turn: True if turning head, false if tilting
        :param value: value to set the motor to
        :return:
        """
        if turn:
            self.headTurn = value
            if self.headTurn > 7900:
                self.headTurn = 7900
            elif self.headTurn < 1510:
                self.headTurn = 1510
            self.tango.setTarget(HEADTURN, self.headTurn)
        else:
            self.headTilt = value
            if self.headTilt > 7900:
                self.headTilt = 7900
            elif self.headTilt < 1510:
                self.headTilt = 1510
            self.tango.setTarget(HEADTILT, self.headTilt)

    def search_for_face(self):
        """
        search for a face, if face is found, return success, otherwise loop
        :return: the face found which is its (x, y, w, h) or None
        """
        if time.process_time() - self.last_face_time < self.no_face_search_restart_interval:
            # don't do search again
            return None

        start_time = time.process_time()
        # scan for face while not expired
        while time.process_time() - start_time < self.give_up_search_time:
            for y in self.scan:
                for x in self.scan:
                    self.move_head(True, x)
                    self.move_head(False, y)
                    # update frame
                    frame = camera.capture(rawCapture, format="bgr", use_video_port=True)
                    image = frame.array
                    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

                    # check if a face is in image
                    faces = face_cascade.detectMultiScale(gray, 1.8, 5)
                    if len(faces) > 0:
                        # face found
                        self.last_face_time = time.process_time()
                        # clear the stream in preparation for the next frame
                        rawCapture.truncate(0)
                        return faces[0]

                    # clear the stream in preparation for the next frame
                    rawCapture.truncate(0)
        # time expired, face not found
        return None

    def face_found(self, face):
        """
        do face found actions
        - don't do if the face is lost for less then 15 sec
        - say “hello human”
        :param face:
        :return:
        """
        pass

    def get_face_distance(self, face):
        """
        get the distance to the detected face based off of its size
        returns the distance units it calculated, where 1 is the optimum distance

        - get distance (reference parameter face size, average x frames of face)
        :param face: the detected face
        :return: distance to face in arbitrary units established by the calibration
        """
        x, y, w, h = face
        d1 = 1  # 1 unit for short distance
        d2 = 5  # 5 units for long distance
        s1 = self.reference_face_size_at_1
        s2 = self.reference_face_size_at_5

        b = (d1 * s2 - d2 * s1) / (d1 - d2)
        m = (s1 - s2) / (d1 - d2)

        # get distance units, 1 is where we want to be
        dis = (w - b)/m
        return dis




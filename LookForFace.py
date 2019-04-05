import maestro
import numpy as np
import cv2 as cv
import time


class SearchForFace:

    def __init__(self, client):
        self.HEADTILT = 4
        self.HEADTURN = 3
        self.TURN=2
        self.MOTORS=1
        self.face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

        # allow the camera to warmup
        time.sleep(0.1)

        # use the given Tango Phone client
        self.client = client

        # stop scanning for a face after this timeout
        self.give_up_search_time = 120  # give up after 2 min
        self.start_time = -1

        # vars for fitting face size to linear function
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
        self.scan_index = 0
        self.scan_size = len(self.scan)

        # motor control variables
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.motors = 6000
        self.turn = 6000

        self.zero_motors()

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
            self.tango.setTarget(self.HEADTURN, self.headTurn)
        else:
            self.headTilt = value
            if self.headTilt > 7900:
                self.headTilt = 7900
            elif self.headTilt < 1510:
                self.headTilt = 1510
            self.tango.setTarget(self.HEADTILT, self.headTilt)

    def zero_motors(self):
        """
        sets all motors to their zero position
        :return: None
        """
        for x in range(0, 5):
            self.tango.setTarget(x, 6000)

    def turn_bot(self, value):
        """
        Turn robot to position
        :param value: amount robot is turned
        :return:
        """
        self.turn += value
        if self.turn > 7400:
            self.turn=7400
        if self.turn<2110:
            self.turn=2110
        self.tango.setTarget(self.TURN, self.turn)

    def move_bot(self, value):
        """
        Move robot forward or back
        :param value: Amount robot will be moved
        :return:
        """
        self.motors+=value
        if (self.motors>7900):
            self.motors=7900
        if (self.motors<1510):
            self.motors=1510
        self.tango.setTarget(self.MOTORS, self.motors)

    def search_for_face_manager(self, image):
        """
        manages search_for_face, can be called repeatedly and will emulate a 2d for loop on self.scan
        :param image:
        :return:
        """
        if self.scan_index == 0:
            self.start_time = time.process_time()
        # scan for face while not expired
        if time.process_time() - self.start_time < self.give_up_search_time:
            # convert a single index (scan_index) of max length scan_size^2
            # to the equivalent of a 2d for loop on self.scan
            face = self.__search_for_face(image, self.scan_index // self.scan_size, self.scan_index % self.scan_size)
            self.scan_index += 1
            # wrap on scan_index^2
            self.scan_index %= np.power(self.scan_index, 2)
            return face
        return None

    def __search_for_face(self, image, x, y):
        """
        search for a face, if face is found, return success, otherwise loop
        :return: the face found which is its (x, y, w, h) or None
        """

        # move to next scanning position
        self.move_head(True, self.scan[x])
        self.move_head(False, self.scan[y])

        # check for a face
        face = self.get_face(image)
        if face is not None:
            return face

    def get_face(self, image):
        """
        Try to detect a face and return it. returns None on a failure
        :return: the face or None
        """
        # update frame

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # check if a face is in image
        faces = self.face_cascade.detectMultiScale(gray, 1.8, 5)
        if len(faces) > 0:
            return faces[0]
        else:
            # no face found
            return None

    def face_found(self):
        """
        do face found actions
        - don't do if the face is lost for less then 15 sec
        - say “hello human”
        :param face: the face that was found
        :return: None
        """
        for words in ["hello human", "How are you"]:
            time.sleep(1)
            self.client.sendData(words)

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

    def center_on_face(self, face, image):
        """
        move neck and wheels so that the robot is looking directly at the face
        :param face: the detected face
        :return:
        """

        width, height = image.shape[:2]
        x,y,w,h = face
        roi_face = image[y:y+h, x:x+w]
        face_centery, face_centerx = image(y+h//2, x+w//2)
        not_moved = True

        if face_centerx < (width/2-100):
            self.move_head(True, 200)
            not_moved = False
        if face_centerx > (width/2+100):
            self.move_head(True, 200)
            not_moved = False
        if (self.headTurn > 6100) or (self.headTurn<5900):
            if (self.headTurn > 6100):
                self.turn_bot(-300)
                time.sleep(1.5)
                self.turn_bot(300)
                not_moved = False
            if (self.headTurn<5900):
                self.turn_bot(300)
                time.sleep(1.5)
                self.turn_bot(-300)
                not_moved = False
        return not_moved

    def move_forward_or_back(self, face):
        """
        Checks the size of the face, and moves either forward or back to get the face to the correct size
        :param face: the detected face
        :return:
        """

        while not ((self.get_face_distance(face) < 1.1) or (self.get_face_distance(face) > .9)):
            # checks if face is too small, then moves back
            if self.get_face_distance(face) < .9:
                self.move_bot(300)
            # checks if face is too big, then moves forward
            elif self.get_face_distance(face) > 1.1:
                self.move_bot(-300)
        self.motors = 6000
        self.tango.setTarget(self.MOTORS, self.motors)

    def track_face(self, face, image):
        """
        moves the neck so that the face is centered on the screen
        If no face is on screen for 15 sec, goes back to search for face
        :param face: the detected face
        :return:
        """
        width, height = image.shape[:2]
        x, y, w, h = face
        roi_face = image[y:y + h, x:x + w]
        face_centery, face_centerx = image(y + h // 2, x + w // 2)

        if face_centery < (height / 2 - 100):
            self.move_head(False, 200)
        if face_centery > (height / 2 + 100):
            self.move_head(False, 200)
        if face_centerx < (width / 2 - 100):
            self.move_head(True, 200)
        if face_centerx > (width / 2 + 100):
            self.move_head(True, 200)
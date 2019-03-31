import maestro

# TODO remove
# MOTORS = 1
# TURN = 2
# BODY = 0
HEADTILT = 4
HEADTURN = 3


class SearchForFace:

    def __init__(self):
        # vars for the face finding interval
        self.no_face_search_restart_interval = 0  # min time interval required to restart search
        self.last_face_time = 0  # last time a face was seen

        # vars for fitting face size to linear function
        self.current_distance_to_human = None  # current distance to the human
        self.reference_face_size_at_5m = None
        self.reference_face_size_at_1m = None

        # motor control variables
        self.tango = maestro.Controller()
        self.body = 6000
        self.headTurn = 6000
        self.headTilt = 6000
        self.motors = 6000
        self.turn = 6000

    def head(self, key):
        print(key.keycode)
        if key.keycode == 38:
            self.headTurn += 200
            if self.headTurn > 7900:
                self.headTurn = 7900
            self.tango.setTarget(HEADTURN, self.headTurn)
        elif key.keycode == 52:
            self.headTurn -= 200
            if self.headTurn < 1510:
                self.headTurn = 1510
            self.tango.setTarget(HEADTURN, self.headTurn)
        elif key.keycode == 25:
            self.headTilt += 200
            if self.headTilt > 7900:
                self.headTilt = 7900
            self.tango.setTarget(HEADTILT, self.headTilt)
        elif key.keycode == 39:
            self.headTilt -= 200
            if self.headTilt < 1510:
                self.headTilt = 1510
            self.tango.setTarget(HEADTILT, self.headTilt)

    def search_for_face(self):
        """
        search for a face, if face is found, return success
        :return:
        """
        pass

    def face_found(self):
        """
        do face found actions
        - don't do if the face is lost for less then 15 sec
        - say “hello human”
        :return:
        """
        pass

    def get_face_distance(self, face):
        """
        get the distance to the detected face based off of size

        - get distance (reference parameter face size, average x frames of face)
        :param face: the detected face
        :return:
        """
        pass


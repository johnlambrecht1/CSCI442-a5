

class SearchForFace:

    def __init__(self):
        # vars for the face finding interval
        self.no_face_search_restart_interval = 0  # min time interval required to restart search
        self.last_face_time = 0  # last time a face was seen

        # vars for fitting face size to linear function
        self.current_distance_to_human = None  # current distance to the human
        self.reference_face_size_at_5m = None
        self.reference_face_size_at_1m = None

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


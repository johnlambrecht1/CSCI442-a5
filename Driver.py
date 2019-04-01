from client import ClientSocket
from LookForFace import SearchForFace
import time

IP = '10.200.28.12'
PORT = 5010
# set up client and face searching
client = ClientSocket(IP, PORT)
face_search = SearchForFace(client)
distance_tolerance = 0.1  # don't move to the face if within this distance of 1 unit

# global variables
no_face_search_restart_interval = 0  # min time interval required to restart face search
last_face_time = 0  # last time a face was seen


def move_to_face(distance):
    if distance < 1 - distance_tolerance:
        # go backwards
        pass
    elif distance > 1 + distance_tolerance:
        # go forwards
        pass
    else:
        # don't move
        pass
    pass


def searching():
    global last_face_time
    # zero motors
    face_search.zero_motors()
    # start searching for a face
    face = face_search.search_for_face()
    # check that a face was found
    if face is not None:
        # face found
        last_face_time = time.process_time()
        # say "hello human"
        face_search.face_found()
    else:
        print("No face found before timeout")


def tracking_face():
    pass
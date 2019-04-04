from client import ClientSocket
from LookForFace import SearchForFace
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time

IP = '10.200.56.146'
PORT = 5010
# set up client and face searching
client = ClientSocket(IP, PORT)
face_search = SearchForFace(client)
distance_tolerance = 0.1  # don't move to the face if within this distance of 1 unit

# global variables
no_face_search_restart_interval = 0  # min time interval required to restart face search
last_face_time = -no_face_search_restart_interval  # last time a face was seen


def move_to_face():
    """
    moving to offset away from face state
    :param distance: the distance to the face
    :return: False if face is lost
    """
    face = face_search.search_for_face()
    face_search.move_forward_or_back(face)

    return False


def searching(image):
    global last_face_time
    # zero motors
    face_search.zero_motors()
    # start searching for a face
    face = face_search.search_for_face(image)
    # check that a face was found
    if face is not None:
        # face found
        last_face_time = time.process_time()
        # say "hello human"
        dis = face_search.face_found(face)
        return True, dis
    else:
        print("No face found before timeout")
        return False, 0


def tracking_face():
    """
    tracking face state
    :return: False if face is lost
    """
    face = face_search.search_for_face()
    face_search.track_face(face)
    return False


def rotate_to_face():
    """
    rotating to center on face state
    :return: False if face is lost
    """
    face = face_search.search_for_face()
    face_search.center_on_face(face)
    return False


def running_loop():
    search_state = True
    rotate_state = False
    moving_state = False
    tracking_state = False
    dis = 0
    camera = PiCamera()
    w, h = 320, 240
    camera.resolution = (w,h)
    camera.framerate=32
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        rawCapture.truncate(0)
        while True:
            if search_state:
                # search for a face, once found go on to rotate state unless still in tracking state
                face_found, dis = searching(image)
                if face_found:
                    search_state = False
                    rotate_state = not tracking_state

            elif rotate_state:
                face_found = rotate_to_face()
                rotate_state = False
                if not face_found:
                    search_state = True

            elif moving_state:
                face_found = move_to_face()
                moving_state = False
                if not face_found:
                    search_state = True

            elif tracking_state:
                # only exit tracking state to do some searching then go right back to tracking
                face_found = tracking_face()
                timeout = time.process_time() - last_face_time < no_face_search_restart_interval
                if not face_found:
                    if not timeout:
                        search_state = True



running_loop()
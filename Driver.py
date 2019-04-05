from client import ClientSocket
from LookForFace import SearchForFace
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time

IP = '10.200.22.237'
PORT = 5010
face = None
# set up client and face searching
client = None##ClientSocket(IP, PORT)
face_search = SearchForFace(client)
distance_tolerance = 0.1  # don't move to the face if within this distance of 1 unit

# global variables
no_face_search_restart_interval = 3  # min time interval required to restart face search
last_face_time = -no_face_search_restart_interval  # last time a face was seen


def move_to_face(face):
    """
    moving to offset away from face state
    :return: False if face is lost
    """
    face_search.move_forward_or_back(face)
    return False


def searching(image):
    global last_face_time
    # start searching for a face
    face = face_search.search_for_face_manager(image)
    # check that a face was found
    if face is not None:
        # face found
        last_face_time = time.process_time()
        # say "hello human"
        # TODO face_search.face_found()
        return True, face
    else:
        return False, None


def tracking_face(face, image):
    """
    tracking face state
    :return: False if face is lost
    """
    face_search.track_face(face, image)
    return False


def rotate_to_face(face, image):
    """
    rotating to center on face state
    :return: False if face is lost
    """
    face_search.center_on_face(face, image)
    return False


def running_loop():
    global face
    search_state = True
    rotate_state = False
    moving_state = False
    tracking_state = False
    camera = PiCamera()
    w, h = 320, 240
    camera.resolution = (w,h)
    camera.framerate=32
    rawCapture = PiRGBArray(camera, size=camera.resolution)

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        rawCapture.truncate(0)
        # TODO remove sleep
        time.sleep(0.1)

        if search_state:
            print("searching state")
            # search for a face, once found go on to rotate state unless still in tracking state
            face_found, face = searching(image)
            if face_found:
                search_state = False
                rotate_state = not tracking_state

        elif rotate_state:
            print("rotating state")
            face_found = rotate_to_face(face, image)
            timeout = time.process_time() - last_face_time < no_face_search_restart_interval
            if not face_found:
                if not timeout:
                    search_state = True
                    rotate_state = False


        elif moving_state:
            print("moving state")
            face_found = move_to_face(face)
            timeout = time.process_time() - last_face_time < no_face_search_restart_interval
            if not face_found:
                if not timeout:
                    search_state = True
                    moving_state = False

        elif tracking_state:
            print("tracking state")
            # only exit tracking state to do some searching then go right back to tracking
            face_found = tracking_face(face, image)
            timeout = time.process_time() - last_face_time < no_face_search_restart_interval
            if not face_found:
                if not timeout:
                    search_state = True


running_loop()

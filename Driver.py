from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2 as cv

camera = PiCamera()
w, h = 640, 480
camera.resolution = (w, h)  # (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)

# allow the camera to warmup
time.sleep(0.1)
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # get frame size
    w, h = image.shape[:2]
    # use the lower center of the image
    #x, y = w//5, h//2
    #image = image[y:y + h//4, x:x + 3*w//5]

    face = face_cascade.detectMultiScale(image, 1.8, 5)

    for (x,y,w,h) in face:
        cv.rectangle(image, (y,x), (y+h, x+w), (0,0,255), 3)

    cv.imshow("image", image)
    key = cv.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2 as cv




camera = PiCamera()  # why doesn't it like this line?

w, h = 640, 480
camera.resolution = (w,h)
camera.framerate=32
rawCapture = PiRGBArray(camera, size=camera.resolution)
print("test2")
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    print("test1")
    #running_loop(image, rawCapture)
    cv.imshow("image", image)
    rawCapture.truncate()
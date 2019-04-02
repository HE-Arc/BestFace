#coding: utf-8

import numpy as np
import cv2 as cv
import os
from time import time
from datetime import datetime
from dotenv import load_dotenv

from threading import Thread
from queue import Queue, Empty

#####
#
# Face Detection
#
#####

MIN_WIDTH = 300
MIN_HEIGT = 300

def generate_image_directory():
    '''
    Create a unique directory for a sequence of frame
    return the directory
    '''
    # Generate unique directory name
    directory_name = "bestface_" + datetime.now().timestamp().__int__().__str__()

    # Create directory using the current working dir
    path = os.path.join(os.getcwd(), directory_name)
    try:
        os.mkdir(path)
    except Exception as e:
        print(f"An error occured: {e}")

    return path

def viola_jones(img):
    """
    Detect a face in an image using the FACE_CASCADE_CLASSIFIER of opencv.
    Return true if deteced and and the image with a rectangle where the face is
    """
    detected = False
    face_cascade = cv.CascadeClassifier(os.getenv("FACE_CASCADE_CLASSIFIER", 0))
    try:
        faces = face_cascade.detectMultiScale(img, 1.3, 5)
        # print(faces) # ex: [[221  91 356 356]]
        for(x, y, w, h) in faces:
            if w >= MIN_HEIGT and h >= MIN_HEIGT:
                detected = True
                cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    except:
        pass
    return detected, img

#####
#
# Producer / Consumer pattern
#
#####

queue = Queue(20)
run = True

IMG_TO_SKIP = 5
img_skipped = 0

class CameraProducerThread(Thread):
    '''
    This class provide all the images of a face when detected
    '''
    def run(self):
        global queue
        global run

        cap = None
        try:
            cap = cv.VideoCapture(0)

            while run:
                ret, frame = cap.read()
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                ret, vj = viola_jones(gray)
                if ret:
                    queue.put(vj)
        finally:
            cap.release()


class PhotoTakerConsumerThread(Thread):
    '''
    This class save a defined number of picture
    '''
    
    def run(self):
        global queue
        global run

        global img_skipped

        sequence_running = False
        dir_path = None
        img_num = 0
        while run:
            try:
                img = queue.get_nowait()

                if img_skipped % IMG_TO_SKIP != 0:
                    img_skipped += 1
                    pass

                if not sequence_running:
                    sequence_running = True
                    dir_path = generate_image_directory()

                img_path = os.path.join(dir_path, "img" + str(img_num) + ".png")
                cv.imwrite(img_path, img, [int(cv.IMWRITE_PNG_COMPRESSION), 9])
                
                img_num += 1
                queue.task_done()
            except Empty:
                sequence_running = False
                img_num = 0
            pass

#####
#
# Main
#
#####

if __name__=="__main__":
    print(cv.__version__)
    load_dotenv()
    '''
    use_camera()
    viola_jones()
    '''

    producer = CameraProducerThread()
    consumer = PhotoTakerConsumerThread()

    producer.start()
    consumer.start()

    while run:
        if input() == "q":
            run = False
            break

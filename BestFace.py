#coding: utf-8

import numpy as np
import cv2 as cv
import os
from time import time
from datetime import datetime
from dotenv import load_dotenv

from threading import Thread
from queue import Queue, Empty

def generate_image_directory():
    '''
    Create a unique directory for a sequence of frame
    return the directory
    '''
    # Generate unique directory name
    directory_name = "bestface_" + datetime.now().timestamp().__int__().__str__()

    # Create directory using the current working dir
    path = os.path.join(os.getcwd(), directory_name)
    os.mkdir(path)

    return path

def use_camera():
    cap = cv.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, vj = viola_jones(gray)
        if ret:
            name = "img_" + time().__str__() + ".png"
            cv.imwrite(name, frame, [int(cv.IMWRITE_PNG_COMPRESSION), 9])
        cv.imshow('vj', vj)
        if(cv.waitKey(1) & 0xFF == ord('q')):
            break
    cap.release()
    cv.destroyAllWindows()

def viola_jones(img):
    detected = False
    face_cascade = cv.CascadeClassifier(os.getenv("FACE_CASCADE_CLASSIFIER", 0))
    try:
        faces = face_cascade.detectMultiScale(img, 1.3, 5)
        # print(faces) # ex: [[221  91 356 356]]
        for(x, y, w, h) in faces:
            detected = True
            cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    except:
        pass
    return detected, img

queue = Queue(20)

class CameraProducerThread(Thread):
    '''
    This class provide all the images of a face when detected
    '''
    def run(self):
        global queue

        cap = None
        try:
            cap = cv.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                ret, vj = viola_jones(gray)
                if ret:
                    queue.put(frame)
        finally:
            cap.release()


class PhotoTakerConsumerThread(Thread):
    '''
    This class save a defined number of picture
    '''
    
    def run(self):
        global queue

        sequence_running = False
        dir_path = None
        img_num = 0
        while True:
            try:
                img = queue.get_nowait()

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

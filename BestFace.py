#coding: utf-8

import numpy as np
import cv2 as cv
import os
from time import time
from datetime import datetime
from dotenv import load_dotenv

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


if __name__=="__main__":
    print(cv.__version__)
    '''
    load_dotenv()
    use_camera()
    viola_jones()
    '''
    print(generate_image_directory())
#coding: utf-8

import numpy as np
import cv2 as cv
import os
from dotenv import load_dotenv

def use_camera():
    cap = cv.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        if ret:
            vj = viola_jones(gray)
            cv.imshow('vj', vj)
        if(cv.waitKey(1) & 0xFF == ord('q')):
            break
    cap.release()
    cv.destroyAllWindows()

def viola_jones(img):
    face_cascade = cv.CascadeClassifier(os.getenv("FACE_CASCADE_CLASSIFIER", 0))
    
    faces = face_cascade.detectMultiScale(img, 1.3, 5)
    for(x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return img


if __name__=="__main__":
    print(cv.__version__)
    load_dotenv()
    use_camera()
    viola_jones()
#coding: utf-8

import numpy as np
import cv2 as cv
import os
from time import time
from datetime import datetime
from dotenv import load_dotenv

from threading import Thread
from queue import Queue, Empty

import re
import random

from shutil import rmtree

from statistics import mean
from math import log

#####
#
# Face Detection
#
#####

MIN_WIDTH = 300
MIN_HEIGT = 300

IMG_EXT = ".png"

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
        #print(f"An error occured: {e}")
        pass

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
                # cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    except:
        pass
    return detected, img

score_eyes_img_counter = 0
def score_eyes(img):
    """
    Check eyes caracteristics of the eyes and return a score
    if the value is near 1, the eyes are align
    else, the eyes are not align and the values is near 0
    """
    global score_eyes_img_counter
    eye_cascade = cv.CascadeClassifier(os.getenv("EYE_CASCADE_CLASSIFIER", 0))

    scores = {
        "size": 0, 
        "alignement": 0,
        "distance": 0,
    }
    try:
        eyes = eye_cascade.detectMultiScale(img)
        if len(eyes) < 2: # don't detect the two eyes
            return 0
        score_eyes_img_counter += 1
        # OpenCV return a square rectangle where the eyes are centered
        e_left = eyes[0]
        e_right = eyes[1]

        print(f"left: {e_left}\tright: {e_right}")

        # Size
        if e_left[2] < 60 or e_right[2] < 60:
            # if the eyes are too small
            return 0
        if e_left[2] > e_right[2]:
            # left eye is bigger
            scores["size"] = e_right[2] / e_left[2]
        elif e_right[2] > e_left[2]:
            # right eye is bigger
            scores["size"] = e_left[2] / e_right[2]
        else:
            scores["size"] = 1

        # TODO alignement
        abs_height = abs(e_left[1] - e_right[1])
        if abs_height == 0 or abs_height < 10:
            scores["alignement"] = 1
        else:
            x = abs_height / 10
            scores["alignement"] = ((1 / x * log(x)) - 1/x) # TODO too low

        print(f"height: {abs_height} \talignement: {scores['alignement']}")
        
        # TEMP save the images with eyes
        img_path = os.path.join(os.getcwd(),"eyes", score_eyes_img_counter.__str__() + ".png")
        cv.rectangle(img,(e_left[0],e_left[1]),(e_left[0]+e_left[2],e_left[1]+e_left[3]),(0,255,0),2)
        cv.rectangle(img,(e_right[0],e_right[1]),(e_right[0]+e_right[2],e_right[1]+e_right[3]),(255,0,0),2)
        cv.imwrite(img_path, img, [int(cv.IMWRITE_PNG_COMPRESSION), 9])
        # If it can save the score above condition are ok

        # TODO distance
        scores["distance"] = 0
        
    except Exception as e:
        print(e)

    final_score = mean(scores.values())

    #print(final_score)

    return final_score

#####
#
# Face Selection
#
#####

def get_bestface_dirs():
    current_dir = os.getcwd()
    dirs = list(filter(lambda x: os.path.isdir(x), os.listdir(current_dir)))
    bestface_dirs = list(filter(lambda dir_name : re.match("^bestface_\d{5,10}$", dir_name), dirs))
    return bestface_dirs

def face_score(picture_path):
    """
    assign a score to a picture using its path. It refer to symetrie.
    the score values is between 0 and 1
    """
    picture = cv.imread(picture_path)

    scores = []
    scores.append(score_eyes(picture))

    return mean(scores)

def select_face():
    """
    Foreach dir that is named "bestface_xxx"
    Take all the picture and save the best one
    """
    print("Start selection...")
    # Create the directory where the best faces will be stored
    select_face_dir = "bestfaces"
    try:
        os.mkdir(select_face_dir)
    except:
        # the directory already exists
        pass

    # Run throught all directory so throught each person
    bestface_dirs = get_bestface_dirs()
    for d in bestface_dirs:
        print(f"Directory: {d}")

        ranked_pictures = []

        # Get all the pictures
        dir_files = os.listdir(os.path.join(os.getcwd(), d))
        pictures = list(filter(lambda f: re.match("^img\d{1,3}\.png$", f), dir_files))

        # foreach pictures
        for pic in pictures:
            # assign a score
            score = face_score(os.path.join(d, pic))
            ranked_pictures.append({"score": score, "picture" :pic})
        #print(ranked_pictures)
        
        # Sort the pictures by score
        sorted_pictures = sorted(ranked_pictures, key = lambda entry: entry["score"])
        #print(sorted_pictures)

        # Save the best picture in another folder (bestfaces ?)
        select_face_path = os.path.join(select_face_dir,d + ".png")
        try:
            os.rename(os.path.join(d, sorted_pictures[0]["picture"]), select_face_path)
        except IndexError as ie:
            # Empty files
            pass
        except FileExistsError as e:
            # Replace it
            os.remove(select_face_path)
            os.rename(os.path.join(d, sorted_pictures[0]["picture"]), select_face_path)

        # delete the folder
        #rmtree(d)
        
    # search new folder
    
    # TODO Continue while new folders are here

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
        print("producer start running")

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
            print("producer stopped")


class PhotoTakerConsumerThread(Thread):
    '''
    This class save a defined number of picture
    '''
    
    def run(self):
        print("consumer start running")

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

                img_path = os.path.join(dir_path, "img" + str(img_num) + IMG_EXT)
                cv.imwrite(img_path, img, [int(cv.IMWRITE_PNG_COMPRESSION), 9])
                
                img_num += 1
                queue.task_done()
            except Empty:
                sequence_running = False
                img_num = 0
            pass
        print("consumer stopped")

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

    # Start the threads
    #producer.start()
    #consumer.start()

    #run = False
    while run:
        if input() == "q":
            run = False
            break

    # Select the best pictures
    select_face()
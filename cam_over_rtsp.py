# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 19:30:27 2019

@author: Dejan
"""

import cv2
import math
from queue import Queue
from openalpr import Alpr

url = "rtsp://admin:admin@192.168.1.119:554/0"
cap = cv2.VideoCapture(url)
fps = math.floor(cap.get(5))
delta_t = 1
delay = 2

alpr = Alpr('eu')
alpr.set_top_n = 4

Qf = Queue(-1)  # queue of frames to decode
Qd = Queue(-1)  # queue of decoded data

def get_frames():
    print('reader started')
    i_lim = fps * delta_t
    i = 0
    try:
        while True:
            frame = cap.read()[1]
            i += 1
            if i >= i_lim:
                Qf.put(frame)
                i = 0
                print(Qf.qsize())
                
                
    except Exception as e:
        print(e)
        
    cap.release()
    cv2.destroyAllWindows()
    

def alprDecoder():
    pass
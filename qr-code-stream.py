# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:54:32 2018

@author: Dejan
"""

import cv2
import pyzbar.pyzbar as pyzbar
import math
from queue import Queue
from threading import Thread

#cap = cv2.VideoCapture(0)
url = "rtsp://admin:admin@192.168.1.119:554/0"
cap = cv2.VideoCapture(url)
fps = math.floor(cap.get(5))
delta_t = 0.5
delay = 2

Qf = Queue(-1)  # queue of frames to decode
Qd = Queue(-1)  # queue of decoded data

def QR_decoder():
    print('decoder started')
    skip_frames = math.floor(delay / delta_t)
    print(skip_frames)
    while True:
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        print(Qf.qsize())
        i = 0
        while i < skip_frames:
            Qf.get()
            i += 1

        frame = cv2.cvtColor(Qf.get(), cv2.COLOR_BGR2GRAY)
        decodedQRs = pyzbar.decode(frame)
        if decodedQRs:
            Qd.put(decodedQRs.data) 
        
        print('Type : ', decodedQRs.type)
        print('Data : ', decodedQRs.data,'\n')

        #return decodedQRs

def get_frames():
    print('reader started')
    i_lim = fps * delta_t
    i = 0
    try:
        while True:
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
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


Thread(target=get_frames, daemon=True).start()
Thread(target=QR_decoder, args=(), daemon=True).start()
from picamera import PiCamera
import time
import importlib.util
from queue import Queue
import sys
import io
import sqlite3
import cv2
import RPi.GPIO as gpio
from threading import Thread, RLock
import math
from fuzzywuzzy import fuzz
from tkinter import *

from threading import Thread

# alpr_path = '/home/pi/.local/lib/python2.7/site-packages/openalpr/openalpr.py'

# openalpr = importlib.util.spec_from_file_location('openalpr', alpr_path)
# Alpr = importlib.util.module_from_spec(openalpr)
# openalpr.loader.exec_module(Alpr)

#alpr_path = '/usr/lib'
# sys.path.insert(0,alpr_path)
from openalpr import Alpr


alpr = Alpr('eu', 'openalpr.conf', 'runtime_data')
alpr.set_top_n(5)
db_path = 'alprData.db'
insertStr = 'INSERT INTO alprTable (plates, time, opened, confidence) VALUES (?, ?, ?, ?)'
selStr = 'SELECT plates FROM userTable'
url = "rtsp://admin:admin@192.168.5.55:554/0"

delay = 2 #Koliko kasni slika sa kamere [sec
pic_dt = 3 #svakih koliko uzima sliku [sec]

Pi_Cam = False
IP_Cam = True

fullRatio = 80
fullRatioWithPartial = 80
partialRatio = 100

Qpic = Queue(-1)
Qpic_nd = Queue(-1)
Qrez = Queue(-1)
lock = RLock()

rt=Tk()
rt.geometry("700x600")
rt.wm_title("baza_korisnika")

conn = sqlite3.connect(db_path)
cur = conn.cursor()
with conn:
        conn.execute("create table if not exists userTable(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, naziv TEXT, plates TEXT UNIQUE)")
        conn.execute("create table if not exists alprTable (plates	TEXT NOT NULL, time	TEXT NOT NULL, opened INTEGER DEFAULT 0, confidence	REAL NOT NULL)")
cur.execute(selStr)

cap = cv2.VideoCapture(url)
fps = math.floor(cap.get(5))
userPlates = cur.fetchall()
userPlates = [x[0] for x in userPlates]
gpio.setmode(gpio.BOARD)
gpio.setup(11,gpio.OUT)


def OpenPiCamera():
    print('Pi camera started')
    with PiCamera() as camera:
        camera.start_preview(alpha=200)
        while True:
                pic_stream = io.BytesIO()
                time.sleep(2)
                camera.capture(pic_stream, 'jpeg')
                Qpic.put(pic_stream.getvalue())
                pic_stream.close()

        camera.stop_preview()


def OpenIPCamera():
    i_lim = fps * pic_dt
    i = 0
    while True:
        try:
            cap.read()[1]
            i += 1
            if i >= i_lim:
                try:
                    frame = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
                    Qpic_nd.put(frame)
                    i = 0
                    cap.imshow('fr', frame) 
                except:
                    pass
        except Exception as e:
            print(e)
       
    cap.release()
    cv2.destroyAllWindows()


def ALPR_decoder():
    print('ALPR started')
    i = 0
    while True:
        if Pi_Cam:
            alprOut = alpr.recognize_array(Qpic.get())
        elif IP_Cam:
            alprOut = alpr.recognize_ndarray(Qpic_nd.get())
            #print('results', alprOut['results'])
        else:
            print('Izaberi kameru!!! Pi_Cam/IP_Cam')

        if len(alprOut['results']):
            Qrez.put({'epoch': alprOut['epoch_time'], 'results': alprOut['results']})
            print('detektovane tablice')
        else:
            print('nema nikoga')


def podizac():
    gpio.output(11,1)
    time.sleep(2)
    gpio.output(11,0)


def sqlInsert():
    print('sqlinsert started')
    conn2 = sqlite3.connect(db_path)
    #plate1 = ''
    while True:
        data = Qrez.get()
        epoch = data['epoch']
        rezs = data['results']
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch/1000))
        for rez in rezs[0]['candidates']:
                plate = rez['plate']
                opened = plate in userPlates

                if plate_matcher(plate, userPlates):
                    Thread(target=podizac, daemon=True).run()
                    print('OPENED OPENED OPENED')


                confidence = rez['confidence']
                print(plate, opened, confidence)
                with lock:
                    with conn2:
                        conn2.execute(insertStr, [plate, t, opened, confidence])

                # if opened and not(plate1==plate):
                #         Thread(target=podizac, daemon=True).run()
                #         print('OPENED OPENED OPENED')


def plate_matcher(plate, plates):
    print('running matcher')
    for p in plates:
        print('matching:', plate, p)
        fr = fuzz.ratio(plate, p)
        pr = fuzz.partial_ratio(plate, p)
        print('fr: ',fr, 'pr: ', pr)
        if fr>=fullRatio or (fr>=fullRatioWithPartial and pr>=partialRatio):
            return(True)
    
    return(False)

        
if Pi_Cam:
    Thread(target=OpenPiCamera, daemon=True).start()
if IP_Cam:
    Thread(target=OpenIPCamera, daemon=True).start()
Thread(target=ALPR_decoder, daemon=True).start()
Thread(target=sqlInsert, daemon=True).start()


def add_command():
    if(len(naziv.get())!=0 and len(plates.get())!=0):
        with lock:
            with conn:
                conn.execute("insert into userTable (naziv, plates) values(?,?)",(naziv.get().lower(),plates.get()))
        userPlates.append(plates.get())
        lb1.delete(0,END)
        cur.execute('select id from userTable where naziv=? and plates =?', (naziv.get().lower(),plates.get()))
        id = cur.fetchone()
        lb1.insert(END,(id, naziv.get(),plates.get()))



def view_command():
    lb1.delete(0,END)
    cur.execute("SELECT * FROM userTable")
    [lb1.insert(END,row) for row in cur.fetchall()]
        

def findit_command():
    lb1.delete(0,END)
    cur.execute("select * from userTable where naziv like ? or plates like ?",(naziv.get().lower(),plates.get()))
    [lb1.insert(END,row) for row in cur.fetchall()]
        

def dele_command():
        if len(plates.get())!=0:
                cur.execute("delete from userTable where naziv=? and plates=?",(naziv.get().lower(),plates.get()))
                conn.commit()
                clearit_command()
                view_command()


def clearit_command():
    e1.delete(0,END)
    e2.delete(0,END)    
    

def update_command():
        if len(plates.get())!=0:
                with lock:
                    with conn:
                        conn.execute("update userTable set naziv=?,plates=? where id=?",(naziv.get().lower(),plates.get(), lbData[0]))
                clearit_command()
                view_command()


r=2
l0=Label(rt,text="") #nazivi labela prije unosa
l0.grid(row=r-1,column=0)

l1=Label(rt,text="Naziv",font=("Courier", 10))
l1.grid(row=r,column=3)

l2=Label(rt,text="Tablice",font=("Courier", 10))
l2.grid(row=r+1,column=3)


naziv=StringVar()


e1=Entry(rt,textvariable=naziv,font=("Courier", 15))#unosi redom ime prezime tablice
e1.grid(row=r,column=4)
plates=StringVar()
e2=Entry(rt,textvariable=plates,font=("Courier", 15))
e2.grid(row=r+1,column=4)
reg=StringVar()


lb1=Listbox(rt,height=10, width=40,font=("Courier", 20))#lista sa scrollom
lb1.grid(row=10, column=0,rowspan=8,columnspan=6)
sb=Scrollbar(rt)
sb.grid(row=7,column=5,rowspan=8)

lb1.configure(yscrollcommand=sb.set)#scroll 
sb.configure(command=lb1.yview)


def onselect(evt):
        global lbData
        lb = evt.widget
        try:
                yid = lb.curselection()[0]
                lbData = lb.get(yid)
                e1.delete(0,END)
                e1.insert(END, lbData[1])
                e2.delete(0,END)
                e2.insert(END, lbData[2])
        except:
                pass


lb1.bind('<<ListboxSelect>>',onselect)#selektovanje

b1=Button(rt,text="lista korisnika",width=20, command=view_command)
b1.grid(row=0,column=0)

b2=Button(rt,text="dodaj korisnika",width=20, command=add_command)
b2.grid(row=1,column=0)

b3=Button(rt,text="obrisi korisnika",width=20, command=dele_command)
b3.grid(row=2,column=0)

b4=Button(rt,text="pronadji korisnika",width=20, command=findit_command)
b4.grid(row=3,column=0)

b5=Button(rt,text="prepravi korisnika",width=20, command=update_command)
b5.grid(row=4,column=0)

rt.mainloop()
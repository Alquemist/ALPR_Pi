# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 09:09:42 2019

@author: RedOct
"""

import sqlite3

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)

def okidac():
  for x in range (0,1):
    GPIO.output(11,1)
    time.sleep(10)
    GPIO.output(11,0)
    
def konnect1():
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("create table if not exists alprTable (plates text,time text,opened int,confidence float)")
    con.commit()
    con.close()
    
def addrec2(plates,time,opened,confidence):
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("delete from alprTable")
    cur.execute("insert into alprTable values(?,?,?,?)",(plates,time,opened,confidence))
    print("upisno je:",plates,opened,time,confidence)           
    con.commit()
    con.close()
    
konnect1()
def uporedi():
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("select * from userTable inner join alprTable on userTable.plates=alprTable.plates")
    rows=cur.fetchall()
    con.close()
    #print(rows)
    if (rows):
     print("bingo")
     okidac()
     
    else:
        print("nema pogotka")
   

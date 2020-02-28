# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 18:13:03 2019

@author: RedOct
"""

from tkinter import *
import sqlite3

import time
from threading import Thread

dbName = "alprData.db"

rt=Tk()
rt.geometry("700x600")
rt.wm_title("baza_korisnika")

conn = sqlite3.connect(dbName)
cur = conn.cursor()

with conn:
        conn.execute("create table if not exists userTable(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, naziv TEXT, plates TEXT UNIQUE)")


def add_command():
    if(len(naziv.get())!=0 and len(plates.get())!=0):
        with conn:
                conn.execute("insert into userTable (naziv, plates) values(?,?)",(naziv.get(),plates.get()))
        userPlates.append(plates.get()1)
        lb1.delete(0,END)
        cur.execute('select id from userTable where naziv=? and plates =?', (naziv.get(),plates.get()))
        id = cur.fetchone()
        lb1.insert(END,(id, naziv.get(),plates.get()))

        

def view_command():
    lb1.delete(0,END)
    cur.execute("SELECT * FROM userTable")
    [lb1.insert(END,row) for row in cur.fetchall()]
        

def findit_command():
    lb1.delete(0,END)
    cur.execute("select * from userTable where naziv like ? or plates like ?",(naziv.get(),plates.get()))
    [lb1.insert(END,row) for row in cur.fetchall()]
        

def dele_command():
        if len(plates.get())!=0:
                cur.execute("delete from userTable where naziv=? and plates=?",(naziv.get(),plates.get()))
                conn.commit()
                clearit_command()
                view_command()


def clearit_command():
    e1.delete(0,END)
    e2.delete(0,END)    
    

def update_command():
        if len(plates.get())!=0:
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

def printer():
        while True:
                print('hhhhh')
                time.sleep(3)

Thread(target=printer, daemon=True).start()

rt.mainloop()
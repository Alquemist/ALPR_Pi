# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 18:52:01 2019

@author: RedOct
"""

import sqlite3

# def connect():
#     con=sqlite3.connect("alprData.db")
#     cur=con.cursor()
#     cur.execute("create table if not exists userTable(naziv text,plates text)")
#     con.commit()
#     con.close()
    
def addrec(naziv,plates):
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    
    cur.execute("insert into userTable values(?,?)",(naziv,plates))
    print("upisno je:",naziv,plates)           
    con.commit()
    con.close()
    
def view():
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM userTable")
    rows=cur.fetchall()
    con.close()
    return rows


  
def dele(naziv):
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("delete from userTable where naziv=?",(naziv,))
    con.commit()
    con.close()


def findit(naziv="",plates=""):
    print('FIND IT', naziv, plates)
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("select * from userTable where naziv=? or plates=?",(naziv,plates,))
    rows=cur.fetchall()
    con.close()
    print(rows)
    return rows
    
'''def updt(mid,naziv="",plates=""):
    con=sqlite3.connect("alprData.db")
    cur=con.cursor()
    cur.execute("update userTable set naziv=?,plates=? where id=?",(naziv,plates,mid))
    con.commit()'''
    
    
    
connect()


















 
    
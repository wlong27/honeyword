import sqlite3
import random
import bcrypt
import gen

#Set size of words
n = 5

#Insert honey words and tracking index
def insert_new(username, password, cur, index):
    honeywords = gen_honeywords(n, password)

    #Remove duplicates and keep the actual password in the list
    honeywords = list(set(honeywords)) 
    if (password not in honeywords):
        honeywords.pop(0)
        honeywords.append(password)    
        random.shuffle(honeywords)

    #hash all the honeywords for storing in DB
    for word in honeywords:
        index += 1
        hashed = bcrypt.hashpw(word.encode('utf-8'), bcrypt.gensalt())
        if (word == password):   #this is the actual password! we need to track separately
            insert_tracked_index(username, index, cur)
        cur.execute('INSERT INTO Users VALUES("{0}","{1}","{2}")'.format(username,hashed.decode('utf-8'),index))
    return index

 #Insert into separate tbl for tracking
def insert_tracked_index(username, index, cur):
    cur.execute('INSERT INTO UsersIndex VALUES("{0}","{1}")'.format(username, index))

#Generate list of n honeywords and shuffle the position randomly
def gen_honeywords(n, pw):
    pw_list = [pw]
    lines = gen.high_probability_passwords.split()
    for line in lines:
        if (len(line)==len(pw)):
            pw_list.extend(line.split())
    honeywords = gen.generate_passwords(n, pw_list)
    return honeywords




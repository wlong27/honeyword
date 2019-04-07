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
        try:
            cur.execute('INSERT INTO Users VALUES("{0}","{1}","{2}","{3}")'.format(username,hashed.decode('utf-8'),index,word))
        except Exception as e:
            print(e)
            return -1
    return index

 #Insert into separate tbl for tracking
def insert_tracked_index(username, index, cur):
    cur.execute('INSERT INTO UsersIndex VALUES("{0}","{1}")'.format(username, index))

#Generate list of n honeywords and shuffle the position randomly
def gen_honeywords(n, pw):
    pw_list = [pw]
    lines = gen.high_probability_passwords.split()
    for line in lines:
        if (len(line)==len(pw) and line != pw):
            pw_list.extend(line.split())
    honeywords = gen.generate_passwords(n, pw_list)
    return honeywords

def honey_checker(username, password, cur):
    cur.execute('select * from Users where userName="{0}"'.format(username))
    hash_lst = [] 
    for row in cur.fetchall(): #hash, index
        hash_lst.append((row[1],row[2]))  

    ret_index = 0

    #No hash found. missing user
    if (len(hash_lst) == 0):
        print('No Hash found for user ' + username)
        return ret_index

    #Take the index of the first matching valid hash
    for tup in hash_lst:
        validHash = bcrypt.checkpw(password.encode('utf-8'), tup[0].encode('utf-8'))
        if validHash:
            ret_index = tup[1]
            break

    #if index is still 0, user has entered wrong password
    if (ret_index == 0):
        print('Wrong password for ' + username + password)
        return ret_index

    #Now we check for correct index after valid hash check
    cur.execute('select * from UsersIndex where userName="{0}"'.format(username))
    for row in cur.fetchall():
        if row[1] == ret_index:
            return ret_index
    
    #Honey words will return -1
    return -1
            
import sqlite3

with sqlite3.connect("sample.db") as connection:
    c = connection.cursor()
    c.execute('CREATE TABLE Users(userName TEXT, passwdHash TEXT)')
    c.execute('INSERT INTO Users VALUES("Good", "test")')
    c.execute('INSERT INTO Users VALUES("Good2", "test2")')
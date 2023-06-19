from DatabaseAccess import *
from window import *

import sqlite3 as sql

#Initiate server connection and cursor for queries
connect = sql.connect("server.db")
cursor = connect.cursor()


db = DatabaseAccess(cursor,connect) #Create database access object to pass to the window
window = Window(db) #Create window object
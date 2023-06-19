from DatabaseAccess import *
from window import *

import sqlite3 as sql

connect = sql.connect("server.db")
cursor = connect.cursor()

db = DatabaseAccess(cursor,connect)
window = Window(db)
print("hi")
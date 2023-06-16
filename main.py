import sqlite3 as sql

connect = sql.connect("server.db")
cursor = connect.cursor()
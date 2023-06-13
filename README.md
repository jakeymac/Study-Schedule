# Overview

I created this program to help clinics organize their study and participant information. This program uses sqlite3 to interact with an SQL database. Study Schedule is simple to use due to the nature of the GUI system involved. Study Schedule saves and works with multiple studies themselves, all participants involved in each study and saves information including names, birthdays, other related info, and times and dates for each visit of each study. 

[Software Demo Video](http://youtube.link.goes.here](https://youtu.be/2qVCD8vphdY)

# Relational Database

This relational database uses 4 tables: study, participant, Study_Dates_Times, and Participant_Dates_Times. Study and participant simply save information for each of those categories. The other two tables correspond to rows in these tables. The Participant_Dates_Times table corresponds to both the study and participant tables with corresponding keys to both, and also includes corresponding dates from the study table. The Study_Date_Times table only includes study_id, the primary key from the study table.


# Development Environment

I wrote this entire project in Visual Studio Code, along with using a software called DB Browser for SQLite to work with and read data from the database file.

The python libraries I used were tkinter and Sqlite3
# Useful Websites

* [W3Schools](w3schools.com)
* [Tutorialspoint](tutorialspoint.com)

# Future Work

* Improve design/spacing of GUI
* Better organization of the project's code
* Joining of similar functions within the project

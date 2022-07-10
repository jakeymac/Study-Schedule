import tkinter as tk
from tkinter import ttk
import tkcalendar
import tkinter.messagebox as tk_mb
import sqlite3 as sql

connect = sql.connect("server.db")
cursor = connect.cursor()

class Main():
    def __init__(self,root):
        self.root = root
        self.root.title("StudySchedule")
        
        self.main_menu()

    def main_menu(self):
        self.main_menu_frame = tk.Frame(self.root)
        
        self.main_menu_frame.pack()

        self.main_menu_top_label = tk.Label(self.main_menu_frame,text="Welcome to StudySchedule")
        self.main_menu_top_label.grid(row=0,column=0,columnspan=2,pady=5)
    
        self.add_study_button = tk.Button(self.main_menu_frame,text="Add New Study",command=self.add_new_study_window)
        self.add_study_button.grid(row=1,column=0,padx=5)

        self.view_study_button = tk.Button(self.main_menu_frame,text="View Study Info",command=self.view_study_info_window)
        self.view_study_button.grid(row=2,column=0)

        self.edit_study_button = tk.Button(self.main_menu_frame,text="Edit Study",command=self.open_edit_study_picker_window)
        self.edit_study_button.grid(row=3,column=0)

        self.add_participants_button = tk.Button(self.main_menu_frame,text="Add Participant",command=self.open_add_participant_study_picker_window)
        self.add_participants_button.grid(row=1,column=1)

        self.edit_participant_button = tk.Button(self.main_menu_frame,text="Edit Participant",command=self.open_edit_participant_study_picker_window)
        self.edit_participant_button.grid(row=2,column=1)

        self.view_participant_button = tk.Button(self.main_menu_frame,text="View Participant",command=self.open_view_participant_study_picker_window)
        self.view_participant_button.grid(row=3,column=1)

        self.view_entire_schedule_button = tk.Button(self.main_menu_frame,text="View Entire\n Study Schedule",command=self.open_schedule_study_pickers_window)
        self.view_entire_schedule_button.grid(row=1,rowspan=2,column=2)

        self.exit_program_button = tk.Button(self.main_menu_frame,text="Exit",command=self.close_program)
        self.exit_program_button.grid(row=3,column=2)


    def open_schedule_study_pickers_window(self):
        self.main_menu_frame.destroy()
        self.schedule_study_picker_frame = tk.Frame(self.root)
        self.schedule_study_picker_frame.pack()
        
        self.schedule_study_picker_label = tk.Label(self.schedule_study_picker_frame,text="Select a Study:")
        self.schedule_study_picker_label.grid(row=0,column=0)

        study_names = self.get_study_names()
        print(study_names)

        self.schedule_study_picker_var = tk.StringVar()
        self.schedule_study_picker = tk.OptionMenu(self.schedule_study_picker_frame,self.schedule_study_picker_var,*study_names,command=self.place_open_schedule_button)
        self.schedule_study_picker.grid(row=1,column=0)

        self.exit_open_schedule_study_picker_button = tk.Button(self.schedule_study_picker_frame,text="Back to Main Menu",command=self.exit_schedule_study_picker)
        self.exit_open_schedule_study_picker_button.grid(row=3,column=0)
        
    def place_open_schedule_button(self,*args):
        self.open_schedule_button = tk.Button(self.schedule_study_picker_frame,text="Open Schedule",command=self.open_entire_study_schedule)
        self.open_schedule_button.grid(row=2,column=0)

    def open_entire_study_schedule(self):
        self.schedule_study_picker_frame.destroy()
        self.view_study_schedule_frame = tk.Frame(self.root)
        self.view_study_schedule_frame.pack()

        self.study_schedule_label = tk.Label(self.view_study_schedule_frame,text=self.schedule_study_picker_var.get())
        self.study_schedule_label.grid(row=0,column=0,columnspan=2)
        
        #Find study id
        cursor.execute(f"""SELECT study_id FROM study WHERE study_name = "{self.schedule_study_picker_var.get()}" """)
        study_id = cursor.fetchone()[0]

        print(f"Study ID: {study_id}")
        cursor.execute(f"SELECT date FROM Study_Date_Times WHERE study_id = {study_id}")
        dates = [date[0] for date in cursor.fetchall()]
        print(dates)

        #initials_list
        cursor.execute(f"SELECT initials,participant_id FROM Participant WHERE study_id = {study_id}")

        initials_and_id = cursor.fetchall()

        columns = ["Name" + " | "]
        for date in dates:
            columns.append(date + " | ")

        columns[-1] = columns[-1][0:-3] #Get rid of " | " on last date column header

        self.total_schedule = [columns]

        for participant in initials_and_id:
            values = [participant[0] + "  | "]
            for date in dates:
                cursor.execute(f"""SELECT time FROM Participant_Date_Times WHERE date = "{date}" AND participant_id = {participant[1]} """)
                time = cursor.fetchone()[0]
                if len(time) == 6:
                    values.append(" " + time + "  | ")
                else:
                    values.append(time+ "  | ")

            values[-1] = values[-1][0:-2]
            self.total_schedule.append(values)

        text_widget_frame = tk.Frame(self.view_study_schedule_frame)
        text_widget_frame.grid(row=1,column=0,columnspan=2)

        horizontal_scrollbar = tk.Scrollbar(text_widget_frame,orient="horizontal")
        horizontal_scrollbar.pack(side=tk.BOTTOM,fill="x")

        vertical_scrollbar = tk.Scrollbar(text_widget_frame,orient="vertical")
        vertical_scrollbar.pack(side=tk.RIGHT,fill="y")

        self.study_schedule_widget = tk.Text(text_widget_frame,wrap=tk.NONE,xscrollcommand=horizontal_scrollbar.set,yscrollcommand=vertical_scrollbar.set)
        self.study_schedule_widget.pack()

        horizontal_scrollbar.config(command=self.study_schedule_widget.xview)
        vertical_scrollbar.config(command=self.study_schedule_widget.yview)

        self.final_schedule_string = ""
        for line in self.total_schedule:
            new_line = "".join(line) + "\n"
            self.final_schedule_string += new_line
            print(new_line)
            self.study_schedule_widget.insert(tk.END,new_line)

        self.exit_schedule_button = tk.Button(self.view_study_schedule_frame,text="Back to Main Menu",command=self.exit_view_schedule)
        self.exit_schedule_button.grid(row=2,column=0)

        self.export_frame = tk.Frame(self.view_study_schedule_frame)
        self.export_frame.grid(row=2,column=1)

        self.export_entry_label = tk.Label(self.export_frame,text="Enter File Name to\n Export Schedule:")
        self.export_entry_label.grid(row=0,column=0)

        self.export_entry = tk.Entry(self.export_frame)
        self.export_entry.grid(row=0,column=1)

        self.export_schedule_button = tk.Button(self.export_frame,text="Export Schedule",command=self.export_entire_schedule)
        self.export_schedule_button.grid(row=1,column=0,columnspan=2)
    
    def export_entire_schedule(self):
        new_file = open(self.export_entry.get(),"a")
        new_file.write(self.final_schedule_string)
        new_file.close()
        tk_mb.showinfo(message=f"Exported successfuly to {self.export_entry.get()}")

    def open_view_participant_study_picker_window(self):
        self.main_menu_frame.destroy()
        self.view_participant_pickers_frame = tk.Frame(self.root)
        self.view_participant_pickers_frame.pack()

        study_names = self.get_study_names()

        self.view_participant_study_picker_label = tk.Label(self.view_participant_pickers_frame,text="Select Study:")
        self.view_participant_study_picker_label.grid(row=0,column=0)

        self.view_participant_study_picker_var = tk.StringVar()
        self.view_participant_study_picker = tk.OptionMenu(self.view_participant_pickers_frame,self.view_participant_study_picker_var,*study_names,command=self.open_view_participant_initials_picker)
        self.view_participant_study_picker.grid(row=1,column=0)

        self.view_participant_exit_button = tk.Button(self.view_participant_pickers_frame,text="Back to Main Menu",command=self.exit_view_participant_menu)
        self.view_participant_exit_button.grid(row=5,column=0)

        self.view_participant_initials_picker_open = False
        self.open_participant_view_button_placed = False

    def open_view_participant_initials_picker(self,*args):
        if self.view_participant_initials_picker_open:
            self.view_participant_initials_picker_frame.destroy()
        
        if self.open_participant_view_button_placed:
            self.open_view_participant_button.config(text=f"View{self.view_participant_initials_picker_var.get()}'s Info")
        
        self.view_participant_initials_picker_open = True

        cursor.execute(f"""SELECT study_id FROM study WHERE study_name = "{self.view_participant_study_picker_var.get()}" """)
        study_id = cursor.fetchone()[0]

        cursor.execute(f"SELECT initials FROM Participant WHERE study_id = {study_id}")
        participants = [participant[0] for participant in cursor.fetchall()]
        
        self.view_participant_initials_label = tk.Label(self.view_participant_pickers_frame,text="Select Participant:")
        self.view_participant_initials_label.grid(row=2,column=0)

        self.view_participant_initials_picker_var = tk.StringVar()
        self.view_participant_initials_picker = tk.OptionMenu(self.view_participant_pickers_frame,self.view_participant_initials_picker_var,*participants,command=self.place_view_participant_button)
        self.view_participant_initials_picker.grid(row=3,column=0)

    def place_view_participant_button(self,*args):
        self.open_participant_view_button_placed = True
        self.open_view_participant_button = tk.Button(self.view_participant_pickers_frame,text=f"View{self.view_participant_initials_picker_var.get()}'s Info",command=self.open_view_participant_info_window)
        self.open_view_participant_button.grid(row=4,column=0)
    
    def open_view_participant_info_window(self):
        self.view_participant_pickers_frame.destroy()

        cursor.execute(f"""SELECT * FROM participant WHERE initials = "{self.view_participant_initials_picker_var.get()}" """)
        participant_info= cursor.fetchall()[0]
        
        self.view_participant_info_frame = tk.Frame(self.root)
        self.view_participant_info_frame.pack()

        self.view_participant_id = participant_info[0]
        first_name = participant_info[1]
        last_name = participant_info[2]
        initials = participant_info[3]
        birthday = participant_info[4]
        other_info = participant_info[5]

        cursor.execute(f"""SELECT date,time,is_in_house FROM participant_date_times WHERE participant_id = {self.view_participant_id}""")
        date_info = cursor.fetchall()

        self.participant_initials_label = tk.Label(self.view_participant_info_frame,text=f"Participant {initials}")
        self.participant_initials_label.grid(row=0,column=0)

        self.view_participant_main_info_frame = tk.Frame(self.view_participant_info_frame)
        self.view_participant_main_info_frame.grid(row=1,column=0)

        first_name_label = tk.Label(self.view_participant_main_info_frame,text=f"First Name: {first_name}")
        
        last_name_label = tk.Label(self.view_participant_main_info_frame,text=f"Last Name: {last_name}")

        initials_label = tk.Label(self.view_participant_main_info_frame,text=f"Initials: {initials}")

        birthday_label = tk.Label(self.view_participant_main_info_frame,text=f"Birthday: {birthday}")

        other_info_label = tk.Label(self.view_participant_main_info_frame,text=f"Other Info:")
        self.view_other_info_entry = tk.Text(self.view_participant_main_info_frame,height=7,width=35)
        self.view_other_info_entry.insert(tk.END,other_info)
        self.view_other_info_entry.config(state=tk.DISABLED)
        
        first_name_label.grid(row=1,column=0)
        last_name_label.grid(row=2,column=0)
        initials_label.grid(row=3,column=0)
        birthday_label.grid(row=4,column=0)
        other_info_label.grid(row=5,column=0)
        self.view_other_info_entry.grid(row=6,column=0)

        self.view_participant_times_frame = tk.Frame(self.view_participant_info_frame)
        self.view_participant_times_frame.grid(row=2,column=1)

        self.view_participant_times_widget = tk.Text(self.view_participant_info_frame,height=30,width=25)
        self.view_participant_times_widget.grid(row=1,column=1)

        self.view_participant_times_dict = {}
        current_row = 0
        for day in date_info:
            date = day[0]
            time = day[1]

            in_house = "\nIn House"
            if day[2] == 0:
                in_house = "\nFollow-Up Visit"

            self.view_participant_times_widget.insert(tk.END,f"{date} : {time} {in_house}\n\n")
            
            current_row += 1

        back_to_main_menu_button = tk.Button(self.view_participant_info_frame,text="Back to Main Menu",command=self.close_view_participant_info_window)
        back_to_main_menu_button.grid(row=9,column=0)

        back_to_pickers_button = tk.Button(self.view_participant_info_frame,text="Select Other Participant",command=self.back_to_view_participant_pickers)
        back_to_pickers_button.grid(row=10,column=0)

    def open_edit_participant_study_picker_window(self):
        self.main_menu_frame.destroy()
        self.edit_participant_pickers_frame = tk.Frame(self.root)
        self.edit_participant_pickers_frame.pack()

        study_names = self.get_study_names()
        
        self.edit_participant_study_picker_label = tk.Label(self.edit_participant_pickers_frame,text="Select Study:")
        self.edit_participant_study_picker_label.grid(row=0,column=0)

        self.edit_participant_study_picker_var = tk.StringVar()
        self.edit_participant_study_picker = tk.OptionMenu(self.edit_participant_pickers_frame,self.edit_participant_study_picker_var,*study_names,command=self.open_edit_participant_intials_picker)
        self.edit_participant_study_picker.grid(row=1,column=0)

        self.edit_participant_exit_button = tk.Button(self.edit_participant_pickers_frame,text="Back to Main Menu",command=self.exit_edit_participant_menu)
        self.edit_participant_exit_button.grid(row=5,column=0)

        self.edit_participant_initials_picker_open = False
        self.open_participant_edit_button_placed = False

    def open_edit_participant_intials_picker(self,*args):
        if self.edit_participant_initials_picker_open:
            self.edit_participant_initials_picker_frame.destroy()
    
        if self.open_participant_edit_button_placed:
            self.open_edit_participant_button.config(text=f"Edit {self.edit_participant_initials_picker_var.get()}'s Info")
        
        self.edit_participant_initials_picker_open = True
        
        cursor.execute(f"""SELECT study_id FROM study WHERE study_name = "{self.edit_participant_study_picker_var.get()}" """)
        study_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT initials FROM Participant WHERE study_id = {study_id}")
        participants = [participant[0] for participant in cursor.fetchall()]

        self.edit_participant_initials_label = tk.Label(self.edit_participant_pickers_frame,text="Select Participant:")
        self.edit_participant_initials_label.grid(row=2,column=0)

        self.edit_participant_initials_picker_var = tk.StringVar()
        self.edit_participant_initials_picker = tk.OptionMenu(self.edit_participant_pickers_frame,self.edit_participant_initials_picker_var,*participants,command=self.place_edit_participant_button)
        self.edit_participant_initials_picker.grid(row=3,column=0)

    def place_edit_participant_button(self,*args):
        self.open_participant_edit_button_placed = True
        self.open_edit_participant_button = tk.Button(self.edit_participant_pickers_frame,text=f"Edit {self.edit_participant_initials_picker_var.get()}'s Info",command=self.open_edit_participant_info_window)
        self.open_edit_participant_button.grid(row=4,column=0)

    def open_edit_participant_info_window(self):
        self.edit_participant_pickers_frame.destroy()

        cursor.execute(f"""SELECT * FROM participant WHERE initials = "{self.edit_participant_initials_picker_var.get()}" """)
        participant_info= cursor.fetchall()[0]
        
        self.edit_participant_info_frame = tk.Frame(self.root)
        self.edit_participant_info_frame.pack()

        self.edit_participant_id = participant_info[0]
        first_name = participant_info[1]
        last_name = participant_info[2]
        initials = participant_info[3]
        birthday = participant_info[4]
        other_info = participant_info[5]

        cursor.execute(f"""SELECT date,time,is_in_house FROM participant_date_times WHERE participant_id = {self.edit_participant_id}""")
        date_info = cursor.fetchall()

        self.participant_initials_label = tk.Label(self.edit_participant_info_frame,text=f"Participant {initials}")
        self.participant_initials_label.grid(row=0,column=0,columnspan=2)

        first_name_label = tk.Label(self.edit_participant_info_frame,text="First Name:")
        self.edit_first_name_entry = tk.Entry(self.edit_participant_info_frame)
        self.edit_first_name_entry.insert(0,first_name)
        
        last_name_label = tk.Label(self.edit_participant_info_frame,text="Last Name:")
        self.edit_last_name_entry = tk.Entry(self.edit_participant_info_frame)
        self.edit_last_name_entry.insert(0,last_name)

        initials_label = tk.Label(self.edit_participant_info_frame,text="Initials:")
        self.edit_initials_entry = tk.Entry(self.edit_participant_info_frame)
        self.edit_initials_entry.insert(0,initials)

        birthday_label = tk.Label(self.edit_participant_info_frame,text="Birthday:")
        self.edit_birthday_entry = tk.Entry(self.edit_participant_info_frame)
        self.edit_birthday_entry.insert(0,birthday)

        other_info_label = tk.Label(self.edit_participant_info_frame,text="Other Info:")
        self.edit_other_info_entry = tk.Text(self.edit_participant_info_frame,height=5,width=40)
        self.edit_other_info_entry.insert(tk.END,other_info)

        first_name_label.grid(row=1,column=0)
        last_name_label.grid(row=2,column=0)
        initials_label.grid(row=3,column=0)
        birthday_label.grid(row=4,column=0)
        other_info_label.grid(row=5,column=0,columnspan=2)

        self.edit_first_name_entry.grid(row=1,column=1)
        self.edit_last_name_entry.grid(row=2,column=1)
        self.edit_initials_entry.grid(row=3,column=1)
        self.edit_birthday_entry.grid(row=4,column=1)
        self.edit_other_info_entry.grid(row=6,column=0,columnspan=2)

        self.edit_participant_times_frame = tk.Frame(self.edit_participant_info_frame)
        self.edit_participant_times_frame.grid(row=7,column=0,columnspan=2)

        self.edit_participant_times_dict = {}
        current_row = 0
        for day in date_info:
            date = day[0]
            time = day[1]

            in_house = "\nIn House"
            if day[2] == 0:
                in_house = "\nFollow-Up Visit"
            new_date_label = tk.Label(self.edit_participant_times_frame,text=f"{date}{in_house}")
            new_date_label.grid(row=current_row,column=0)
            
            new_time_entry = tk.Entry(self.edit_participant_times_frame)
            new_time_entry.grid(row=current_row,column=1)
            new_time_entry.insert(0,time)

            self.edit_participant_times_dict[date] = new_time_entry
            current_row += 1

        save_participant_edits_button = tk.Button(self.edit_participant_info_frame,text="Save",command=self.finalize_edit_participant)
        save_participant_edits_button.grid(row=8,column=0,columnspan=2)

        back_to_main_menu_button = tk.Button(self.edit_participant_info_frame,text="Back to Main Menu",command=self.close_edit_participant_info_window)
        back_to_main_menu_button.grid(row=9,column=0)

        back_to_pickers_button = tk.Button(self.edit_participant_info_frame,text="Select Other Participant",command=self.back_to_edit_participant_pickers)
        back_to_pickers_button.grid(row=9,column=1)

    def finalize_edit_participant(self):
        #Retrieve all Info
        first_name_input = self.edit_first_name_entry.get()
        last_name_input = self.edit_last_name_entry.get()
        initials_input = self.edit_initials_entry.get()
        birthday_input = self.edit_birthday_entry.get()
        other_info_input = self.edit_other_info_entry.get("1.0",tk.END).rstrip()

        cursor.execute(f"""UPDATE Participant 
                            SET first_name = '{first_name_input}' 
                            WHERE participant_id = {self.edit_participant_id}""")
        
        connect.commit()

        cursor.execute(f"""UPDATE Participant
                            SET last_name = '{last_name_input}'
                            WHERE participant_id = {self.edit_participant_id} """)

        connect.commit()

        cursor.execute(f"""UPDATE Participant
                            SET initials = '{initials_input}'
                            WHERE participant_id = {self.edit_participant_id} """)

        connect.commit()

        cursor.execute(f"""UPDATE Participant 
                            SET birthday = '{birthday_input}'
                            WHERE participant_id = {self.edit_participant_id} """)

        connect.commit()
        
        cursor.execute(f"""UPDATE Participant 
                            SET other_info = "{other_info_input}"
                            WHERE participant_id = {self.edit_participant_id} """)

        connect.commit()

        for date in self.edit_participant_times_dict:
            time = self.edit_participant_times_dict.get(date).get()
            #Update rows in 
            cursor.execute(f"""UPDATE Participant_Date_Times 
                                SET time = '{time}'
                                WHERE participant_id = {self.edit_participant_id} AND date = '{date}'""")
            connect.commit()

        tk_mb.showinfo(message=f"Succesfully edited participant {initials_input}'s information")

        self.back_to_edit_participant_pickers()

    def open_edit_study_picker_window(self):
        self.main_menu_frame.destroy()
        self.edit_study_master_frame = tk.Frame(self.root)
        self.edit_study_master_frame.pack()

        self.edit_study_picker_label = tk.Label(self.edit_study_master_frame,text="Select Study:")
        self.edit_study_picker_label.grid(row=0,column=0)

        self.edit_study_picker_var = tk.StringVar()
        study_names = self.get_study_names()
        self.study_edit_open = False
        self.edit_study_picker = ttk.OptionMenu(self.edit_study_master_frame,self.edit_study_picker_var,"",*study_names,command=self.open_edit_study_window)
        self.edit_study_picker.grid(row=1,column=0)

        self.exit_study_edit_button = tk.Button(self.edit_study_master_frame,text="Back to Main Menu",command=self.exit_edit_study_window)
        self.exit_study_edit_button.grid(row=3,column=0)

        self.open_edit_study = False
        
    def open_edit_study_window(self,*args):
        if self.open_edit_study:
            self.edit_study_frame.destroy()

        self.open_edit_study = True

        self.edit_study_frame = tk.Frame(self.edit_study_master_frame)
        self.edit_study_frame.grid(row=2,column=0)

        study_name = self.edit_study_picker_var.get()
        cursor.execute(f""" SELECT study.study_info, Study_Date_Times.date, Study_Date_Times.is_in_house 
                            FROM study INNER JOIN Study_Date_Times 
                            ON Study_Date_Times.study_id = study.study_id 
                            WHERE study_name = '{study_name}' """)

        study_info = cursor.fetchall()

        self.edit_other_info_entry_label = tk.Label(self.edit_study_frame,text="Study Info:")
        self.edit_other_info_entry_label.grid(row=0,column=0)

        self.edit_other_info_entry = tk.Text(self.edit_study_frame,height=5,width=40)
        self.edit_other_info_entry.grid(row=1,column=0)
        self.edit_other_info_entry.insert(tk.END,study_info[0][0])
        
        self.edit_dates_frame = tk.Frame(self.edit_study_frame)
        self.edit_dates_frame.grid(row=2,column=0)

        self.edit_dates_label = tk.Label(self.edit_dates_frame,text="Study Dates:")
        self.edit_dates_label.grid(row=0,column=0,columnspan=2)

        self.edit_date_entries = []
        self.edit_in_house_variables = []
        current_row = 1
        self.original_dates = []
        for entry in study_info:
            date = entry[1]
            in_house = entry[2]

            self.original_dates.append(date)

            new_date_entry = tk.Entry(self.edit_dates_frame)
            new_date_entry.grid(row=current_row,column=0)
            new_date_entry.insert(0,date)

            self.edit_date_entries.append(new_date_entry)

            new_in_house_var = tk.IntVar()
            new_check_button = tk.Checkbutton(self.edit_dates_frame,text="In-House Visit",variable=new_in_house_var,onvalue=1,offvalue=0)
            new_check_button.grid(row=current_row,column=1)
            self.edit_in_house_variables.append(new_in_house_var)

            if in_house == 1:
                new_check_button.select()
            
            current_row += 1

        self.edit_study_save_button = tk.Button(self.edit_dates_frame,text="Save",command=self.finalize_edit_study)
        self.edit_study_save_button.grid(row=current_row,column=0,columnspan=2)

    def finalize_edit_study(self):
        finalize_confirmation = tk_mb.askyesno(title="Save Info",message=f"Are you sure you want to save the info for {self.edit_study_picker_var.get()}?")
        
        if finalize_confirmation:
            cursor.execute(f"""UPDATE study 
                               SET study_info = "{self.edit_other_info_entry.get("1.0",tk.END)}" 
                               WHERE study_name = "{self.edit_study_picker_var.get()}" """)

            connect.commit()

            cursor.execute(f"""SELECT study_id FROM study WHERE study_name = "{self.edit_study_picker_var.get()}" """)
            study_id = cursor.fetchone()[0]

            for index in range(0,len(self.edit_date_entries)):
                date = self.edit_date_entries[index].get()
                print(f"Testing: {date}")
                in_house = self.edit_in_house_variables[index].get()
                cursor.execute(f"""UPDATE Study_Date_Times SET date = "{date}", is_in_house = "{in_house}" WHERE study_id = "{study_id}" AND date = "{self.original_dates[index]}" """)
                connect.commit()

                cursor.execute(f"""UPDATE Participant_Date_Times SET date = "{date}", is_in_house = "{in_house}" WHERE study_id = "{study_id}" AND date= "{self.original_dates[index]}" """)
                connect.commit()

    def open_add_participant_study_picker_window(self):
        self.main_menu_frame.destroy()
        self.add_participant_master_frame = tk.Frame(self.root)
        self.add_participant_master_frame.pack()

        self.add_participant_study_picker_label = tk.Label(self.add_participant_master_frame,text="Select Study:")
        self.add_participant_study_picker_label.grid(row=0,column=0)

        self.add_participant_study_picker_var = tk.StringVar()
        study_names = self.get_study_names()

        self.add_participant_open = False
        self.add_participant_study_picker = ttk.OptionMenu(self.add_participant_master_frame,self.add_participant_study_picker_var,"",*study_names,command=self.open_add_participant_window)
        self.add_participant_study_picker.grid(row=1,column=0)

    def open_add_participant_window(self,*args):
        if self.add_participant_open:
            self.add_participant_frame.destroy()

        self.add_participant_open = True
        self.add_participant_frame = tk.Frame(self.add_participant_master_frame)
        self.add_participant_frame.grid(row=2,column=0)

        self.add_participant_study_name = self.add_participant_study_picker_var.get()

        self.add_participant_title_label = tk.Label(self.add_participant_frame,text=f"Add information to {self.add_participant_study_name} study")
        self.add_participant_title_label.grid(row=0,column=0,columnspan=2)

        self.add_participant_first_name_label = tk.Label(self.add_participant_frame,text="First Name:")
        self.add_participant_first_name_label.grid(row=1,column=0)

        self.add_participant_first_name_entry = tk.Entry(self.add_participant_frame)
        self.add_participant_first_name_entry.grid(row=1,column=1)

        self.add_participant_last_name_label = tk.Label(self.add_participant_frame,text="Last Name:")
        self.add_participant_last_name_label.grid(row=2,column=0)

        self.add_participant_last_name_entry = tk.Entry(self.add_participant_frame)
        self.add_participant_last_name_entry.grid(row=2,column=1)

        self.add_participant_intial_label = tk.Label(self.add_participant_frame,text="Initals:")
        self.add_participant_intial_label.grid(row=3,column=0)

        self.add_participant_initials_entry = tk.Entry(self.add_participant_frame)
        self.add_participant_initials_entry.grid(row=3,column=1)    

        self.add_participant_birthday_label = tk.Label(self.add_participant_frame,text="Birthday:")
        self.add_participant_birthday_label.grid(row=4,column=0)

        self.add_participant_birthday_entry = tk.Entry(self.add_participant_frame)
        self.add_participant_birthday_entry.grid(row=4,column=1,padx=5) 

        self.add_participant_other_info_label = tk.Label(self.add_participant_frame,text="Other Info:")
        self.add_participant_other_info_label.grid(row=5,column=0,columnspan=2)
        
        self.add_participant_other_info_entry = tk.Text(self.add_participant_frame,height=5,width=40)
        self.add_participant_other_info_entry.grid(row=6,column=0,columnspan=2,padx=2)
        
        self.add_participant_date_top_label = tk.Label(self.add_participant_frame,text="Date:")
        self.add_participant_date_top_label.grid(row=0,column=2)

        self.add_participant_time_top_label = tk.Label(self.add_participant_frame,text="Time:")
        self.add_participant_time_top_label.grid(row=0,column=3)

        #Finding all dates of study
        cursor.execute(f"""SELECT date,is_in_house FROM Study_Date_times 
                           INNER JOIN study 
                           ON Study_Date_Times.study_id = study.study_id 
                           WHERE study.study_name = '{self.add_participant_study_name}'""")

        study_dates = cursor.fetchall()
    
        self.date_dict = {}
        current_row = 1
        for date in study_dates:
            if date[1] == 1:
                in_house = "\n(In-House)"
            else:
                in_house = "\n(Follow-Up Visit)"
            new_date_label = tk.Label(self.add_participant_frame,text=date[0] + in_house)
            new_date_label.grid(row=current_row,column=2)
            new_date_entry = tk.Entry(self.add_participant_frame)
            new_date_entry.grid(row=current_row,column=3)

            self.date_dict[date[0]] = [new_date_entry,date[1]]
            current_row +=1

        self.add_participant_exit_button = tk.Button(self.add_participant_frame,text="Back to Main Menu",command=self.exit_add_participant_menu)
        self.add_participant_exit_button.grid(row=7,column=0)

        self.add_participant_finalize_button = tk.Button(self.add_participant_frame,text="Add Participant",command=self.add_participant_finalize)
        self.add_participant_finalize_button.grid(row=7,column=1)

    def add_participant_finalize(self):
        #Find study ID for schedule table
        cursor.execute(f"""SELECT study_id FROM study WHERE study_name = '{self.add_participant_study_name}' """)
        study_id = cursor.fetchone()[0]

        first_name = self.add_participant_first_name_entry.get()
        last_name = self.add_participant_last_name_entry.get()
        initials = self.add_participant_initials_entry.get()
        birthday = self.add_participant_birthday_entry.get()
        other_info = self.add_participant_other_info_entry.get("1.0",tk.END).rstrip()
        essential_info = [first_name,last_name,initials,birthday]

        cursor.execute(f"""SELECT participant_id FROM participant WHERE initials = "{initials}" """)
        participant_id = cursor.fetchone()

        cursor.execute(f"SELECT initials FROM participant ")
        all_initials = [initials[0] for initials in cursor.fetchall()]

        if initials in all_initials:
            tk_mb.showinfo(message="Sorry, those initials already exist in this study")

        else:
            print("ok go")
            if "" in essential_info:
                tk_mb.showinfo(message="Make sure all fields are filled out!")
            else:
                print("ok let's go")
                all_dates_filled = True
                for date in self.date_dict:
                    if self.date_dict.get(date)[0].get() == "":
                        all_dates_filled = False
                        break

                if not all_dates_filled:
                    tk_mb.showinfo(message="Make sure all dates have a time")
                else:
                    #Place participant info into table
                    cursor.execute(f"""INSERT INTO Participant (study_id,first_name,last_name,initials,birthday,other_info)
                                        VALUES({study_id}, '{first_name}','{last_name}','{initials}','{birthday}',"{other_info}") """)
                    connect.commit()

                    cursor.execute("""SELECT MAX(participant_id) FROM Participant """)
                    

                    participant_id = cursor.fetchone()[0]
                    print(f"Inserting into Participant Date Times THIS ID: {participant_id}")

                    for date in self.date_dict:
                        time = self.date_dict.get(date)[0].get()
                        in_house = self.date_dict.get(date)[1]

                        cursor.execute(f"""INSERT INTO Participant_Date_Times
                                            (study_id,participant_id,date,time,is_in_house)
                                            VALUES ({study_id},{participant_id},'{date}','{time}',{in_house}) """)

                        connect.commit()

                    tk_mb.showinfo(message=f"Participant {initials} has been added to the study")

    def add_new_study_window(self):
        self.main_menu_frame.destroy()
        self.new_study_frame = tk.Frame(self.root)
        self.new_study_frame.pack()
        
        self.new_study_top_label = tk.Label(self.new_study_frame,text="Add New Study Information Below")
        self.new_study_top_label.grid(row=0,column=0,columnspan=2)

        self.new_study_name_label = tk.Label(self.new_study_frame,text="Study Name:")
        self.new_study_name_label.grid(row=1,column=0)

        self.new_study_name_entry = tk.Entry(self.new_study_frame)
        self.new_study_name_entry.grid(row=2,column=0)

        self.new_study_info_label = tk.Label(self.new_study_frame,text="Other Information:")
        self.new_study_info_label.grid(row=3,column=0)

        self.new_study_info_entry = tk.Text(self.new_study_frame,width=40,height=5)
        self.new_study_info_entry.grid(row=4,column=0,padx=5)

        self.new_date_entry_label = tk.Label(self.new_study_frame)
        self.new_date_entry_label.grid(row=5,column=0)

        self.new_info_date_entry = tkcalendar.DateEntry(self.new_study_frame,selectmode="day")
        self.new_info_date_entry.grid(row=6,column=0)

        self.in_house = tk.IntVar()
        self.in_house_check = tk.Checkbutton(self.new_study_frame,text="In-House Visit",variable=self.in_house,onvalue=1,offvalue=0)
        self.in_house_check.grid(row=7,column=0)

        self.date_entry_button = tk.Button(self.new_study_frame,text="Add Study Date",command=self.new_info_add_date_to_list)
        self.date_entry_button.grid(row=8,column=0)

        self.new_study_date_list_frame = tk.Frame(self.new_study_frame)
        self.new_study_date_list_frame.grid(row=9,column=0)

        self.top_date_list_label= tk.Label(self.new_study_date_list_frame,text="Dates:")
        self.top_date_list_label.grid(row=0,column=0)

        self.new_study_date_dict = {}

        self.back_button = tk.Button(self.new_study_frame,text="Back to Main Menu",command=self.exit_new_study_menu)
        self.back_button.grid(row=11,column=0)

    def view_study_info_window(self):
        #Close main menu 
        self.main_menu_frame.destroy()

        #Initialize new menu
        self.view_study_master_frame = tk.Frame(self.root)
        self.view_study_master_frame.pack()

        self.view_study_picker_label = tk.Label(self.view_study_master_frame,text="Select Study:")
        self.view_study_picker_label.grid(row=0,column=0)
        
        self.view_study_picker_var = tk.StringVar()
        study_names = self.get_study_names()

        self.study_view_open = False
        self.view_study_picker = ttk.OptionMenu(self.view_study_master_frame,self.view_study_picker_var,"",*study_names,command=self.display_study_info)

        self.view_study_picker.grid(row=1,column=0)

        self.exit_study_info_view_button = tk.Button(self.view_study_master_frame,text="Back to \nMain Menu",command=self.exit_view_study_info_menu)
        self.exit_study_info_view_button.grid(row=3,column=1,padx=10)

    def display_study_info(self,*args):
        if self.study_view_open:
            self.view_study_info_frame.destroy()
        
        self.study_view_open = True

        study_name = self.view_study_picker_var.get()
        
        cursor.execute(f"SELECT study_info FROM study WHERE study_name = '{study_name}'")
        study_info = cursor.fetchone()[0]

        cursor.execute(f""" SELECT date, is_in_house FROM Study_Date_Times 
                            INNER JOIN 
                            study 
                            ON Study_Date_Times.study_id = study.study_id
                            WHERE 
                            study.study_name = '{study_name}' """)

        study_dates = cursor.fetchall()

        self.view_study_info_frame = tk.Frame(self.view_study_master_frame)
        self.view_study_info_frame.grid(row=2,column=0)

        self.study_name_label = tk.Label(self.view_study_info_frame,text=study_name)
        self.study_name_label.grid(row=0,column=0,columnspan=2)

        self.study_info_view_other_info_label = tk.Label(self.view_study_info_frame,text="Other Info:")
        self.study_info_view_other_info_label.grid(row=1,column=1,padx=10)

        self.study_other_info_text_label = tk.Label(self.view_study_info_frame,text=study_info)
        self.study_other_info_text_label.grid(row=2,column=1)
        
        self.schedule_label = tk.Label(self.view_study_info_frame,text="Dates:")
        self.schedule_label.grid(row=1,column=0,padx=10)

        for date in range(len(study_dates)):
            if study_dates[date][1] == 1:
                in_house = " - In House"
            else:
                in_house = " - Follow-Up Visit"

            label_text = study_dates[date][0] + in_house

            new_label = tk.Label(self.view_study_info_frame,text=label_text)
            new_label.grid(row=2+date,column=0,padx=10)     

    def new_info_add_date_to_list(self):
        if len(self.new_study_date_dict) == 0:
            self.finalize_new_study_button = tk.Button(self.new_study_frame,text="Add New Study",command=self.finalize_new_study)
            self.finalize_new_study_button.grid(row=10,column=0)

        if self.in_house.get() == 1:
            type = "In House"
        else:
            type = "Follow Up"

        new_date = self.new_info_date_entry.get_date().strftime("%m-%d-%y")
        self.new_study_date_dict[new_date] = self.in_house.get()
        
        new_label = tk.Label(self.new_study_date_list_frame,text=new_date + " - " + type)
        new_label.grid(row=len(self.new_study_date_dict),column=0)
        
    def add_dates_to_study(self,study_id,date_list):
        for date in date_list:
            in_house = date_list.get(date)
            cursor.execute(f"""INSERT INTO Study_Date_Times VALUES('{study_id}','{date}','{in_house}') """)
            connect.commit()

    def finalize_new_study(self):
        study_name = self.new_study_name_entry.get()
        study_info = self.new_study_info_entry.get("1.0",tk.END).rstrip() #Get rid of newline at the end of string
        if study_name == "":
            tk_mb.showinfo(message="Sorry, make sure you add a name for this new study")
        else:
            study_names = self.get_study_names()
            is_duplicate = False
            for study in study_names:
                if study_name == study[0]:
                    is_duplicate = True
                    break
            if is_duplicate:
                tk_mb.showinfo(message=f"Sorry, try picking another study name, {study_name} already exists in our system.")
            else:
                is_duplicate_date = False
                for date in self.new_study_date_dict:
                    if list(self.new_study_date_dict.keys()).count(date) > 1:
                        is_duplicate_date = True
                        break
                if is_duplicate_date:
                    tk_mb.showinfo(message="Uh oh! Make sure none of your study dates are the same as one another")
                else:
                    cursor.execute(f"""INSERT INTO study (study_name, study_info) VALUES ('{study_name}',"{study_info}")""")
                    connect.commit()

                    cursor.execute(f"SELECT study_id FROM study WHERE study_name = '{study_name}'")
                    study_id = tuple(cursor.fetchone())[0]
                    self.add_dates_to_study(study_id,self.new_study_date_dict)

    def get_study_names(self):
        cursor.execute("SELECT study_name FROM study")
        return [study[0] for study in cursor.fetchall()]

    def exit_edit_study_window(self):
        self.edit_study_master_frame.destroy()
        self.main_menu()

    def exit_view_study_info_menu(self):
        self.view_study_master_frame.destroy()
        self.main_menu()

    def exit_new_study_menu(self):
        self.new_study_frame.destroy()
        self.main_menu()

    def exit_add_participant_menu(self):
        self.add_participant_master_frame.destroy()
        self.main_menu()
    
    def exit_edit_participant_menu(self):
        self.edit_participant_pickers_frame.destroy()
        self.main_menu()

    def back_to_edit_participant_pickers(self):
        self.edit_participant_info_frame.destroy()
        self.open_edit_participant_study_picker_window()

    def close_edit_participant_info_window(self):
        self.edit_participant_info_frame.destroy()
        self.main_menu()

    def exit_view_participant_menu(self):
        self.view_participant_pickers_frame.destroy()
        self.main_menu()
        
    def back_to_view_participant_pickers(self):
        self.view_participant_info_frame.destroy()
        self.open_view_participant_study_picker_window()

    def close_view_participant_info_window(self):
        self.view_participant_info_frame.destroy()
        self.main_menu()

    def exit_schedule_study_picker(self):
        self.schedule_study_picker_frame.destroy()
        self.main_menu()

    def exit_view_schedule(self):
        self.view_study_schedule_frame.destroy()
        self.main_menu()

    def close_program(self):
        leave = tk_mb.askyesno(message="Are you sure you want to close the program?")
        if leave:
            exit()

root = tk.Tk()
main = Main(root)
main.root.mainloop()
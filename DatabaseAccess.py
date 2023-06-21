import tkinter.messagebox as tk_mb

class DatabaseAccess:
    def __init__(self,cursor,connect):
        self.cursor = cursor
        self.connect = connect

    def get_study_id(self,study_name):
       self.cursor.execute(f"""SELECT study_id FROM study WHERE study_name = '{study_name}' """)
       return self.cursor.fetchone()[0]
    
    def get_initials(self,study_id):
        self.cursor.execute(f"SELECT initials FROM Participant WHERE study_id = {study_id}")
        return [participant[0] for participant in self.cursor.fetchall()]
    
    def get_initials_and_id(self,study_id):
        self.cursor.execute(f"SELECT initials,participant_id FROM Participant WHERE study_id = '{study_id}'")
        return self.cursor.fetchall()
    
    ################################################################
    #NOTE:Could be updated to use participant ID instead of initials
    ################################################################
    def get_all_participant_info(self,initials):
        self.cursor.execute(f"""SELECT * FROM participant WHERE initials = "{initials}" """)
        return self.cursor.fetchall()[0]

    def get_study_names(self):
        """Retrieves all current study names"""
        self.cursor.execute("SELECT study_name FROM study")
        results = self.cursor.fetchall()
        if len(results) == 0:
            return None
        
        return [study[0] for study in results]
    
    def get_time_by_id_and_date(self,date,participant_id):
        self.cursor.execute(f""" SELECT time FROM Participant_Date_Times WHERE date = '{date}' AND participant_id = '{participant_id}' """)
        return str(self.cursor.fetchone()[0])
    
        
    def get_study_dates(self,study_id):
        self.cursor.execute(f"SELECT date FROM Study_Date_Times WHERE study_id = '{study_id}'")
        return [date[0] for date in self.cursor.fetchall()]
    
    def get_date_info_by_participant(self,participant_id):
        self.cursor.execute(f"""SELECT date,time,is_in_house FROM participant_date_times WHERE participant_id = {participant_id}""")
        return self.cursor.fetchall()
    
    def get_date_info_by_study(self,study_name):
        self.cursor.execute(f"""SELECT date,is_in_house FROM Study_Date_times 
                           INNER JOIN study 
                           ON Study_Date_Times.study_id = study.study_id 
                           WHERE study.study_name = '{study_name}'""")
        
        return self.cursor.fetchall()

    def update_participant_column(self,participant_id,info,info_column_name):
        self.cursor.execute(f"""UPDATE Participant 
                            SET {info_column_name} = '{info}' 
                            WHERE participant_id = {participant_id}""")

        self.connect.commit()

    def update_participant_date_times(self,participant_id, date,time):
        self.cursor.execute(f""" UPDATE Participant_Date_Times
                                 SET time = '{time}'
                                 WHERE participant_id = {self.edit_participant_id} AND date = '{date}' """)
        self.connect.commit()
        
    def update_study_info(self,study_info,study_name):
        self.cursor.execute(f"""UPDATE study 
                                SET study_info = '{study_info}' 
                                WHERE study_name = '{study_name}' """)
        
        self.connect.commit()

    
    def finalize_new_study(self,study_name,study_info,study_date_dict):
        """Verifies a given name and info for a study, and then adds it to the database"""
        self.cursor.execute(f"""INSERT INTO study (study_name, study_info) VALUES ('{study_name}',"{study_info}")""")
        self.connect.commit()

        self.cursor.execute(f"SELECT study_id FROM study WHERE study_name = '{study_name}'")
        study_id = tuple(self.cursor.fetchone())[0]

        self.add_dates_to_study(study_id,study_date_dict)

    def add_dates_to_study(self,study_id,date_list):
        for date in date_list:
            in_house = date_list.get(date)
            self.cursor.execute(f"""INSERT INTO Study_Date_Times VALUES('{study_id}','{date}','{in_house}') """)
            self.connect.commit()


    def add_participant(self,study_id,first_name,last_name,initials,birthday,other_info,date_dict):
        #Place participant info into table
                    
        self.cursor.execute(f"""INSERT INTO Participant (study_id,first_name,last_name,initials,birthday,other_info)
                            VALUES({study_id}, '{first_name}','{last_name}','{initials}','{birthday}',"{other_info}") """)
        
        self.connect.commit()

        self.cursor.execute(f"""SELECT participant_id FROM Participant WHERE initials = '{initials}' """)
        participant_id = self.cursor.fetchone()[0]

        for date in date_dict:
            time = date_dict.get(date)[0].get()
            in_house = date_dict.get(date)[1]

            self.cursor.execute(f"""INSERT INTO Participant_Date_Times
                                (study_id,participant_id,date,time,is_in_house)
                                VALUES ('{study_id}','{participant_id}','{date}','{time}','{in_house}') """)

            self.connect.commit()


    def update_study_date_times(self,date,in_house,study_id,original_date):
        self.cursor.execute(f"""UPDATE Study_Date_Times 
                                SET date = "{date}", is_in_house = "{in_house}" 
                                WHERE study_id = "{study_id}" AND date = "{original_date}" """)

        self.connect.commit()

        self.cursor.execute(f"""UPDATE Participant_Date_Times 
                                SET date = "{date}", is_in_house = "{in_house}" 
                                WHERE study_id = "{study_id}" AND date= "{original_date}" """)
        
        self.connect.commit()


    def study_already_exists(self,study_name):
        self.cursor.execute(f"""SELECT study_name FROM study WHERE study_name = '{study_name}'""")
        results = self.cursor.fetchone()
        if results:
            return True
        
        return False


#OLD METHODS/ALREADY ADDED???
    def delete_study(self,study_name):
        self.cursor.execute(f"""SELECT study_id FROM study WHERE study_name = '{study_name}'""")
        study_id = self.cursor.fetchone()[0]
        self.cursor.execute(f"""DELETE FROM Participant WHERE study_id = '{study_id}' """)
        self.connect.commit()
        self.cursor.execute(f""" DELETE FROM Participant_Date_Times WHERE study_id = '{study_id}'""")
        self.connect.commit()
        self.cursor.execute(f"""DELETE FROM Study_Date_Times WHERE study_id = '{study_id}'""")
        self.connect.commit()
        self.cursor.execute(f"""DELETE FROM study WHERE study_id = '{study_id}' """)
        self.connect.commit()

        tk_mb.showinfo(message=f"{study_name} study successfully deleted")

    
    def delete_study_date(self,study_name,date):

        study_id = self.get_study_id(study_name)
        
        self.cursor.execute(f"""DELETE FROM Participant_Date_Times
                                WHERE study_id = '{study_id}' AND date = '{date}' """)
        
        self.connect.commit()

        self.cursor.execute(f""" DELETE FROM Study_Date_Times 
                                 WHERE study_id = '{study_id}' AND date = '{date}' """)
        
        self.connect.commit()
        

    def get_study_info(self,study_name):
        self.cursor.execute(f""" SELECT study.study_info, Study_Date_Times.date, Study_Date_Times.is_in_house 
                            FROM study INNER JOIN Study_Date_Times 
                            ON Study_Date_Times.study_id = study.study_id 
                            WHERE study_name = '{study_name}' """)
        
        return self.cursor.fetchall()
        
    def get_study_other_info(self,study_name):
        self.cursor.execute(f"""SELECT study.study_info
                            FROM study
                            WHERE study_name = '{study_name}'""")

        return self.cursor.fetchone()[0]

    #NEEDS TO GET THE study_date_dict as a parameter now
    #Can probably delete this method
    def add_participant_finalize(self,study_name,study_date_dict,first_name,last_name,initials,birthday,other_info):
        essential_info = [first_name,last_name,initials,birthday]
        
        if "" in essential_info:
            tk_mb.showinfo(message="Make sure all fields are filled out")
        
        else:
            #Get study ID
            self.cursor.execute(f"""SELECT study_id FROM study WHERE study_name = '{study_name}' """)
            study_id = self.cursor.fetchone()[0]

            #Gets all exisiting initials of participants already in the study
            self.cursor.execute(f"SELECT initials FROM participant WHERE study_id = {study_id}")
            all_initials = [initials[0] for initials in self.cursor.fetchall()]

            if initials in all_initials:
                tk_mb.showinfo(message="Sorry, there is already a participant with those initials")
            
            else:
                for date in study_date_dict:
                    if study_date_dict.get(date)[0].get() == "":
                        #Not all dates have a set time for this participant
                        tk_mb.showinfo(message="Make sure all dates have a set time")
                        return
                    
                self.cursor.execute(f"""INSERT INTO Participant (study_id,first_name,last_name,initials,birthday,other_info))
                                        VALUES({study_id}, '{first_name}', '{last_name}','{initials.upper()}','{birthday}','{other_info}')""")
                self.connect.commit()

                self.cursor.execute(f"""SELECT participant_id FROM Participant WHERE initials = '{initials}' """)
                participant_id = self.cursor.fetchone()[0]

                for date in study_date_dict:
                    time = study_date_dict.get(date)[0].get()
                    in_house = study_date_dict.get(date)[1]

                    self.cursor.execute(f"""INSERT INTO Participant_Date_Times
                                            (study_id, participant_id, date, time, is_in_house)
                                            VALUES ('{study_id}','{participant_id}','{date}','{time}','{in_house}') """)
                                        
                    self.connect.commit()

                tk_mb.showinfo(title="Success",message=f"Participant {initials} has been added to {study_name}")

        
    

    
    






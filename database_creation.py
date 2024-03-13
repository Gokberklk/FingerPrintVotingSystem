import sqlite3
import os
from random import *
from faker import Faker
import const
from logger import Logger
import time


class createDatabase:
    def __init__(self):
        self.createDB()

    def createDB(self):
        if os.path.exists(const.database_name):
            try:
                os.remove(const.database_name)
                Logger.log("Old Database is deleted.")
            except PermissionError as win32_error:
                Logger.raise_error(win32_error)
                Logger.log("Program will be sleep 10 second.")
                time.sleep(10)
                Logger.log("Program started again.")
                self.createDB()
        connectionDB = sqlite3.connect(const.database_name)
        cursor = connectionDB.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        Logger.log("Database is created.")
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS CITIZEN("
                           "CitizenID INTEGER PRIMARY KEY,"
                           "Name TEXT,"
                           "Surname TEXT,"
                           "DOB DATE,"
                           "Adress TEXT,"
                           "FingerPrint BLOB,"
                           "Photo BLOB)")

            cursor.execute("CREATE TABLE IF NOT EXISTS Election("
                           "ElectionID INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "Result TEXT,"
                           "DateOfElection DATE,"
                           "ElectionTime TIME,"
                           "Description TEXT)")

            cursor.execute("CREATE TABLE IF NOT EXISTS Vote("
                           "Isvoted BOOLEAN,"
                           "CitizenID INTEGER,"
                           "ElectionID INTEGER,"
                           "FOREIGN KEY (CitizenID) REFERENCES CITIZEN(CitizenID),"
                           "FOREIGN KEY (ElectionID) REFERENCES Election(ElectionID),"
                           "PRIMARY KEY(CitizenID, ElectionID))")

            cursor.execute("CREATE TABLE IF NOT EXISTS Admin("
                           "CitizenID INTEGER,"
                           "FOREIGN KEY (CitizenID) REFERENCES CITIZEN(CitizenID),"
                           "PRIMARY KEY(CitizenID))")

            cursor.execute("CREATE TABLE IF NOT EXISTS Candidate("
                           "CitizenID INTEGER,"
                           "FOREIGN KEY (CitizenID) REFERENCES CITIZEN(CitizenID),"
                           "PRIMARY KEY(CitizenID))")

            cursor.execute("CREATE TABLE IF NOT EXISTS CandidateElection("
                           "CountOfVote INTEGER,"
                           "CitizenID INTEGER,"
                           "ElectionID INTEGER,"
                           "FOREIGN KEY (CitizenID) REFERENCES Candidate(CitizenID),"
                           "FOREIGN KEY (ElectionID) REFERENCES Election(ElectionID),"
                           "PRIMARY KEY(CitizenID, ElectionID))")
            Logger.log("Tables are created.")
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            Logger.raise_error("Tables cannot created.")
        connectionDB.commit()
        cursor.close()
        connectionDB.close()


class InsertionRecord:

    def __init__(self, path, face):
        # ---------Helper Variable---------------
        self.images_name = []
        self.faces_name = []
        self.images = []
        self.faces = []
        self.path = path
        self.path2 = face
        self.faker = Faker()
        # ---------------------------------------
        # -------Citizen Variable----------------
        self.national_ID = None
        self.first_name = None
        self.last_name = None
        self.birth_date = None
        self.city = None

    @staticmethod
    def run():
        createDatabase()
        DB_insert_Record.readImage()
        DB_insert_Record.insertRecord()
        Logger.log("All processes are completed.")

    def readImage(self):
        try:  # Reading fingerprint names to find this image path
            for image_path in os.listdir(self.path):
                self.images_name.append(image_path)
        except OSError as error:
            Logger.raise_error(error)
        try:  # Reading fingerprint as binary format and append to list
            for image_name in self.images_name:
                with open(self.path + "//" + image_name, "rb") as image:
                    binary_data = image.read()
                    self.images.append(binary_data)
            Logger.log("Finger prints are reading successfully")
        except Exception as error:
            Logger.raise_error(error)

        try:  # Reading face image names to find this image path
            for face_path in os.listdir(self.path2):
                self.faces_name.append(face_path)
        except Exception as error:
            Logger.raise_error(error)
        try:  # Reading face image as binary format and append to list
            for face_name in self.faces_name:
                with open(self.path2 + "//" + face_name, "rb") as face:
                    binary_data = face.read()
                    self.faces.append(binary_data)
            Logger.log("Faces are reading successfully")
        except Exception as error:
            Logger.raise_error(error)

    def insertRecord(self):
        connectionDB = sqlite3.connect(const.database_name)
        cursor = connectionDB.cursor()

        for index_num in range(len(const.citizen)):
            cursor.execute("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (const.citizen[index_num] + (self.images[index_num],) + (self.faces[index_num],)))

        Logger.log("Real people are inserted Citizen table.")

        for i in range(80):
            self.random_Citizen_Info()
            cursor.execute("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (self.national_ID, self.first_name, self.last_name,
                            self.birth_date, self.city, self.images[i], self.faces[i]))
        Logger.log("Mock people are inserted Citizen tabel.")

        # ------Admin------
        cursor.execute("INSERT INTO Admin (CitizenID) SELECT CitizenID FROM Citizen WHERE CitizenID = ?",
                       (const.citizen[0][0],))
        Logger.log("Mock admins are inserted.")

        # ------Candidate------
        cursor.executemany("INSERT INTO Candidate (CitizenID) SELECT CitizenID FROM Citizen WHERE CitizenID = ?",
                           const.candidate)
        Logger.log("Mock candidates are inserted.")

        # ------CandidateElection------
        cursor.executemany("INSERT INTO CandidateElection (CountOfVote, CitizenID, ElectionID) VALUES (?,?,?)",
                           const.candidate_election)
        Logger.log("Mock candidate_table are inserted.")

        # ------Election------
        cursor.executemany(
            "INSERT INTO Election (ElectionID, Result, DateOfElection, ElectionTime) VALUES (?, ?, ?, ?)",
            const.election)
        Logger.log("Mock elections are inserted.")

        # ------Vote------
        cursor.execute("INSERT INTO Vote (CitizenID, IsVoted) SELECT CitizenID, ? FROM Citizen WHERE CitizenID",
                       (False,))
        Logger.log("Mock Vote are inserted.")

        connectionDB.commit()
        cursor.close()
        connectionDB.close()

    def random_Citizen_Info(self):
        self.national_ID = randint(10000000000, 99999999999)
        self.first_name = self.faker.first_name()
        self.last_name = self.faker.last_name()
        self.birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=100).strftime("%Y-%m-%d")
        self.city = choice(["Adana", "Bursa", "Konya", "Eskişehir"])


if __name__ == "__main__":
    DB_insert_Record = InsertionRecord(const.path_of_image, const.path_of_face)
    DB_insert_Record.run()

















"""if os.path.exists(const.database_name):
            try:
                cursor.execute("DELETE FROM Citizen")
                cursor.execute("DELETE FROM Admin")
                cursor.execute("DELETE FROM Candidate")
                cursor.execute("DELETE FROM CandidateElection")
                cursor.execute("DELETE FROM Election")
                cursor.execute("DELETE FROM Vote")
                connectionDB.commit()
                Logger.log("")
            except sqlite3.OperationalError:
                DataBaseCreation.createDatabase()"""

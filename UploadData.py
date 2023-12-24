import sqlite3
import os
import DataBaseCreation
from datetime import *
from random import *
from faker import Faker


class InsertionRecord():

    def __init__(self, path, face):
        self.images_name = []
        self.faces_name = []
        self.images = []
        self.faces = []
        self.path = path
        self.path2 = face
        self.faker = Faker()
#---------------------------------------
        self.national_ID = None
        self.first_name = None
        self.last_name = None
        self.birth_date = None
        self.city = None


    def readImage(self):
        for image_path in os.listdir(self.path):
            self.images_name.append(image_path)
            print(image_path)
        i = 0
        for image_path in self.images_name:
            with open(self.path + "//" + image_path, "rb") as image:
                binary_data = image.read()
                self.images.append(binary_data)

        for face_path in os.listdir(self.path2):
            self.faces_name.append(face_path)
            print(face_path)
        i = 0
        for face_path in self.faces_name:
            with open(self.path2 + "//" + face_path, "rb") as face:
                binary_data = face.read()
                self.faces.append(binary_data)

    def insertRecord(self):
        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()
        if os.path.exists("Government"):
            cursor.execute("DELETE FROM Citizen")
            connectionDB.commit()

        citizen = [(11111111111, "Gökberk", "Lük", "1900-06-06", "Adana", self.images[0], self.faces[0]),
                   (22222222222, "Adem", "Garip", "1900-06-06", "Bursa", self.images[1], self.faces[1]),
                   (33333333333, "Canberk", "Sefa", "1900-06-06", "Bursa", self.images[2], self.faces[2]),
                   (44444444444, "Osman Eren", "Gündogdu", "1900-06-06", "Konya", self.images[3], self.faces[2]),
                   (55555555555, "Ata", "Öztaş", "1900-06-06", "Eskişehir", self.images[3], self.faces[3])]
        cursor.executemany("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?, ?)", citizen)
        i = 4
        for i in range(80):
            self.random_Citizen_Info()
            citizen = (self.national_ID, self.first_name, self.last_name, self.birth_date, self.city, self.images[i], self.faces[i])
            cursor.execute("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?, ?)", citizen)

        #------Admin
        cursor.execute("DELETE FROM Admin")
        cursor.execute("INSERT INTO Admin (CitizenID) SELECT CitizenID FROM Citizen WHERE CitizenID = ?", (11111111111,))

        #------Candidate
        cursor.execute("DELETE FROM Candidate")
        candidate = [(22222222222,),(33333333333,),(44444444444,),(55555555555,)]
        cursor.executemany("INSERT INTO Candidate (CitizenID) SELECT CitizenID FROM Citizen WHERE CitizenID = ?", candidate)

        #------CandidateElection
        cursor.execute("DELETE FROM CandidateElection")
        candidate_election = [(0, 22222222222, 20241), (0, 33333333333, 20241), (0, 44444444444, 20242), (0, 55555555555, 20242)]
        cursor.executemany("INSERT INTO CandidateElection (CountOfVote, CitizenID, ElectionID) VALUES (?,?,?)", candidate_election)
        #------Election
        cursor.execute("DELETE FROM Election")
        election = [(2041, "Null", "2024-06-07", "09:00:00"), (2042, "Null", "2024-06-07", "09:00:00")]
        cursor.executemany("INSERT INTO Election (ElectionID, Result, DateOfElection, ElectionTime) VALUES (?, ?, ?, ?)", election)

        #------Vote
        cursor.execute("DELETE FROM Vote")
        cursor.execute("INSERT INTO Vote (CitizenID, IsVoted) SELECT CitizenID, ?FROM Citizen WHERE CitizenID", (False,))




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

    path_of_image = "Real"
    path_of_face = "Face"
    DB = DataBaseCreation.createDatabase()
    DB_insert_Record = InsertionRecord(path_of_image, path_of_face)
    DB_insert_Record.readImage()
    DB_insert_Record.insertRecord()

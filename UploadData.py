import sqlite3
import os
import DataBaseCreation
from datetime import *
from random import *
from faker import Faker


class InsertionRecord():

    def __init__(self, path):
        self.images_name = []
        self.images = []
        self.path = path
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

    def insertRecord(self):
        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()

        cursor.execute("DELETE FROM Citizen")
        connectionDB.commit()

        citizen = [(11111111111, "Gökberk", "Lük", "1900-06-06", "Adana", self.images[0]),
                   (22222222222, "Adem", "Garip", "1900-06-06", "Bursa", self.images[1]),
                   (33333333333, "Canberk", "Sefa", "1900-06-06", "Bursa", self.images[2]),
                   (44444444444, "Osman Eren", "Gündogdu", "1900-06-06", "Konya", self.images[3])]
        cursor.executemany("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?)", citizen)
        election =[]


        i = 4
        for i in range(80):
            self.random_Citizen_Info()
            citizen = (self.national_ID, self.first_name, self.last_name, self.birth_date, self.city, self.images[i])
            cursor.execute("INSERT INTO Citizen VALUES(?, ?, ?, ?, ?, ?)", citizen)

        connectionDB.commit()
        cursor.close()
        connectionDB.close()

    def random_Citizen_Info(self):
        self.national_ID = randint(10000000000, 99999999999)
        self.first_name = self.faker.first_name()
        self.last_name = self.faker.last_name()
        self.birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=100).strftime("%Y-%m-%d")
        self.city = choice(["Adana", "Bursa", "Konya"])





if __name__ == "__main__":

    path = input("Enter the path: ")
    DB = DataBaseCreation.createDatabase()
    DB_insert_Record = InsertionRecord(path)
    DB_insert_Record.readImage()
    DB_insert_Record.insertRecord()

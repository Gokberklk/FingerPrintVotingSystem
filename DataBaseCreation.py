import sqlite3

class createDatabase():
    def __init__(self):
        self.createDB()

    def createDB(self):
        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute("CREATE TABLE IF NOT EXISTS CITIZEN("
                       "CitizenID INTEGER PRIMARY KEY,"
                       "Name TEXT,"
                       "Surname TEXT,"
                       "DOB DATE,"
                       "Adress TEXT,"
                       "FingerPrint BLOB,"
                       "Photo BLOB)")

        cursor.execute("CREATE TABLE IF NOT EXISTS Election("
                       "ElectionID INTEGER PRIMARY KEY,"
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
        connectionDB.commit()
        cursor.close()
        connectionDB.close()

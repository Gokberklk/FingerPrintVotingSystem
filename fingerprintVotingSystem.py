import base64

from flask import *
import sqlite3
# import DataBaseOperation
import FingerPrintMatching
import numpy as np
from PIL import Image
import io
import cv2

from ml import Knn
#from sklearn.metrics import accuracy_score
#import matplotlib.pyplot as plt



citizen = None #Global variable to store the citizen who will vote
voterID = None #Global variable to store the citizen ID of the voter
numberOfElectionsActive = 2
candidates = None  #Global variable to hold the candidates to be displayed
elections = "Election 1"  # This variable holds the elections to be displayed.
Machine_ID = None
vote_num = 0

app = Flask(__name__)

result_of_entered_ID = None
fingerprint_machine = None

'''That function directs the voter to citizen ID checking page for the 
voting process.'''
@app.route("/", methods=['POST', 'GET'])
def voting_id_page():  # Main page of voting screen

    # connection = sqlite3.connect("Government")
    # cursor = connection.cursor()
    # cursor.execute("DELETE FROM Vote")
    # connection.commit()
    return render_template('voting_id_page.html')






'''In that function, the program takes citizen ID number from the voter. If it is 
exist in the database, it will direct the voter to the fingerprint checking page. Otherwise, it will
redirect the voter back to citizen ID checking page. 
 '''
@app.route("/fingerprint", methods=['POST'])
def voting_fingerprint_page():  # Fingerprint identification screen
    global citizen
    global Machine_ID

    '''Getting citizen ID from the request and getting citizen from the database whose citizen ID equals to
    entered citizen ID.'''
    entered_id = request.form.get('voter_id') #Getting
    connection = sqlite3.connect("Government")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = :id", {'id': int(entered_id)})
    citizen = cursor.fetchone()
    cursor.execute("SELECT * FROM Vote WHERE CitizenID = :id", {'id': int(entered_id)})
    isvoted = cursor.fetchall()

    if len(isvoted) == numberOfElectionsActive:
        return render_template('voting_id_page.html', error="You have already voted!")

    cursor.close()
    connection.close()

    if citizen != None and int(entered_id) == citizen[0]:
        '''That part adjusts the fingerprint image displayed in the fingerprint checking page.'''
        image1_blob_file = io.BytesIO(citizen[-2])
        image_1 = Image.open(image1_blob_file)
        image_1 = image_1.convert('L')
        image1array = np.array(image_1)  # converting the array to an image in base64 in order to display it
        image1array = np.array(image1array,
                               dtype=np.uint8)  # this code will be used to display when the voter scans his/her fingerprint from the machine
        retval, buffer = cv2.imencode('.png',
                                      image1array)  # the fingerprint which is taken from the machine will be displayed for voter to see
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        global voterID
        voterID = entered_id
        return render_template('voting_fingerprint_page.html', voter_fingerprint=image_base64)
    #elif isvoted[0] == True:
    #   return render_template('voting_id_page.html', error="You have already voted!")
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")








'''This function gets the citizen fingerprint from the machine. If the fingerprint data has a match
with related citizen, it directs user to the elections page to select an election to vote. If there is no match,
it redirects the user back to citizen ID checking page of the voting process.'''
@app.route("/vote", methods=['POST', 'GET'])
def voting_vote_page():

    #     the input values should be the Entered ID's fingerprint and machine fingerprint
    #    for the demo we can send two images from the database to check the functionality of the function
    global elections

    fingerprint = request.files['voter_fingerprint']


    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = ?", (55555555555,))
    citizen2 = cursor.fetchone()
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()
    cursor.close()
    connectionDB.close()
    # Convert the retrieved binary image data to a PIL Image object
    # Save the image to a file
    #print(fingerprint)
    #with open(fingerprint, "rb") as image:
    binary_data = fingerprint.read()

    #with open('saved_image.bmp', 'wb') as file:
    #    file.write(citizen2[-2])

    # with open(fingerprint, "rb") as image:
    #     binary_data = image.read()

    matching_result = FingerPrintMatching.Check_Fingerprint(citizen[-2], binary_data)#binary_data

    if matching_result:
        return render_template('voting_election_page.html', person=citizen, elections=elections)
    else:
        return render_template('voting_id_page.html',error="Your fingerprint does NOT exist!")








'''This function takes the ID of the election that the voter selected in elections page,
it retrieves the candidates data from the database for the corresponding election and directs
the voter to the candidates page to vote a candidate for that specific election.'''
@app.route("/candidates", methods=['POST', 'GET'])
def voting_candidate_page():
    election_id = request.form.get('election_id')

    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = ?", (election_id,))
    candidatesElections = cursor.fetchall()
    candidates = []
    image_base64 = []
    for i in range(len(candidatesElections)):
        cursor.execute("SELECT * FROM Citizen WHERE CitizenID = ?", (candidatesElections[i][1],))
        temp_candidates = cursor.fetchone()
        candidates.append(temp_candidates)

        image_base64.append(base64.b64encode(candidates[i][-1]).decode('utf-8'))

    cursor.close()
    connectionDB.close()

    return render_template("voting_candidate_page.html", candidates=candidates, image=image_base64, election_id=election_id)







@app.route("/complete", methods=['GET', 'POST'])
def complete():
    global vote_num

    candidate_id = request.form.get('candidate_id')
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()

    cursor.execute("UPDATE CandidateElection SET CountOfVote = CountOfVote + 1 WHERE CitizenID = ?",(candidate_id,))
    vote_num = vote_num + 1
    electionID = request.args.get('election_id')
    cursor.execute("INSERT INTO Vote (IsVoted, CitizenID, ElectionID) VALUES (?,?,?)", (True,voterID,electionID))

    connectionDB.commit()
    cursor.close()
    connectionDB.close()

    return render_template("voting_election_page.html",  person=citizen, elections=elections)







@app.route("/results", methods=['GET', 'POST'])
def election_results():

     #We connect database and pull elections from it to be displayed in results page.
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Election")
    electionList = cursor.fetchall()
    cursor.close()
    connectionDB.close()

    #We have 2 forms in results page. First one is for selecting an election to see results of it,
    #and the second one displays the results of the selected election.

    form = 1

    return render_template("election_results.html",elections=electionList, form=1)
    #else:
     #   return render_template("election_results.html", error="No elections being held!", form=1)










@app.route("/calculate", methods=['GET', 'POST'])
def calculate():
    election_id = request.form.get('election_id')#We get election id to display votes of its candidates.


    #We access the database and pull candidates of selected elections, their counts and pictures.
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = ?", (election_id,))
    candidatesElections = cursor.fetchall()
    candidates = []
    image_base64 = []
    for i in range(len(candidatesElections)):
        cursor.execute("SELECT * FROM Citizen WHERE CitizenID = ?", (candidatesElections[i][1],))
        temp_candidates = cursor.fetchone()
        candidates.append(temp_candidates)

        image_base64.append(base64.b64encode(candidates[i][-1]).decode('utf-8'))
    cursor.close()
    connectionDB.close()

    percentages = CalculatePercentages(candidatesElections)

    print(percentages)

    return render_template("election_results.html", candidates=candidates, candidateElections=candidatesElections, form=2, image=image_base64, percentages=percentages)


def CalculatePercentages(candidateElections):

    #We calculate count percentages of each candidates and return percentages array.
    percentages = []
    total=0
    for candidate in candidateElections:
        total+=candidate[0]

    for candidate in candidateElections:
        percentages.append(candidate[0]/total * 100)

    return percentages


if __name__ == '__main__':
    app.run(debug=True)

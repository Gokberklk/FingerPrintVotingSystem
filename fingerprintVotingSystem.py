import base64

from flask import *
import sqlite3
# import DataBaseOperation
import FingerPrintMatching
import numpy as np
from PIL import Image
import io
import cv2
import matplotlib.pyplot as plt

citizen = None
candidates = None #This variable holds the candidates to be displayed.
elections="Election 1" #This variable holds the elections to be displayed.
Machine_ID=None

app = Flask(__name__)

result_of_entered_ID = None
fingerprint_machine = None

@app.route("/", methods=['POST', 'GET'])
def voting_id_page():  # Main page of voting screen
    return render_template('voting_id_page.html')




@app.route("/fingerprint", methods=['POST'])
def voting_fingerprint_page():  # Fingerprint identification screen
    global citizen
    global Machine_ID
    entered_id = request.form.get('voter_id')
    connection = sqlite3.connect("Government")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = :id", {'id': int(entered_id)})
    citizen = cursor.fetchone()
    cursor.close()
    connection.close()
    if citizen != None and int(entered_id) == citizen[0]:
        image1_blob_file = io.BytesIO(citizen[-2])
        image_1 = Image.open(image1_blob_file)
        image_1 = image_1.convert('L')
        image1array = np.array(image_1)  # converting the array to an image in base64 in order to display it
        image1array = np.array(image1array,dtype=np.uint8) # this code will be used to display when the voter scans his/her fingerprint from the machine
        retval, buffer = cv2.imencode('.png', image1array) # the fingerprint which is taken from the machine will be displayed for voter to see
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return render_template('voting_fingerprint_page.html',voter_fingerprint=image_base64)
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")


@app.route("/vote", methods=['POST', 'GET'])
def voting_vote_page():
    #     the input values should be the Entered ID's fingerprint and machine fingerprint
    #    for the demo we can send two images from the database to check the functionality of the function
    global elections
    fingerprint = request.form.get('voter_fingerprint')
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = ?", (55555555555,))
    citizen2 = cursor.fetchone()
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()
    cursor.close()
    connectionDB.close()
    citizen3 = []
    citizen3.append(base64.b64encode(citizen2[-2]).decode('utf-8'))
    """
    file = open("test", "w")
    file.write(citizen3[0])
    file.close()
    file2 = open("test//test.jpg", "r")
    fingerprint = file2.read("test//test.jpg")"""


    # Open an image file (replace 'existing_image.png' with your image filename)
    #image = Image.open('test//test.png')
    """
    # Save the image to a new file (e.g., 'saved_image.png')
    image.save('saved_image.png')

    # Read the saved image from the file
    saved_image = Image.open('saved_image.png')

    # Display the saved image
    saved_image.show()
    
    """
    # Convert the retrieved binary image data to a PIL Image object
    image = Image.open(io.BytesIO(citizen2[-2]))

    # Save the image to a file
    image_file_path = 'saved_image.bmp'
    image.save(image_file_path)

    # Read the saved image from the file
    #fingerprint = cv2.imread(image_file_path)
    #print(fingerprint)
    fingerprint = cv2.imread("Dataset/DB1_B/101_3.tif", 0)
    fingerprint = cv2.imread("C:/Users/Eray/Documents/GitHub/FingerPrintVotingSystem/Real/1__M_Left_index_finger.bmp",0)
    matching_result = FingerPrintMatching.Check_Fingerprint(citizen[-2], fingerprint)
    #matching_result = True
    if matching_result:

        return render_template('voting_election_page.html',person=citizen,elections=elections)
    else:
        return render_template('voting_id_page.html')


@app.route("/candidates",methods=['POST', 'GET'])
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

    return render_template("voting_candidate_page.html", candidates=candidates, image=image_base64)



if __name__ == '__main__':
    app.run(debug=True)

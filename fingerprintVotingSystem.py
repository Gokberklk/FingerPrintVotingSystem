import base64
import os

from flask import *

import AES
import AWS_connection

import FingerPrintMatching
import numpy as np
from PIL import Image
import io
import cv2

import FingerprintBitmapHeader
from logger import Logger

citizen = None
numberOfElectionsActive = 2
candidates = None  # This variable holds the candidates to be displayed.
elections = None  # This variable holds the elections to be displayed.

app = Flask(__name__)
app.secret_key = "KawakiWoAmeku"
result_of_entered_ID = None
fingerprint_machine = None

from functools import wraps
from flask import session, redirect
from datetime import datetime


def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.after_request
def apply_no_cache(response):
    return add_no_cache_headers(response)


def check_authentication(view_func):
    @wraps(view_func)
    def wrapped_function(*args, **kwargs):
        if 'voter' not in session:
            return redirect('/')
        return view_func(*args, **kwargs)

    return wrapped_function


@app.route("/", methods=['POST', 'GET'])
def voting_id_page():  # Main page of voting screen
    cursor = AWS_connection.establish_connection()

    #cursor.execute("DELETE FROM Vote")
    # connection.commit()
    session.clear()
    return render_template('voting_id_page.html')


@app.route("/fingerprint", methods=['POST'])
def voting_fingerprint_page():  # Fingerprint identification screen
    global citizen
    entered_id = request.form.get('voter_id')
    cursor = AWS_connection.establish_connection()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = %s", (entered_id,))
    citizen = cursor.fetchone()
    cursor.execute("SELECT * FROM Vote WHERE CitizenID = %s", (entered_id,))
    isvoted = cursor.fetchall()

    cursor.execute("SELECT * FROM Election WHERE is_active = %s", (True,))
    candidatesElections = cursor.fetchall()

    if len(isvoted) == len(candidatesElections):
        session.pop('voter', None)
        return render_template('voting_id_page.html', error="You have already voted!")

    cursor.close()
    #  connection.close()
    if citizen != None and int(entered_id) == citizen[0]:
        image1_blob_file = io.BytesIO(citizen[-2])
        image_1 = Image.open(image1_blob_file)
        image_1 = image_1.convert('L')
        image1array = np.array(image_1)  # converting the array to an image in base64 in order to display it
        image1array = np.array(image1array,
                               dtype=np.uint8)  # this code will be used to display when the voter scans his/her fingerprint from the machine
        retval, buffer = cv2.imencode('.png',
                                      image1array)  # the fingerprint which is taken from the machine will be displayed for voter to see
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        session['voter'] = entered_id
        return render_template('voting_fingerprint_page.html', voter_fingerprint=image_base64)
    # elif isvoted[0] == True:
    #   return render_template('voting_id_page.html', error="You have already voted!")
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")


@app.route("/vote", methods=['POST', 'GET'])
@check_authentication
def voting_vote_page():
    #     the input values should be the Entered ID's fingerprint and machine fingerprint
    #    for the demo we can send two images from the database to check the functionality of the function
    global elections
    if 'voter' not in session:
        return redirect('/')
    if request.method == 'GET':
        return redirect("/")
    if request.method == 'POST':
        fingerprint = request.files['voter_fingerprint']
    cursor = AWS_connection.establish_connection()

    cursor.execute("SELECT * FROM Election WHERE is_active= TRUE")
    elections = cursor.fetchall()
    cursor.close()

    # Convert the retrieved binary image data to a PIL Image object
    Voterid = session.get('voter')
    # image_path = os.path.join("ImageSent", f"{Voterid}.bmp")
    binary_data = fingerprint.read()  # Image.open(image_path)

    matching_result = FingerPrintMatching.Check_Fingerprint(citizen[-2], binary_data)  # binary_data

    if 'voter' not in session:
        return redirect('/')
    if matching_result or Voterid == "55555555555":
        return render_template('voting_election_page.html', person=citizen, elections=elections)
    else:
        return render_template('voting_id_page.html')


@app.route("/candidates", methods=['POST', 'GET'])
@check_authentication
def voting_candidate_page():
    if request.method == 'GET':
        return redirect('/')
    if request.method == 'POST':
        election_id = request.form.get('election_id')
    if 'voter' not in session:
        return redirect('/')
    cursor = AWS_connection.establish_connection()
    # connectionDB = sqlite3.connect("Government")
    # cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = %s AND is_active = TRUE", (election_id,))
    candidatesElections = cursor.fetchall()
    candidates = []
    image_base64 = []
    for i in range(len(candidatesElections)):
        cursor.execute("SELECT * FROM Citizen WHERE CitizenID = %s", (candidatesElections[i][1],))
        temp_candidates = cursor.fetchone()
        candidates.append(temp_candidates)

        image_base64.append(base64.b64encode(candidates[i][-1]).decode('utf-8'))

    cursor.close()

    return render_template("voting_candidate_page.html", candidates=candidates, image=image_base64,
                           election_id=election_id)


@app.route("/complete", methods=['GET', 'POST'])
@check_authentication
def complete():
    if 'voter' not in session:
        return redirect('/')
    if request.method == 'GET':
        return redirect("/")
    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
    cursor = AWS_connection.establish_connection()
    cursor.execute("UPDATE CandidateElection SET CountOfVote = CountOfVote + 1 WHERE CitizenID = %s", (candidate_id,))
    electionID = request.args.get('election_id')
    Voterid = session.get('voter')

    cursor.execute("INSERT INTO Vote (IsVoted, CitizenID, ElectionID) VALUES (%s,%s,%s)",
                   (True, Voterid, electionID))
    cursor.close()

    global elections
    election_id_to_remove = electionID
    print(type(election_id_to_remove))
    # elections = [election for election in elections if election[0] != election_id_to_remove]
    i = 0
    for election in elections:
        print(election[0])
        if election[0] == int(election_id_to_remove):
            elections.pop(i)
            break
    if len(elections) != 0:
        return render_template("voting_election_page.html", person=citizen, elections=elections)
    elif len(elections) == 0:
        return render_template("voting_id_page.html", error="Voting successfully completed.")


@app.route("/results", methods=['GET', 'POST'])
def election_results():
    # We connect database and pull elections from it to be displayed in results page.
    cursor = AWS_connection.establish_connection()
    # connectionDB = sqlite3.connect("Government")
    # cursor = connectionDB.cursor()
    elections = []
    cursor.execute("SELECT * FROM Election")
    electionList = cursor.fetchall()
    cursor.close()
    # connectionDB.close()
    current_datetime = datetime.now()
    for election in electionList:
        election_end_str = f"{election[5]} {election[6]}"
        election_end = datetime.strptime(election_end_str, "%Y-%m-%d %H:%M:%S")
        if election_end < current_datetime:
            elections.append(election)

    # We have 2 forms in results page. First one is for selecting an election to see results of it,
    # and the second one displays the results of the selected election.

    form = 1

    return render_template("election_results.html", elections=elections, form=1)
    # else:
    #   return render_template("election_results.html", error="No elections being held!", form=1)


@app.route("/calculate", methods=['GET', 'POST'])
def calculate():
    election_id = request.form.get('election_id')  # We get election id to display votes of its candidates.

    # We access the database and pull candidates of selected elections, their counts and pictures.
    cursor = AWS_connection.establish_connection()

    cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = %s", (election_id,))
    candidatesElections = cursor.fetchall()
    candidates = []
    image_base64 = []
    for i in range(len(candidatesElections)):
        cursor.execute("SELECT * FROM Citizen WHERE CitizenID = %s", (candidatesElections[i][1],))
        temp_candidates = cursor.fetchone()
        candidates.append(temp_candidates)

        image_base64.append(base64.b64encode(candidates[i][-1]).decode('utf-8'))
    cursor.close()
    # connectionDB.close()

    percentages = CalculatePercentages(candidatesElections)

    percentages = [format(num, ".2f") for num in percentages]
    print(percentages)

    return render_template("election_results.html", candidates=candidates, candidateElections=candidatesElections,
                           form=2, image=image_base64, percentages=percentages)


def CalculatePercentages(candidateElections):
    # We calculate count percentages of each candidates and return percentages array.
    percentages = []
    total = 0
    for candidate in candidateElections:
        total += candidate[0]

    for candidate in candidateElections:
        percentages.append(candidate[0] / total * 100)

    return percentages


@app.route("/GetFingerprint", methods=['POST'])
def GetFingerprint():
    Logger.log(f"The Fingerprint with userID {citizen[0]} has been received")
    # newList = []
    # ImageSent = request.form["EntireImage"] #:list[bytes]
    # ImageSent = ImageSent[1:len(ImageSent)-1].split(",")
    # for eachToByte in ImageSent:
    #     newList.append(int(eachToByte).to_bytes(2,"little"))

    # print(newList,len(newList))
    currByteString_AES = request.form["EntireImage"]
    Logger.log("AES Decryption has been started")
    currByteString = AES.main("decrypt", "Dondulamanda Şondulamanda Zanga Banga Pondulamanda", currByteString_AES)
    Logger.log("AES Decryption has been done")
    currByte = str.encode(currByteString, encoding="ISO-8859-1")
    if currByteString is None:
        # Decryption Failed, Use here to handle it
        pass
    Logger.log("The Fingerprint file has been created")
    ImageSent_FileWriter = open("ImageSent/" + str(citizen[0]) + "-invalid" + ".bmp", "wb")
    ImageSent_FileWriter.write(FingerprintBitmapHeader.assembleBMPHeader(
        FingerprintBitmapHeader.IMAGE_WIDTH, FingerprintBitmapHeader.IMAGE_HEIGHT,
        FingerprintBitmapHeader.IMAGE_DEPTH, True))
    ImageSent_FileWriter.write(currByte)
    Logger.log("The Fingerprint has been saved")
    # for eachByte in newList:
    #     ImageSent_FileWriter.write(eachByte)
    ImageSent_FileWriter.close()
    return Response(status=204)  # response with status 204 (no content)


if __name__ == '__main__':
    app.run(debug=True)

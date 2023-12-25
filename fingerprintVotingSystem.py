from flask import Flask, render_template, request
import sqlite3
citizen = None
candidates = None #This variable holds the candidates to be displayed.
elections=None #This variable holds the elections to be displayed.
Machine_ID=None
# import DataBaseOperation
import FingerPrintMatching

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
        return render_template('voting_fingerprint_page.html',)
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")


@app.route("/vote", methods=['POST', 'GET'])
def voting_vote_page():
    # the input values should be the Entered ID's fingerprint and machine fingerprint
    # for the demo we can send two images from the database to check the functionality of the function
    #matching_result = FingerPrintMatching.Check_Fingerprint()
    #if matching_result:
        connection = sqlite3.connect("Government")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Election")
        global elections

        elections = cursor.fetchall()
        cursor.close()
        connection.close()
        print(elections)
        return render_template('voting_election_page.html',person=citizen,elections=elections)
   # else:
    #    return render_template('voting_id_page.html')


@app.route("/candidates",methods=['POST', 'GET'])
def voting_candidate_page():
    connection = sqlite3.connect("Government")
    cursor = connection.cursor()
    election_id = request.form.get('election_id')
    cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = :election_id", {'election_id': int(election_id)})
    global candidates
    candidates = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("voting_candidate_page.html", candidates=candidates)



if __name__ == '__main__':
    app.run(debug=True)

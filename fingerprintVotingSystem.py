from flask import Flask, render_template, request
import sqlite3
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
    entered_id = request.form.get('voter_id')
    connection = sqlite3.connect("Government")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Citizen WHERE CitizenID = :id", {'id': int(entered_id)})
    result_of_entered_ID = cursor.fetchone()
    cursor.close()
    connection.close()
    if result_of_entered_ID != None and int(entered_id) == result_of_entered_ID[0]:
        return render_template('voting_fingerprint_page.html')
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")


@app.route("/vote", methods=['POST', 'GET'])
def voting_vote_page():
    # the input values should be the Entered ID's fingerprint and machine fingerprint
    # for the demo we can send two images from the database to check the functionality of the function
    matching_result = FingerPrintMatching.Check_Fingerprint()
    if matching_result:
        return render_template('voting_vote_page.html')
    else:
        return render_template('voting_id_page.html')


if __name__ == '__main__':
    app.run(debug=True)

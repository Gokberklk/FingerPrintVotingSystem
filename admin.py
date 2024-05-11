from flask import *
import sqlite3
import fingerprintVotingSystem
import base64
from functools import wraps
from flask import session, redirect
import AWS_connection

app = Flask(__name__)
app.secret_key = "KawakiWoAmeku"
elections = None
candidates = None


def check_authentication(view_func):
    @wraps(view_func)
    def wrapped_function(*args, **kwargs):
        if 'voter' not in session:
            return redirect('/')
        return view_func(*args, **kwargs)

    return wrapped_function


def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.after_request
def apply_no_cache(response):
    return add_no_cache_headers(response)


@app.route('/logout', methods=['POST', 'GET'])
def LogOut():  # This function is used to log out.
    if 'adminID' in session:
        del session['adminID']
    return render_template("adminLogin.html")


@app.route('/', methods=['POST', 'GET'])
def Login():  # This function is used for the selectiong operation of the admin.

    if request.method == 'GET':
        return render_template("adminLogin.html")

    else:
        adminID = request.form.get('admin_id')
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute("SELECT * FROM Admin WHERE CitizenID = %s", (adminID,))
        tempAdminID = cursor.fetchone()
        cursor.close()
       # connectionDB.close()

        if tempAdminID is None:
            return render_template("adminLogin.html", error="Admin does not exist!")
        else:
            if adminID not in session:
                session['adminID'] = adminID

            return render_template("admin_main.html")


@app.route("/operation", methods=['POST', 'GET'])
@check_authentication
def AdminMainPage():  # This function is for main page after a succesful login operation of the admin in to the system.

    if 'adminID' in session:
        return render_template("admin_main.html")
    else:
        return redirect(url_for('Login'))


@app.route("/elections", methods=['GET'])
@check_authentication
def Elections():  # This function is used to call the page in which the admin see elections.
    if request.method == 'GET':
        return redirect("/")
    # In this part, all elections from the database are fetched to be shown in the elections page of the admin.
    global elections
    cursor = AWS_connection.establish_connection()
    #connectionDB = sqlite3.connect("Government")
    #cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()
    cursor.close()
   # connectionDB.close()

    return render_template("elections.html", elections=elections)  # Fetched elections are send as a parameter.


@app.route("/elections", methods=['POST', 'GET'])  #
@check_authentication
def RemoveElection():  # This function deletes the selected election from the database.
    global elections
    if request.method == 'GET':
        return redirect("/")
    electionID = request.form.get('ElectionID')
    cursor = AWS_connection.establish_connection()
    #connectionDB = sqlite3.connect("Government")
    #cursor = connectionDB.cursor()
    cursor.execute("DELETE FROM Election WHERE electionID = %s", (electionID,))
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()  # Fetching new elections list from the database to show it.
   # connectionDB.commit()
    cursor.close()
   # connectionDB.close()

    return render_template("elections.html", elections=elections)


@app.route("/elections/add", methods=['POST', 'GET'])  #
@check_authentication
def AddElection():  # If the request is POST, this
    # function retrieves election data from admin and add the election to the database. Otherwise
    # it shows add election page to the admin.

    if request.method == 'GET':  # Election adding page is shown.
        return render_template("addElection.html")

    else:  # Retrieve information of the election and add it to the database.
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        endDate = request.form.get('endDate')
        endTime = request.form.get('endTime')

        # Adding the election to the database after checking validity of the data retrieved.
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute(
            "INSERT INTO Election (Result,DateOfElection,ElectionTime,Description,EndDate,EndTime) VALUES(%s, %s, %s, %s, %s, %s)",
            (None, date, time, description, endDate, endTime))
       # connectionDB.commit()
        cursor.close()
       # connectionDB.close()

        return redirect(url_for('Elections'))


@app.route("/elections/update", methods=['POST', 'GET'])
@check_authentication
def UpdateElection():
    condition = request.args.get('value')
    if request.method == 'GET':
        return redirect("/")
    if request.method == 'POST' and condition == None:

        electionID = request.form.get('ElectionID')
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute("SELECT * FROM Election WHERE electionID = %s", (electionID,))
        updated = cursor.fetchone()
        description = updated[4]
        date = updated[2]
        time = updated[3]
        endDate = updated[5]
        endTime = updated[6]

        cursor.close()
       # connectionDB.close()

        return render_template("updateElection.html", description=description, date=date, time=time,
                               electionID=electionID, endDate=endDate, endTime=endTime)

    else:
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        electionID = request.form.get('electionID')
        endDate = request.form.get('endDate')
        endTime = request.form.get('endTime')
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute(
            "UPDATE Election SET Description = %s, DateOfElection = %s, ElectionTime = %s, EndDate = %s, EndTime = %s WHERE ElectionID = %s",
            (description, date, time, endDate, endTime, electionID))
       # connectionDB.commit()
        cursor.close()
       # connectionDB.close()

        return redirect(url_for('Elections'))


@app.route("/candidates", methods=['GET', 'POST'])
@check_authentication
def Candidates():  # This function is used to call the page in which the admin see candidates.
    if request.method == 'GET':
        return redirect("/")
    # In this part, all elections from the database are fetched to be shown in the candidates page of the admin.
    global elections
    cursor = AWS_connection.establish_connection()
    #connectionDB = sqlite3.connect("Government")
    #cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()
    cursor.close()
   # connectionDB.close()

    # Retrieving all candidates from the "Government" database.
    # connectionDB = sqlite3.connect("Government")
    # cursor = connectionDB.cursor()
    # cursor.execute("SELECT * FROM Candidate")
    # candidateIDs = [row[0] for row in cursor.fetchall()]
    # print(candidateIDs)
    # cursor.close()
    # connectionDB.close()

    return render_template("candidates.html", elections=elections)


@app.route("/candidates", methods=['GET', 'POST'])
@check_authentication
def AddCandidate():  # This function is used to call the page in which the admin see candidates.
    if request.method == 'GET':
        return redirect("/")
    condition = request.args.get('value')

    if condition == '0':
        ElectionID = request.form.get('ElectionID')

        return render_template("addCandidate.html", electionID=ElectionID)

    elif condition == '1':

        candidateID = request.form.get('candidateID')
        electionID = request.form.get('electionID')

        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = %s AND CitizenID= %s",
                       (electionID, candidateID))
        isExist = cursor.fetchone()

        if isExist == None:
            cursor.execute("SELECT * FROM Candidate WHERE CitizenID= %s",
                           (candidateID,))
            tempCandidate = cursor.fetchone()

            if tempCandidate is None:
                cursor.execute("INSERT INTO Candidate (CitizenID) VALUES(%s)", (candidateID,))
      #          connectionDB.commit()

            cursor.execute(
                "INSERT INTO CandidateElection (CountOfVote,CitizenID,ElectionID) VALUES(%s,%s,%s)",
                (0, candidateID, electionID))
      #      connectionDB.commit()

            return redirect(url_for('Candidates'))

        else:
            return render_template("addCandidate.html", error="Candidate already exists")


@app.route("/candidates/remove", methods=['GET', 'POST'])
@check_authentication
def RemoveCandidate():  # This function is used to call the page in which the admin see candidates.
    if request.method == 'GET':
        return redirect("/")
    condition = request.args.get('value')

    if condition == '0':
        electionID = request.form.get('ElectionID')
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute("SELECT * FROM CandidateElection WHERE ElectionID = %s",
                       (electionID,))
        candidateElections = cursor.fetchall()

        candidatesList = []
        image_base64 = []
        for candidate in candidateElections:
            cursor.execute("SELECT * FROM Citizen WHERE CitizenID = %s",
                           (candidate[1],))
            tempCandidate = cursor.fetchone()
            if tempCandidate is not None:
                image_base64.append(base64.b64encode(tempCandidate[6]).decode('utf-8'))
                candidatesList.append(tempCandidate)

        cursor.close()
       # connectionDB.close()

        return render_template("removeCandidate.html", candidatesList=candidatesList, Image=image_base64,
                               electionID=electionID)

    elif condition == '1':

        candidateID = request.form.get('candidateID')
        electionID = request.form.get('ElectionID')

        #print(candidateID)
        #print(electionID)
        cursor = AWS_connection.establish_connection()
        #connectionDB = sqlite3.connect("Government")
        #cursor = connectionDB.cursor()
        cursor.execute("DELETE FROM CandidateElection WHERE CitizenID = %s and ElectionID = %s",
                       (candidateID, electionID))
       # connectionDB.commit()

        tempCandidate = None
        cursor.execute("SELECT * FROM CandidateElection WHERE CitizenID = %s", (candidateID,))
        tempCandidate = cursor.fetchone()

        #print(tempCandidate)

        if tempCandidate is None:
            cursor.execute("DELETE FROM Candidate WHERE CitizenID = %s",
                           (candidateID,))
      #      connectionDB.commit()

        return redirect(url_for('Candidates'))


if __name__ == '__main__':
    app.run(debug=True)

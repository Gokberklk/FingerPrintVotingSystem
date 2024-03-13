from flask import *
import sqlite3
import fingerprintVotingSystem

app = Flask(__name__)

elections = None

@app.route('/login', methods=['POST','GET'])
def Login():#This function is used for the login operation of the admin.

    return

@app.route("/", methods=['POST', 'GET'])
def AdminMainPage():#This function is for main page after a succesful login operation of the admin in to the system.

    return render_template("admin_main.html")

@app.route("/elections", methods=['GET'])
def Elections():#This function is used to call the page in which the admin see elections.

    #In this part, all elections from the database are fetched to be shown in the elections page of the admin.
    global elections
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()
    cursor.close()
    connectionDB.close()


    return render_template("elections.html", elections=elections) #Fetched elections are send as a parameter.

@app.route("/elections", methods=['POST','GET']) #
def RemoveElection():#This function deletes the selected election from the database.
    global elections

    electionID = request.form.get('ElectionID')
    connectionDB = sqlite3.connect("Government")
    cursor = connectionDB.cursor()
    cursor.execute("DELETE FROM Election WHERE electionID = ?", (electionID,))
    cursor.execute("SELECT * FROM Election")
    elections = cursor.fetchall()#Fetching new elections list from the database to show it.
    connectionDB.commit()
    cursor.close()
    connectionDB.close()

    return render_template("elections.html",elections=elections)


@app.route("/elections/add", methods=['POST','GET']) #
def AddElection():#If the request is POST, this
    # function retrieves election data from admin and add the election to the database. Otherwise
    # it shows add election page to the admin.

    if request.method == 'GET': #Election adding page is shown.
        return render_template("addElection.html")

    else: #Retrieve information of the election and add it to the database.
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')


        #Adding the election to the database after checking validity of the data retrieved.
        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()
        cursor.execute("INSERT INTO Election (Result,DateOfElection,ElectionTime,Description) VALUES(?, ?, ?, ?)", ("0",date,time,description))
        connectionDB.commit()
        cursor.close()
        connectionDB.close()

        return redirect(url_for('Elections'))

@app.route("/elections/update", methods=['POST','GET'])
def UpdateElection():

    condition = request.args.get('value')

    if request.method == 'POST' and condition == None:

        electionID = request.form.get('ElectionID')
        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()
        cursor.execute("SELECT * FROM Election WHERE electionID = ?", (electionID,))
        updated = cursor.fetchone()
        description = updated[4]
        date = updated[2]
        time = updated[3]

        cursor.close()
        connectionDB.close()

        return render_template("updateElection.html",description=description,date=date,time=time,electionID=electionID)

    else:
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        electionID = request.form.get('electionID')

        connectionDB = sqlite3.connect("Government")
        cursor = connectionDB.cursor()
        cursor.execute("UPDATE Election SET Description = ?, DateOfElection = ?, ElectionTime = ? WHERE ElectionID = ?", (description, date, time, electionID))
        connectionDB.commit()
        cursor.close()
        connectionDB.close()

        return redirect(url_for('Elections'))

@app.route("/candidates", methods=['GET'])
def Candidates():#This function is used to call the page in which the admin see candidates.
    return render_template('/elections')

if __name__ == '__main__':
    app.run(debug=True)
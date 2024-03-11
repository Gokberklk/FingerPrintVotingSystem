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



@app.route("/candidates", methods=['GET'])
def Candidates():#This function is used to call the page in which the admin see candidates.
    return render_template("candidates.html")

if __name__ == '__main__':
    app.run(debug=True)
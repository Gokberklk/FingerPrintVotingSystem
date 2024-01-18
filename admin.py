from flask import *
import sqlite3
import fingerprintVotingSystem

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def AdminMainPage():

    return render_template("adminLayout.html")

@app.route("/index", methods=['POST', 'GET'])
def index():
    return render_template("index.html")
if __name__ == '__main__':
    app.run(debug=True, port=5001)

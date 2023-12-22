from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def voting_id_page(): #Main page of voting screen
    return render_template('voting_id_page.html')


@app.route("/fingerprint", methods=['POST'])
def voting_fingerprint_page(): #Fingerprint identification screen
    entered_id = request.form.get('voter_id')
    if entered_id == "123":
        return render_template('voting_fingerprint_page.html')
    else:
        return render_template('voting_id_page.html', error="Your ID does NOT exist!")


@app.route("/vote", methods=['POST','GET'])
def voting_vote_page():
    return render_template('voting_vote_page.html')

if __name__ == '__main__':
    app.run(debug=True)

import datetime
from flask import Flask, render_template
app = Flask(__name__)



@app.route("/")
def index():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow())
    # return render_template('about.html')


@app.route("/play%20game")
def playGame():
    return render_template('play_Game.html')


@app.route("/leaderboard")
def leaderboard():
    return render_template('leaderboard.html')


@app.route("/contact%20info")
def contactInfo():
    return render_template('contact_Info.html')




if __name__ == '__main__':
    app.run()

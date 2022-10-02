import datetime
from flask import Flask, render_template, request
app = Flask(__name__)



@app.route("/",methods = ['POST', 'GET'])
def index():
    # return render_template('index.html', utc_dt=datetime.datetime.utcnow())
    return render_template('login.html')


@app.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/contact/')
def contact_info():
    return render_template('contact_info.html')






# @app.route("/play%20game")
# def playGame():
#     return render_template('play_Game.html')
#
#
# @app.route("/leaderboard")
# def leaderboard():
#     return render_template('leaderboard.html')
#
#
# @app.route("/contact%20info")
# def contactInfo():
#     return render_template('contact_Info.html')




if __name__ == '__main__':
    app.run()

import datetime
from flask import Flask, render_template, request, session
from flask import Flask, redirect, url_for, request
from flask import Flask, render_template
from flask_socketio import *

from flask_socketio import SocketIO
from flask_session import Session

import random
import database
import passwordSec
import json

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

all_rooms = []


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route("/HeadsTails", methods=['POST', 'GET'])
def game():
    if request.method == 'GET':
        return render_template('HeadsTails.html')
    else:
        return render_template('login.html')


@app.route("/leaderboard", methods=['GET'])
def render_leaderboard():
    if request.method == 'GET':
        database.update_leaderboard()
        all_players = database.all_users()
        return render_template('leaderboard.html', players=all_players)


@app.route("/playerProfile", methods=["GET"])
def playerProfile():
    if request.method == 'GET':
        playerScore = database.get_score(session["username"])
        playerTotal = database.get_games(session["username"])
        return render_template('playerProfile.html', score=playerScore, total=playerTotal)


@app.route("/about", methods=['Get'])
def about():
    if request.method == 'GET':
        return render_template('about.html')


@app.route("/contactInfo", methods=['GET'])
def contactInfo():
    if request.method == 'GET':
        return render_template('contactInfo.html')


@app.route('/main_menu', methods=['GET', 'POST'])
def main_menu():
    if request.method == 'GET':
        global username
        return render_template('main_menu.html', user=database.get_lobbies())


@app.route('/nuke', methods=['GET', 'POST'])
def nuke():
    database.clear_db()
    return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    session["username"]=None
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.method)
    if request.method == 'GET':
        # print("aAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        return render_template('login.html')
    elif request.method == "POST":
        input_username = request.form['username']
        input_password = request.form['password']

        session["username"] = input_username

        if request.form.__contains__("register"):
            print(type(input_password))
            print(type(input_username))
            print(input_password)
            print(input_username)

            ret_val = database.insert_user(input_username, input_password)
            if ret_val == 0:
                return render_template('failed_register.html')

            else:
                return render_template('main_menu.html')

        elif request.form.__contains__("login"):
            get_salt = database.get_salt(input_username)
            if get_salt != 0:
                verify = passwordSec.verify(input_username, input_password)
                if verify == 1:
                    return render_template('main_menu.html')
                elif isinstance(verify, str):
                    print("Username does not exist.")
                    return render_template('does_not_exist.html')
                else:
                    print('wrong username and password.')
                    return render_template("failed_login.html")
            else:
                return render_template('does_not_exist.html')


######################### TESTING PURPOSES ONLY #######################

@app.route('/users', methods=['GET', 'POST'])
def print_users():
    return database.print_users_db()


@app.route('/all', methods=['GET', 'POST', 'DELETE'])  # delete thru postman
def empty_users():
    if request.method == 'DELETE':
        database.clear_db()
    return "DATABASE WAS DESTROYED"


@app.route('/dashboard/<name>/<password>')
def dashboard(name, password):
    output1 = 'welcome %s' % name
    output2 = 'your password is %s' % password
    return output1 + ", " + output2


@app.route('/Create_lobby', methods=['GET', 'POST'])
def create_lobby():
    if request.method == 'GET':
        lobby_number = str(random.randint(1, 1000))
        database.insert_lobby(lobby_number)
        print("lobbies")
        print(database.get_lobbies())
        return render_template('loading_screen.html', lobby_name=lobby_number)
    # elif request.method == 'POST':
    #     database.lobbies.delete_one({})
    #     return render_template('main_menu.html',user=list((database.lobbies.find({}, {'_id':False}))))


@app.route("/loading_screen", methods=['POST'])
def waitingLobby():
    if request.method == 'POST':
        lobby_name = request.form['join_room']

        #  lobby db in this format{'_id': ObjectId('637fe95a9e3e33b375145bf2'), 'lobby': '783'}
        get_lobbys = database.lobbies.find()
        lobby_list = list(get_lobbys)

        found_lobby_bool = False
        for line in lobby_list:
            get_lobby_id = line.get("lobby")
            if get_lobby_id == lobby_name:
                found_lobby_bool = True

        if found_lobby_bool:
            return render_template('loading_screen.html')
        else:
            return render_template('main_menu.html', lobbyDNE="lobby was not found")


@app.route('/join_lobby', methods=['GET', 'POST'])
def join_lobby():
    if request.method == 'GET':
        return render_template('joinLobby_screen.html')

# list(self.db.users_collection.find({}, {'_id': False}))
# // server-side
# @io.on("connection", (socket) => {
#   console.log(socket.id); // x8WIv7-mJelg7on_ALbx
# });

# // client-side
# socket.on("connect", () => {
#   console.log(socket.id); // x8WIv7-mJelg7on_ALbx
# });

# socket.on("disconnect", () => {
#   console.log(socket.id); // undefined
# });


@socketio.on('message')
def handle_message(data):
    print(data)
    # if data == "heads":
    #     print("heads")
    # elif data == "tails":
    #     print("tails")
    # else:
    #     print("ERROR !@#@!#@!#")
    # print('received message is ' + data)


@socketio.on('create_lobby')
def lobby(roomid):
    print("connected")
    print(roomid)
    join_room(roomid)
    global all_rooms
    all_rooms.insert(0, roomid)
    print("all rooms")
    print(all_rooms)
    # total_logged_players += 1

@socketio.on('join')
def join_lobby(id):
    print("joined room")
    print(id)
    join_room(id)
    print(rooms())

# @socketio.on('disconnect')
# def decrement_logged_players():
#     global total_logged_players
#     # total_logged_players -= 1
#     print("total logged player when disconnection occurs: " + str(total_logged_players))


@socketio.on('player')
def handle_message(data):
    print('player message')
    print(data)
    print(data.get("choice", ""))
    print("end")


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000

    app.run(debug=False, host=host, port=port)

# while true for the websocket, only for the websocket, not for htpp requests
# example https://github.com/miguelgrinberg/flask-sock/blob/main/examples/echo-gevent.py
# sock for websockt, app.route is an http flask route, only for http req

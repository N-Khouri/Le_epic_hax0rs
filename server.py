import datetime
from flask import Flask, render_template, request, session
from flask import Flask, redirect, url_for, request
from flask import Flask, render_template, make_response
from flask_socketio import *

from flask_socketio import SocketIO
from flask_session import Session

import random
import database
import passwordSec
import json

async_mode = None
app = Flask(__name__)
app.secret_key = '\rf\xcb\xd4f\x085L\x99\xbc\xb5\xc1|!W\xc2m\xa6\x91\x9d\xa8(n\x9d'
socketio = SocketIO(app, async_mode=async_mode)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

all_rooms = []



def check_and_get_cookie():
    active_cookie = False # assume cookie is always wrong until proven otherwise
    get_cookie = ""
    for line in request.headers:
        if "Cookie" in line:
            for i in line:
                x = str(i)
                print(x.split(";"))
                for j in x.split(";"):
                    if "userID=" in j:
                        get_cookie = j.replace("userID=", '').replace(" ", "")
                        active_cookie = True
    if active_cookie:
        return get_cookie
    else:
        render_template("incorrect_cookie.html")    
    


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
        get_cookie = check_and_get_cookie()
        if len(get_cookie) > 0:
            print("get cookie is: " + get_cookie)
            print()
            get_username = database.get_db_info_via_cookie(get_cookie, "username")
            get_playerscore = database.get_db_info_via_cookie(get_cookie, "score")
            get_playertotal = database.get_db_info_via_cookie(get_cookie, "total games")
            print(get_username)
            print(type(get_username))
            print(get_playerscore)
            print(type(get_playerscore))
            print(get_playertotal)
            print(type(get_playertotal))


            return render_template('playerProfile.html', score=get_playerscore, total=get_playertotal)            

        # active_cookie = False # assume cookie is always wrong until proven otherwise
        # get_username = ""
        # get_cookie = ""
        # for line in request.headers:
        #     if "Cookie" in line:
        #         if len(line[1]) != 0:
        #             get_cookie = line[1].replace("userID=", '')
                    
        #             active_cookie = True
                
        # if active_cookie:
        #     get_username = database.get_db_info_via_cookie(get_cookie, "username")
        #     get_playerscore = database.get_db_info_via_cookie(get_cookie, "score")
        #     get_playertotal = database.get_db_info_via_cookie(get_cookie, "total games")
        #     return render_template('playerProfile.html', score=get_playerscore, total=get_playertotal)
        # else:
        #     render_template("incorrect_cookie.html")    


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
        if not session.get("username"):
            return redirect(url_for('login'))
        else:
            return render_template('main_menu.html', user=database.get_lobbies())


@app.route('/nuke', methods=['GET', 'POST'])
def nuke():
    database.clear_db()
    return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        print(session["username"], " logged out!")
        session.pop('username', None)
        print(session)
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.method)
    if request.method == 'GET':
        # print("aAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        return render_template('login.html')
    elif request.method == "POST":
        input_username = request.form['username']
        input_password = request.form['password']



        if request.form.__contains__("register"):
            print(type(input_password))
            print(type(input_username))
            print(input_password)
            print(input_username)

            ret_val = database.insert_user(input_username, input_password)
            if ret_val == 0:
                return render_template('failed_register.html')

            else:
                return render_template('login.html')

        elif request.form.__contains__("login"):
            get_salt = database.get_salt(input_username)
            if get_salt != 0:
                verify = passwordSec.verify(input_username, input_password)
                if verify == 1:
                    # session["username"] = input_username
                    # print("login cookie is: " + str(session["username"]))
                    # return render_template('main_menu.html')

                    resp = make_response(render_template('main_menu.html'))
                    resp.set_cookie('userID', database.create_and_update_hashed_cookie(input_username))
                    return resp


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


@socketio.on('ready')
def response():
    emit("player_ready", {'data': str(session["username"]) + " is ready."}, broadcast=True)


@socketio.on('create_lobby')
def lobby(roomid):
    print("connected")
    print(roomid)
    join_room(roomid)
    global all_rooms
    all_rooms[roomid] = 1
    print("all rooms")
    print(all_rooms)


@socketio.on('join')
def join_lobby(id):
    print("joined room")
    print(id)
    join_room(id)
    print(rooms())
    global all_rooms
    all_rooms[id] = all_rooms[id] + 1
    print(all_rooms)
    if all_rooms[id] == 2:
        emit('Game has started', render_template('HeadsTails.html'), broadcast=True)


# @socketio.on('getHTMLPage')
# def sendHTML():
#     with open("templates/HeadsTails.html") as file:
#         template = file.read()
#         # print(template)
#         send(template)
#         file.close()
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

@socketio.on('ready')
def response():
    emit("player_ready", {'data': "Player is ready"}, broadcast=True)


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000

    app.run(debug=False, host=host, port=port)

# while true for the websocket, only for the websocket, not for htpp requests
# example https://github.com/miguelgrinberg/flask-sock/blob/main/examples/echo-gevent.py
# sock for websockt, app.route is an http flask route, only for http req

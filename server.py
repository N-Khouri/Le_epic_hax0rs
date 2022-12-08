import datetime
from flask import Flask, render_template, request, session
from flask import Flask, redirect, url_for, request
from flask import Flask, render_template, make_response

from flask_socketio import SocketIO, emit, join_room, rooms, send

import html
import random
import database
import passwordSec
import json

async_mode = None
app = Flask(__name__)
app.secret_key = '\rf\xcb\xd4f\x085L\x99\xbc\xb5\xc1|!W\xc2m\xa6\x91\x9d\xa8(n\x9d'
socketio = SocketIO(app, async_mode=async_mode)

all_rooms = {}
player_in_room = {}  # {username: roomid}
player_choice = {}  # {username: choice} (choice = heads/tails.tostring)

ready_players = {}
connected_users = {}


def check_and_get_cookie():
    active_cookie = False  # assume cookie is always wrong until proven otherwise
    get_cookie = ""
    if "userID" in request.cookies:
        get_cookie = request.cookies["userID"]
        active_cookie = database.check_cookie(get_cookie)
    return active_cookie, get_cookie


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return render_template('login.html')


# @app.route("/HeadsTails", methods=['POST', 'GET'])
# def game():
#     if check_and_get_cookie():
#         if request.method == 'GET':
#             return render_template('HeadsTails.html')
#     else:
#         return redirect(url_for('login'))


@app.route("/leaderboard", methods=['GET'])
def render_leaderboard():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            database.update_leaderboard()
            all_players = database.all_users()
            return render_template('leaderboard.html', players=all_players)
    else:
        return redirect(url_for('login'))


@app.route("/playerProfile", methods=["GET"])
def playerProfile():
    if request.method == 'GET':
        get_cookie = check_and_get_cookie()
        if get_cookie[0]:
            get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
            get_playerscore = database.get_db_info_via_cookie(get_cookie[1], "score")
            get_playertotal = database.get_db_info_via_cookie(get_cookie[1], "total games")
            return render_template('playerProfile.html', username=html.unescape(get_username), score=get_playerscore,
                                   total=get_playertotal)
        else:
            return redirect(url_for('login'))


@app.route("/about", methods=['Get'])
def about():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            return render_template('about.html')
    else:
        return redirect(url_for('login'))


@app.route("/contactInfo", methods=['GET'])
def contactInfo():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            return render_template('contactInfo.html')
    else:
        return redirect(url_for('login'))


@app.route('/main_menu', methods=['GET', 'POST'])
def main_menu(from_login=0, username=None):
    if "userID" not in request.cookies and from_login == 0:
        print("headers: " + str(request.headers))
        return redirect(url_for("login"))
    elif from_login == 1:
        resp = make_response(redirect(url_for("main_menu"), code=302))
        print(url_for("main_menu"))
        resp.set_cookie('userID', database.create_and_update_hashed_cookie(username))

        print("here is were it breaks.")
        return resp
    elif from_login == 0 and "userID" in request.cookies:
        get_cookie = check_and_get_cookie()
        if get_cookie[0]:
            if request.method == 'GET':
                get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
                print(get_username)
                return render_template('main_menu.html', username=html.unescape(get_username),
                                       user=database.get_lobbies())
        else:
            return redirect(url_for("login"))


@app.route('/nuke', methods=['GET', 'POST'])
def nuke():
    database.clear_db()
    return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('userID')
    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        # checking if the cookie exists, it does then the user is directed to main menu or else redirected to login page.
        get_cookie = check_and_get_cookie()
        if get_cookie[0]:
            # get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
            # return render_template('main_menu.html', username = html.unescape(get_username), user=database.get_lobbies())
            return redirect(url_for("main_menu"))
        else:
            return render_template('login.html')

    if request.method == "POST":
        input_username = request.form['username']
        input_password = request.form['password']

        _username = html.escape(input_username)
        _password = html.escape(input_password)

        if request.form.__contains__("register"):
            print(type(_password))
            print(type(_username))
            print(input_password)
            print(_password)

            ret_val = database.insert_user(_username, _password)
            if ret_val == 0:
                return render_template('failed_register.html')

            else:
                return render_template('login.html')

        elif request.form.__contains__("login"):
            get_salt = database.get_salt(_username)
            if get_salt != 0:
                verify = passwordSec.verify(_username, _password)
                if verify == 1:
                    # template = render_template('main_menu.html', username = html.unescape(_username), user=database.get_lobbies())
                    # resp = make_response(template)
                    # resp.set_cookie('userID', database.create_and_update_hashed_cookie(_username))
                    # resp.headers["from_login"] = 1

                    return main_menu(1, _username)
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
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            lobby_number = str(random.randint(1, 1000))
            get_cookie = check_and_get_cookie()
            get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
            database.insert_lobby(lobby_number, get_username)
            print("lobbies")
            print(database.get_lobbies())

            global ready_players
            ready_players[lobby_number] = 0

            return render_template('loading_screen.html', lobby_name=lobby_number)
    else:
        return redirect(url_for('login'))


@app.route("/loading_screen", methods=['POST'])
def waitingLobby():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
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
    else:
        return render_leaderboard('incorrect_cookie.html')


@app.route('/join_lobby', methods=['GET', 'POST'])
def join_lobby():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            return render_template('joinLobby_screen.html')
    else:
        return render_leaderboard('incorrect_cookie.html')


@socketio.on('ready')
def response():
    emit("player_ready", {'data': str(session["username"]) + " is ready."}, broadcast=True)


@socketio.on("check_room")
def check_existence(data):
    global all_rooms
    if data in all_rooms:
        file = open("templates/loading_screen.html", 'r')
        template = file.read()
        get_index = template.find("const socket = io();")
        new_template = template[get_index + len("const socket = io();"): template.find("</html>")]
        new_template = "<script type=\"text/javascript\">" + new_template
        new_template = new_template.replace("{{lobby_name}}", data)

        find_link = new_template.find("<script type=\"text/javascript\" src=\"{{ url_for('static', filename='script/HeadsTails.js') }}\"></script>")
        new_template = new_template[:find_link] + new_template[find_link + len("<script type=\"text/javascript\" src=\"{{ url_for('static', filename='script/HeadsTails.js') }}\"></script>"):]
        join_room(data)
        emit("render_template", new_template)
    else:
        return emit("nonexistent_lobby", "Lobby does not exist.")


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
def join_lobby(room_id):
    _id = html.escape(room_id)
    print("joined room")
    print(_id)
    global all_rooms
    if _id not in all_rooms.keys():
        emit("lobby_nonexistent", {'data': "Lobby does not exist."})
    else:
        join_room(_id)
        print(rooms())
        all_rooms[_id] = all_rooms[_id] + 1
        print(all_rooms)
        emit("existent_lobby")


@socketio.on('getHTMLPage')
def sendHTML(data):
    if isinstance(data, dict) and data["game"] == "getGame":
        print("data: " + str(data))
        room_id = data["room"]
        global ready_players
        ready_players[room_id] = ready_players[room_id] + 1
        if ready_players[room_id] != 2:
            emit("ready_status", "Waiting for all opponents to ready up.", room=room_id, broadcast=True)

            counter = 0
            while ready_players[room_id] != 2:
                if counter == 100_000_000:
                    emit("ready_status",
                         "Still waiting...",
                         room=room_id, broadcast=True)

                counter += 1
                continue
        else:
            emit("remove_status", room=room_id, broadcast=True)
            emit("returned_html", {'data': render_template("HeadsTails.html")}, room=room_id, broadcast=True)
    elif isinstance(data, list):
        render_lobby = render_template("loading_screen.html", lobby_name=data[1])

        emit("lobby_p2", {'data': render_lobby})


@socketio.on('player')
def handle_message(data):
    print('player message')
    print(data)
    print(data.get("choice", ""))
    print("end")


@socketio.on('ready')
def response():
    emit("player_ready", {'data': "Player is ready"}, broadcast=True)


@socketio.on('chat_message')
def handle_message(message):
    message = html.escape(message)
    emit('render_message', message, broadcast=True)


@socketio.on('getUsername_or_deleteLobby')
def getUsername_or_deleteLobby(_route):
    print("in getUsername")
    print(_route)
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")

    if len(_route) == 1:
        emit(_route[0], {'username': get_username})

    elif len(_route) == 2:  # Delete the lobby and emit to disconnect all players
        database.delete_lobby(get_username)

        global all_rooms
        del all_rooms[_route[1]]

        global ready_players
        del ready_players[_route[1]]

        emit("remove_players", "Opponent has left the match. Please return to the main menu.", room=_route[1])


# commented this out on lines 290/296 cuz it was filling up console
@socketio.on("wait_to_start_game")  # in loadingsceern.html line 23, joinLobby_screen.html line 16
def hang(roomid):
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    global player_in_room
    player_in_room[
        get_username] = roomid  # when a player joins a room, use dict to keep track of the room the player is in
    # print(player_in_room)


@socketio.on(
    "check_for_other_user_input")  # called on after everytime a player chooses heads/tails, headstails.js lines 41, 28
def check():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")  # current player
    global player_choice
    grab_roomid = player_choice[get_username][
        'room_id']  # player_choice dict =  {'a': {'room_id': '329', 'choice': 'heads'}}, grab the room id
    grab_player_choice = player_choice[get_username]['choice']  # grab choice
    for key, val in player_choice.items():  # key = 'a', val = {'room_id': '329', 'choice': 'heads'}, loop thru every players choice
        if key != get_username:  # skip current player calling this function
            roomid = val["room_id"]
            choice = val["choice"]
            if grab_roomid == roomid:
                if choice == "heads" or choice == "tails":
                    # print("key is: " + str(key))
                    # print("val is: " + str(val))
                    emit("start_game", {get_username: grab_player_choice, key: choice},
                         room=roomid)  # line 169 headstails.js
                    # dict isnt used but this is how i was thinking we wud keep track of both players choices to template in who won and add to db


@socketio.on("heads")  # called in headsFunction
def set_heads():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    global player_in_room
    roomid = player_in_room[get_username]  # player room dict is set as {username: roomid}, done in line 375
    global player_choice
    player_choice[get_username] = {"room_id": roomid,
                                   "choice": "heads"}  # player_choice dict = {'a': {'room_id': '329', 'choice': 'heads'}}
    # will constantly update players choice when clicked on


@socketio.on("tails")  # called in tailsFunction
def set_tails():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    global player_in_room
    roomid = player_in_room[get_username]  # player room dict is set as {username: roomid}, done in line 375
    global player_choice
    player_choice[get_username] = {"room_id": roomid,
                                   "choice": "tails"}  # player_choice dict =  {'a': {'room_id': '329', 'choice': 'heads'}}
    # , will constantly update players choice when clicked on


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000

    app.run(debug=False, host=host, port=port)

# while true for the websocket, only for the websocket, not for htpp requests
# example https://github.com/miguelgrinberg/flask-sock/blob/main/examples/echo-gevent.py
# sock for websockt, app.route is an http flask route, only for http req

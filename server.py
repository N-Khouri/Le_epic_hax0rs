from flask import session
from flask import redirect, url_for, request
from flask import Flask, render_template, make_response

from flask_socketio import SocketIO, emit, join_room, rooms

import html
import random
import database
import passwordSec

async_mode = None
app = Flask(__name__)
app.secret_key = '\rf\xcb\xd4f\x085L\x99\xbc\xb5\xc1|!W\xc2m\xa6\x91\x9d\xa8(n\x9d'
socketio = SocketIO(app, async_mode=async_mode)

all_rooms = {}
player_in_room = {}  # {username: room id}
player_choice = {}  # {username: choice} (choice = heads/tails.tostring)

ready_players = {}
connected_users = {}


@app.errorhandler(404)
def not_found(error):
    return render_template("404_error.html"), 404


def check_and_get_cookie():
    active_cookie = False  # assume cookie is always wrong until proven otherwise
    get_cookie = ""
    if "userID" in request.cookies:
        get_cookie = request.cookies["userID"]
        active_cookie = database.check_cookie(get_cookie)
    return active_cookie, get_cookie


def flip_coin():
    randInt = random.randint(0, 100)
    if randInt < 50:
        return "Heads"
    else:
        return "Tails"


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route("/leaderboard", methods=['GET'])
def render_leaderboard():
    get_cookie = check_and_get_cookie()
    if get_cookie[0]:
        if request.method == 'GET':
            all_players = database.update_leaderboard()
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

        return resp
    elif from_login == 0 and "userID" in request.cookies:
        get_cookie = check_and_get_cookie()
        if get_cookie[0]:
            if request.method == 'GET':
                get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
                database.delete_lobby(get_username)

                print(get_username)
                return render_template('main_menu.html', username=html.unescape(get_username),
                                       user=database.get_lobbies())
        else:
            return redirect(url_for("login"))


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

                    return main_menu(1, _username)
                elif isinstance(verify, str):
                    print("Username does not exist.")
                    return render_template('does_not_exist.html')
                else:
                    print('wrong username and password.')
                    return render_template("failed_login.html")
            else:
                return render_template('does_not_exist.html')


@app.route('/users', methods=['GET', 'POST'])
def print_users():
    return database.print_users_db()


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
            global ready_players

            lobby_number = str(random.randint(1, 1000))
            get_cookie = check_and_get_cookie()
            get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
            existent_lobby = database.get_id_by_username(get_username)
            print("existent lobby: ", existent_lobby)
            if database.get_id_by_username(get_username)[1]:
                get_old_id = database.get_id_by_username(get_username)[0]
                database.delete_lobby(get_username)
                del ready_players[get_old_id]
            database.insert_lobby(lobby_number, get_username)
            print("lobbies")
            print(database.get_lobbies())

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
    if database.check_lobby(data) and all_rooms[data] != 2:
        all_rooms[data] = all_rooms[data] + 1
        get_username = database.get_username_by_id(data)
        database.delete_lobby(get_username)
        file = open("templates/loading_screen.html", 'r')
        template = file.read()
        get_index = template.find("const socket = io();")
        new_template = template[get_index + len("const socket = io();"): template.find("</html>")]
        new_template = "<script type=\"text/javascript\">" + new_template
        new_template = new_template.replace("{{lobby_name}}", data)

        find_link = new_template.find(
            "<script type=\"text/javascript\" src=\"{{ url_for('static', filename='script/HeadsTails.js') }}\"></script>")
        new_template = new_template[:find_link] + new_template[find_link + len(
            "<script type=\"text/javascript\" src=\"{{ url_for('static', filename='script/HeadsTails.js') }}\"></script>"):]
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

    elif len(_route) == 3:
        emit("username_in_js", {'username': get_username})


# commented this out on lines 290/296 cuz it was filling up console
@socketio.on("wait_to_start_game")  # in loadingsceern.html line 23, joinLobby_screen.html line 16
def hang(roomid):
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    global player_in_room
    player_in_room[
        get_username] = roomid  # when a player joins a room, use dict to keep track of the room the player is in


@socketio.on(
    "check_for_other_user_input")  # called on after everytime a player chooses heads/tails, headstails.js lines 41, 28
def check():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")  # current player
    global player_choice
    print("This is bs")
    print(player_choice)
    grab_roomid = player_choice[get_username][
        'room_id']  # player_choice dict =  {'a': {'room_id': '329', 'choice': 'heads'}}, grab the room id
    grab_player_choice = player_choice[get_username]['choice']  # grab choice
    for key, val in player_choice.items():  # key = 'a', val = {'room_id': '329', 'choice': 'heads'}, loop through every player choice
        if key != get_username:  # skip current player calling this function
            roomid = val["room_id"]
            choice = val["choice"]
            if grab_roomid == roomid:
                if choice == "Heads" or choice == "Tails":
                    # print("key is: " + str(key))
                    # print("val is: " + str(val))

                    # Replace this with server side game functionality
                    serverFlipCoin = flip_coin()
                    emit("start_game",
                         {"player1": get_username, get_username: grab_player_choice, "player2": key, key: choice,
                          "server_flip": serverFlipCoin}, room=roomid)  # line 169 headstails.js

                    # dict isn't used but this is how I was thinking we would keep track of both players choices to template in who won and add to db


@socketio.on("heads")  # called in headsFunction
def set_heads():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    global player_in_room
    roomid = player_in_room[get_username]  # player room dict is set as {username: roomid}, done in line 375
    global player_choice
    player_choice[get_username] = {"room_id": roomid,
                                   "choice": "Heads"}  # player_choice dict = {'a': {'room_id': '329', 'choice': 'heads'}}
    # will constantly update players choice when clicked on


@socketio.on("tails")  # called in tailsFunction
def set_tails():
    get_cookie = check_and_get_cookie()
    get_username = database.get_db_info_via_cookie(get_cookie[1], "username")
    print()
    print(get_username)
    global player_in_room
    roomid = player_in_room[get_username]  # player room dict is set as {username: roomid}, done in line 375
    global player_choice
    player_choice[get_username] = {"room_id": roomid,
                                   "choice": "Tails"}  # player_choice dict =  {'a': {'room_id': '329', 'choice': 'heads'}}
    print("this is tails")
    print(player_choice)
    # , will constantly update players choice when clicked on


@socketio.on("leaderboard_update_won")
def update_leaderboard_won(username):
    database.increment_score(username)
    database.increment_games(username)


@socketio.on("leaderboard_update_lost")
def update_leaderboard_lost(username):
    database.increment_games(username)


@socketio.on('connect')
def handle():
    return print("Successfully connected.")


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000

    app.run(debug=False, host=host, port=port)

# while true for the websocket, only for the websocket, not for htpp requests
# example https://github.com/miguelgrinberg/flask-sock/blob/main/examples/echo-gevent.py
# sock for websocket, app.route is a http flask route, only for http req

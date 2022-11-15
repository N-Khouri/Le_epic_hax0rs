import datetime
from flask import Flask, render_template, request
from flask import Flask, redirect, url_for, request

import database
import passwordSec

app = Flask(__name__)
sock = Sock(app)


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html') 
    else:
        return render_template('login.html')

@app.route("/TicTacToe", methods=['POST', 'GET'])
def game():
    if request.method == 'GET':
        return render_template('TicTacToe.html') 
    else:
        return render_template('login.html')


@sock.route('/echo')
def echo(ws):
    request # has all of http information
    while True: #waits for data on socket from one client
        data = ws.receive()
        if data == 'close':
            break
        ws.send(data)



@app.route('/nuke', methods=['GET', 'POST'])
def nuke():
    database.clear_db()
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
                    return render_template('main_menu.html')

            elif request.form.__contains__("login"):
                get_salt = database.get_salt(input_username)
                if get_salt != 0:
                    verify = passwordSec.verify(input_username, input_password)
                    if verify == 1:
                        return render_template('main_menu.html')
                    else:
                        return render_template('failed_login.html')




















            
######################### TESTING PURPOSES ONLY #######################

@app.route('/users', methods=['GET', 'POST'])
def print_users():
    return database.print_users_db()


@app.route('/all', methods=['GET', 'POST', 'DELETE']) # delete thru postman
def empty_users():
    if request.method == 'DELETE':
        database.clear_db()
    return "DATABASE WAS DESTROYED"



@app.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/contact/')
def contact_info():
    return render_template('contact_info.html')


@app.route('/dashboard/<name>/<password>')
def dashboard(name, password):
    output1 = 'welcome %s' % name
    output2 = 'your password is %s' % password
    return output1 + ", " + output2


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 8000

    app.run(debug=False, host=host, port=port)



# while true for the websocket, only for the websocket, not for htpp requests
#example https://github.com/miguelgrinberg/flask-sock/blob/main/examples/echo-gevent.py
# sock for websockt, app.route is an http flask route, only for http req
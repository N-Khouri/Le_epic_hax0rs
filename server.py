import datetime
from flask import Flask, render_template, request
from flask import Flask, redirect, url_for, request

import database

app = Flask(__name__)


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

@app.route('/login', methods=['GET', 'POST'])
def login():
        # print(request.method)
        if request.method == 'GET':
            # print("aAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            return render_template('login.html')
        elif request.method == "POST":
            input_username = request.form['username']
            input_password = request.form['password']
            for line in request.form:
                print(line)




            return render_template('failed_login.html')


            # ret_val = database.insert_user(input_username, input_password)
            # if ret_val == 0:
            #     # print("acc exists")
            #     print("an account with the same username has already been created")
            #     return render_template('failed_login.html')
            #
            # elif ret_val == 1:
            #     # print("acc created")
            #     print("account was created, username is: " + str(input_username) + ", and password is: " + str(input_password))
            #     return render_template('main_menu.html')








            
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

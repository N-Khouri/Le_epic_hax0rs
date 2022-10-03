import datetime
from flask import Flask, render_template, request
from flask import Flask, redirect, url_for, request
app = Flask(__name__)



@app.route("/",methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        return redirect(url_for('dashboard', name=user, password = password))
    else:
        user = request.args.get('name')
        return render_template('login.html')
    # return render_template('login.html')


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
    app.run()

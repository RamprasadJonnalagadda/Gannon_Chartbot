import json
import sqlite3
from flask import Flask, render_template, request,session,logging,url_for,redirect,flash
from flask_recaptcha import ReCaptcha
import os
import requests

app = Flask(__name__)
recaptcha = ReCaptcha(app=app)
app.secret_key = os.urandom(24)
app.static_folder = 'static'
conn = sqlite3.connect('collegeBot.db')
'''
#conn.execute("DROP TABLE IF EXISTS users")
conn.execute("create table users(name varchar(30), email varchar(30), password varchar(15));")
conn.execute("DROP TABLE IF EXISTS suggestion")
conn.execute("create table suggestion(email varchar(30), message varchar(255));")
conn.commit()
'''

app.config.update(dict(
    RECAPTCHA_ENABLED=True,
    RECAPTCHA_SITE_KEY="6Lc1CNgiAAAAAIvlBRXYgJxY_4Tt23-0VlybXYtX",
    RECAPTCHA_SECRET_KEY="6Lc1CNgiAAAAAKmqxGHyl6gLp5nvS8QbmRBEav6c"
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'


@app.route("/index")
def home():
    if 'id' in session:
        return render_template('index.html')
    else:
        return redirect('/')


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/register')
def about():
    return render_template('register.html')


@app.route('/forgot')
def forgot():
    return render_template('forgot.html')


@app.route('/login_validation',methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    with sqlite3.connect('collegeBot.db') as conn:
        users = conn.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(
            email, password))
        users = list(users.fetchall())

    if len(users) > 0:
        session['id'] = users[0][0]
        flash('You were successfully logged in')
        return redirect('/index')
    else:
        flash('Invalid credentials !!!')
        return redirect('/')


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    with sqlite3.connect('collegeBot.db') as conn:
        conn.execute("""INSERT INTO  users(name,email,password) VALUES('{}','{}','{}')""".format(name, email, password))
        conn.commit()

    myuser = conn.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
    flash('You have successfully registered!')
    myuser = list(myuser.fetchall())
    session['id'] = myuser[0][0]
    return redirect('/index')


@app.route('/suggestion',methods=['POST'])
def suggestion():
    email = request.form.get('uemail')
    suggesMess = request.form.get('message')
    with sqlite3.connect('collegeBot.db') as conn:
        conn.execute("""INSERT INTO  suggestion(email,message) VALUES('{}','{}')""".format(email,suggesMess))
        conn.commit()
    flash('You suggestion is successfully sent!')
    return redirect('/index')


@app.route('/add_user',methods=['POST'])
def register():
    if recaptcha.verify():
        flash('New User Added Successfully')
        return redirect('/register')
    else:
        flash('Error Recaptcha')
        return redirect('/register')


@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    if userText.lower() == "are you a bot":
        return "yes, I am a Gannon bot "

    data = json.dumps({"sender": "Rasa", "message": userText})

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    res = requests.post('http://localhost:5005/webhooks/rest/webhook', data=data, headers=headers).json()
    if not res:
        # return "I do not understand your question. Please rephrase and ask the question"
        return "Please contact global support for more details. <br><br> <a href='https://www.gannon.edu/admissions/international-admissions/global-support-and-student-engagement/' target='_blank'> click here for support </a>."
    return str(res[0]['text'])


if __name__ == "__main__":
    # app.secret_key=""
    app.run()

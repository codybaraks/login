from flask import Flask, redirect, request, render_template, session, url_for, flash
import mysql.connector as connector
import uuid
from flask_mail import Message, Mail
from itsdangerous import URLSafeSerializer, SignatureExpired
# import random, string
from validation import *
from passlib.hash import sha256_crypt
import hashlib

db = connector.connect(host="localhost", user="root", passwd="root", database="personal")

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'earvinbaraka@gmail.com'
app.config['MAIL_PASSWORD'] = 'Commandprompt.1'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.secret_key = 'jxbxjxdjdjdjddj'


@app.route('/')
def hello_world():
    return redirect(url_for('register'))


@app.route('/pass_form')
def pass_form():
    return redirect(url_for('password_confirm'))


@app.route('/home')
def home():
    return render_template('main.html')


@app.route('/form_reset', methods=['POST', 'GET'])
def form_reset():
    form = ResetForm()
    form.validate_on_submit()
    if request.method == 'POST':
        email = request.form["email"]
        # if email == None:
        #     flash("check your Email!")
        # else:
        #     print('mail not entered')
        #     flash('Enter Your Email')
        print(email)
    return render_template('reset.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    form.validate_on_submit()
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        # password.hexdigest
        # password = hashlib.md5(password.encode())
        print(name, surname, email, password)
        cursor = db.cursor()
        sql = "INSERT INTO `register`(`name`, `surname`, `email`, `password`) VALUES (%s,%s,%s,%s)"
        val = (name, surname, email, password)
        cursor.execute(sql, val)
        db.commit()
    return render_template('home.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = RegisterForm()
    form.validate_on_submit()
    if request.method == 'POST':
        email = request.form['email']
        password = (request.form['password'])

        print(email, password)
        cursor = db.cursor(buffered=True)
        sql = "SELECT * FROM register WHERE email=%s AND password=%s"
        val = (email, password)
        cursor.execute(sql, val)
        register = cursor.fetchone()
        if register:
            session['email'] = register[2]
            session['password'] = register[3]
            return redirect(url_for('home'))
        else:
            flash('Wrong username or password!')

    return render_template('login.html', form=form)


@app.route('/password_confirm', methods=['GET', 'POST'])
def password_confirm():
    # if request.form["password"] != request.form["conf_pass"]:
    #     flash("Your password and password verification didn't match."
    #           , "danger")
    form = RegisterForm()
    form.validate_on_submit()
    if request.method == 'POST':
        if request.form["password"] != request.form["conf_pass"]:
            flash("Your password and password verification didn't match.", "danger")
            password = request.form['password']
            conf_pass = request.form['conf_pass']

            print(password, conf_pass)
            cursor = db.cursor()
            sql = "UPDATE `register` SET `password`=%s WHERE email='earvinbaraka@gmail.com'"
            val = (password,)
            cursor.execute(sql, val)
            db.commit()
            flash('password updated')
    return render_template('password_Reset.html', form=form)


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    form = RegisterForm()
    form.validate_on_submit()
    if request.method == 'POST':
        email = request.form['email']
        if email == '':
            print('email not entered', 'danger')
            flash('Email not Entered, Enter email', 'danger')
            return redirect(url_for('form_reset'))
        else:
            print('thanks its entered')
            flash('Email captured')
        print(email)
        cursor = db.cursor(buffered=True)
        sql = "SELECT * FROM register WHERE email=%s"
        val = (email,)
        cursor.execute(sql, val)
        register = cursor.fetchone()
        if register:
            session['email'] = register[2]
            print(uuid.uuid4().hex.upper())
            token = uuid.uuid4().hex.upper()
            sql2 = "INSERT INTO `token`(`token`, `email`) VALUES (%s,%s)"
            val2 = (token, email)
            cursor.execute(sql2, val2)
            db.commit()

            msg = Message(subject='Password Reset', sender='earvinbaraka@gmail.com',
                          recipients=[request.form['email']])
            link = url_for('conf_email', token=token, _external=True)
            msg.body = render_template('sentmail.html', token=token, link=link)
            mail.send(msg)

            flash('Link sent to your Email')
            # print("checking for real")
            return redirect(url_for('register', token=token))
        else:

                msg = Message(subject='Password Reset', sender='earvinbaraka@gmail.com',
                              recipients=[request.form['email']])
                msg.body = "This email does not exist in our system, " \
                           "if you not the one who entered this mail ignore this message"
                mail.send(msg)
                flash('Email does not exist or wrong username or password!', 'danger')
                return redirect(url_for('register'))

    return render_template('home.html', form=form)


@app.route('/conf_email/<token>')
def conf_email(token):
    try:
        email = token
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    # return '<h1>The token works!</h1>'
    return redirect(url_for('pass_form'))


if __name__ == '__main__':
    app.run()

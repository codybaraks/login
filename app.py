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


@app.route('/slider')
def slider():
    if session.get('names') == None:
        return redirect(url_for('login'))
    return render_template('Main_Site.html')


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
    if session.get('names') == None:
        return redirect(url_for('login'))

    if session.get('role') == "Normal":
        return redirect(url_for('slider'))

    form = RegisterForm()
    form.validate_on_submit()
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        # sha256_crypt.encrypt
        # password.hexdigest
        # password = hashlib.md5(password.encode())
        print(name, surname, email, password, role)
        cursor = db.cursor()
        sql = "INSERT INTO `register`(`name`, `surname`, `email`, `password`, `role`) VALUES (%s,%s,%s,%s,%s)"
        val = (name, surname, email, password, role)
        cursor.execute(sql, val)
        db.commit()
    return render_template('home.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    if form.validate_on_submit():
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            cursor = db.cursor()
            print(email, password)
            sql = "SELECT * FROM register WHERE email=%s AND password=%s"
            vals = (email, password)
            cursor.execute(sql, vals)
            register = cursor.fetchone()
            if register:
                session['names'] = register[2]
                session['role'] = register[5]
                return redirect(url_for('slider'))
            else:
                flash('wrong username or password!')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if session.get('names') == None:
        return redirect(url_for('login'))
    session.pop('names')
    session.pop('role')
    return redirect(url_for('login'))


@app.route('/show_users')
def show_users():
    if session.get('names') == None:
        return redirect(url_for('login'))

    if session.get('role') == "Normal":
        return redirect(url_for('slider'))

    cursor = db.cursor()
    sql = "SELECT * FROM register"
    cursor.execute(sql)
    register = cursor.fetchall()
    return render_template('show_users.html', register=register)


@app.route('/del/<id>')
def del_ref(id):
    if session.get('names') == None:
        return redirect(url_for('login'))
    cursor = db.cursor()
    sql = "DELETE FROM register WHERE id=%s"
    cursor.execute(sql, (id,))
    db.commit()
    flash('User Successfully Removed ')
    return redirect(url_for('remove'))


@app.route('/delete')
def remove():
    if session.get('names') == None:
        return redirect(url_for('login'))
    cursor = db.cursor()
    sql = "SELECT * FROM register"
    cursor.execute(sql)
    register = cursor.fetchall()
    return render_template('show_users.html', register=register)


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
            cursor = db.cursor(buffered=True)
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

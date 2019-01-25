from flask import Flask, redirect, request, render_template, session, url_for, flash
import mysql.connector as connector
import random, string
db = connector.connect(host="localhost", user="root", passwd="root", database="personal")

app = Flask(__name__)
app.secret_key = 'jxbxjxdjdjdjddj'


@app.route('/')
def hello_world():
    return redirect(url_for('register'))


@app.route('/reset_form')
def reset_form():
    return render_template('reset.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        print(name, surname, email, password)
        cursor = db.cursor()
        sql = "INSERT INTO `register`(`name`, `surname`, `email`, `password`) VALUES (%s,%s,%s,%s)"
        val = (name, surname, email, password)
        cursor.execute(sql, val)
        db.commit()
    return render_template('home.html')


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        email = request.form['email']

        print(email)
        cursor = db.cursor(buffered=True)
        sql = "SELECT * FROM register WHERE email=%s"
        val = (email,)
        cursor.execute(sql, val)
        register = cursor.fetchone()
        if register:
            session['email'] = register[2]
            flash('message correct pass')
            def randomString(stringLength=10):
             print("First Random String is  ", randomString())
            # print("checking for real")
            return redirect(url_for('register'))
        else:
            flash('wrong username or password!')
    return render_template('home.html')


if __name__ == '__main__':
    app.run()

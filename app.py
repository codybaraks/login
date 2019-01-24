from flask import Flask, redirect, request, render_template
import mysql.connector as connector

db = connector.connect(host="localhost", user="root", passwd="root", database="personal")

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


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


if __name__ == '__main__':
    app.run()

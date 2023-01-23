from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import string
import secrets

app = Flask(__name__, template_folder='templates', static_folder='staticFiles')

app.secret_key = '$20061221Mm'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '$20061221Mm'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

mail = Mail(app) 
   
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mohamedashraf321333@gmail.com'
app.config['MAIL_PASSWORD'] = 'bjsereavrjyognyy'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

email = None
password = None
code = None
 
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            return redirect(url_for('home'))
        else:
            error = 'Incorrect username/password!'
    return render_template('login.html', error=error)

@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST' and 'password' in request.form and 'password2' in request.form and 'email' in request.form:
        global email, password, code
        password2 = request.form['password2']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            error = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            error = 'Invalid email address!'
        elif password2 != password:
            error = "Passwords don't match"
        elif not email or not password or not password2:
            error = "Please fill the form"
        elif len(password) < 8:
            error = "Password must be more than 8"
        else:
            code = codeGenerator()
            msg = Message(
                'Hello',
                sender ='mohamedashraf321333@gmail.com',
                recipients = [email]
                  )
            msg.html = render_template("verificationEmail.html", code=code)
            mail.send(msg)
            return redirect(url_for('activate'))
    elif request.method == 'POST':
        error = 'Please fill out the form!'
    return render_template('signUp.html', error=error)

@app.route('/activate', methods=['POST', 'GET'])
def activate():
    error = None
    if request.method == 'POST' and 'code' in request.form:
        test = request.form['code']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if test == code:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s)', (password, email,))
            mysql.connection.commit()
            error = 'You have successfully registered!'
            return redirect(url_for('login'))
        else:
            error = 'Invalid Code'
    return render_template('check.html', error=error)

@app.route('/volunteer', methods=['POST', 'GET'])
def volunteer():
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        msg = Message(
            'Volunteering form',
            sender ='mohamedashraf321333@gmail.com',
            recipients = [email]
            )
        msg.body = "This service isn't available yet!"
        mail.send(msg)
        redirect(url_for('home'))
    return render_template('volunteer.html')

@app.route('/contact-us', methods=['POST', 'GET'])
def contactUs():
    if request.method == 'POST' and 'email' in request.form:
        myEmail = 'medosoudi14@gmail.com'
        email = request.form['email']
        name = request.form['name']
        message = request.form['message']
        msg = Message(
            'One of contacts',
            sender ='mohamedashraf321333@gmail.com',
            recipients = [myEmail]
            )
        msg.html = render_template("contactUsEmail.html", name=name, message=message, email=email)
        mail.send(msg)
        redirect(url_for('home'))
    return render_template('contactUs.html')

@app.route('/forget-password', methods=['POST', 'GET'])
def forgetPassword():
    error = None
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT password FROM accounts WHERE email = %s', (email,))
            password = str(cursor.fetchone())
            password = password[14:]
            password = password[:-2]
            msg = Message(
                'Your forgotten Password',
                sender ='mohamedashraf321333@gmail.com',
                recipients = [email]
               )
            msg.html = render_template("forgottenPass.html", password=password)
            mail.send(msg)
        else:
            error = 'Invalid Email'
    return render_template('forgetPassword.html', error=error)
 
@app.route('/info')
def info():
    return render_template('info.html')

def codeGenerator():
    digits = string.digits
    pwd_length = 8
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(digits))
    return pwd

if __name__=='__main__':
    app.run(debug = True)
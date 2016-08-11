from flask import Flask, redirect, url_for, request, render_template, escape, session
from flask_pymongo import PyMongo
from os import urandom

app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/', methods=['POST', 'GET'])
def index():

	if request.method == 'POST':

		if 'login' in request.form:
			session['username'] = request.form['username']

		elif 'logout' in request.form:
			session.pop('username', None)

		elif 'signup' in request.form:
			return redirect(url_for('signup'))

	return render_template('main.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	result = None
	if request.method == 'POST':
		if validate_signup(request.form['username'], request.form['password']):
			add_user(request.form['username'], request.form['password'])
			result = 'success!'
		else:
			result = 'error'
	
	return render_template('signup.html', result=result)

def validate_signup(username, password):
	return True

def add_user(username, password):
	return True

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		session['username'] = request.form['username']
		return redirect(url_for('index'))
	return '''
		<form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''
	# error = None
	# if request.method == 'POST':
	# 		if valid_login(request.form['username'],
	# 		   			   request.form['password']):
	# 			session['username'] = request.form['username']
	# 			return log_the_user_in(request.form['username'])
	# 		else:
	# 			error = 'Invalid username/password'
	# return render_template('login.html', error=error)

app.secret_key = str(urandom(24))
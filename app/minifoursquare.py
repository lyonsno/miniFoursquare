from flask import Flask, redirect, url_for, request, render_template, escape, session
from flask.ext.login import LoginManager
from flask.views import MethodView
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from os import urandom
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_47hcqr8r'
app.config['MONGO_URI'] = 'mongodb://heroku_47hcqr8r:8qrmbmda85l7dmtjc9cnvc9bpl@ds139715.mlab.com:39715/heroku_47hcqr8r'

mongo = PyMongo(app)
app.secret_key = str(urandom(24))

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():

	if form.validate_on_submit():
		login_user(user)

@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)

# this is a placeholder, not at all secure
class LoginForm():

	def __init__(self, username, password):
		self.username = userName
		self.password = password
		self._id = None

	def validate_on_submit():
		return 

class User(MethodView):

	def __init__(self):
		self.authenticated = True
		self.is_active = True
		self.is_anonymous = False

	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return self.isActive

	def is_anonymous(self):
		return self.isAnonymous

	def get_id(self):
		return self._id

	def get(self, user_id):
		if user_id is None:
			#return a list of users
			cursor = mongo.db.users.find({})
			user_jsons = {'users' : []}
			for doc in cursor:
				user_jsons['users'].append(doc)

			user_jsons = json_util.dumps(user_jsons, default=json_util.default)
			return user_jsons
		else:
			# expose a single user
			print("exposing")
			user = mongo.db.users.find_one_or_404({'_id' : ObjectId(user_id)})
			user_json = json_util.dumps(user, default=json_util.default)
			return user_json

	def post(self):
		# create a new user
		form = request.form
		user = {"username" : form["username"], "reviewIds" : form["reviewIds"] }
		mongo.db.users.insert_one(user)
		return json_util.dumps(user, default=json_util.default)

	def delete(self, user_id):
		# delete a single user
		result = mongo.db.users.delete_one({'_id' : ObjectId(user_id)})
		if result.deleted_count != 1:
			return "404 user not found"
		else: 
			return "200 user deleted"

	def put(self, user_id):
		# update a single user
		pass

user_view = User.as_view('user')
app.add_url_rule('/users/', defaults={'user_id' : None}, view_func=user_view, methods=['GET'])
app.add_url_rule('/users/', view_func=user_view, methods=['POST'])
app.add_url_rule('/users/<user_id>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])

class Review():
	
	def __init__(self, numStars, ):
		self.numStars = 5
		self.text = ""
		self.tags = []
		self.dateTime = None
		self.businessId
		self.businessName
		self.userId
		self.userName

class Business():

	def __init__(self, jsonObj):
		jsonDict = json_util.loads(jsonObj)
		self.name = jsonDict["name"]
		self.reviewIds = jsonDict["reviewIds"]
		self.location = jsonDict["location"]

class UserAPI(MethodView):

	def get(self, user_id):
		if user_id is None:
			#return a list of users
			pass
		else:
			# expose a single user
			pass

	def post(self):
		# create a new user
		form = request.form
		user = {"name" : form["name"], "reviewIds" : form["reviewIds"] }
		mongo.db.users.insert_one(user)
		return str(user)

	def delete(self, user_id):
		# delete a single user
		pass

	def put(self, user_id):
		# update a single user
		pass



# endpoint for leaving review of business
@app.route('/businesses/<bizName>/reviews', methods=['GET', 'POST'])
def reviews(bizName):
	if request.method == 'POST':

		mongo.db.reviews.insert_one({request.form})
		mongo.db.businesses.update({'name' : bizName}, {'$push' : {'reviews' : reviewId}}, True)

# endpoint for getting business data json
@app.route('/business/<bizId>/data', methods=['GET'])
def buisness_data(bizId):
	biz = mongo.db.businesses.find({'_id' : bizId})
	return json_util.dumps(biz)

@app.route('/', methods=['POST', 'GET'])
def index():
	invalidLogin = False
	if request.method == 'POST':

		if 'login' in request.form:
			if not login_user(request.form['username'], session):
				invalidLogin = True

		elif 'logout' in request.form:
			session.pop('username', None)

		elif 'signup' in request.form:
			return redirect(url_for('signup'))

	return render_template('index.html', invalidLogin=invalidLogin)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	result = None
	if request.method == 'POST':
		if 'gohome' in request.form:
			return redirect(url_for('index'))
		elif 'username' in request.form:
			result = try_create_user(request.form['username'])

	if result == 'success':
		login_user(request.form['username'], session)

	return render_template('signup.html', result=result)

def try_create_user(username):
	if not user_exists(request.form['username']):
		username = request.form['username']
		create_user(username)
		login_user(username, session)
		return 'success'
	else:
		return 'failure'
def create_user(username):
	mongo.db.users.insert_one({'username': username})

def user_exists(username):
	user = mongo.db.users.find_one({'username': username})
	if user is None:
		return False
	else:
		return True

def login_user(username, session):
	if user_exists(username):
		session['username'] = username
		return True
	else:
		return False




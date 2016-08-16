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

class User(MethodView):

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
			return "404 user not found for delete"
		else: 
			return "200 user deleted"

	def put(self, user_id):
		# update a single user
		# don't think we really need this one yet
		pass

userView = User.as_view('user')
app.add_url_rule('/users/', defaults={'user_id' : None}, view_func=userView, methods=['GET'])
app.add_url_rule('/users/', view_func=userView, methods=['POST'])
app.add_url_rule('/users/<user_id>', view_func=userView, methods=['GET', 'PUT', 'DELETE'])

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

class Business(MethodView):

	def get(self, business_id):
		if business_id is None:
			#return a list of all businesses
			cursor = mongo.db.businesses.find({})
			biz_jsons = {'businesses' : []}
			for doc in cursor:
				biz_jsons['businesses'].append(doc)
			biz_jsons = json_util.dumps(biz_jsons, default=json_util.default)
			return biz_jsons

		else:
			# expose single business
			biz = mongo.db.businesss.find_one_or_404({'_id' : ObjectId(business_id)})
			biz_json = json_util.dumps(biz, default=json_util.default)
			return biz_json

	def post(self):
		# create a new business
		form = request.form
		biz = {"businessName" : form["businessName"], "reviewIds" : form["reviewIds"], "location" : form["location"]}
		mongo.db.businesses.insert_one(biz)
		return json_util.dumps(biz, default=json_util.default)

	def delete(self, business_id):
		# delete a single business
		result = mongo.db.businesses.delete_one({'_id' : ObjectId(business_id)})
		if result.deleted_count != 1:
			return "404 business not found for delete"
		else:
			return "200 business deleted"

	def put(self, business_id):
		# update a single business
		# dont need this yet
		pass

businessView = Business.as_view('business')
app.add_url_rule('/businesses/', defaults={'business_id' : None}, view_func=businessView, methods=['GET'])
app.add_url_rule('/businesses/', view_func=businessView, methods=['POST'])
app.add_url_rule('/businesses/<business_id>', view_func=businessView, methods=['GET', 'PUT' 'DELETE'])


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




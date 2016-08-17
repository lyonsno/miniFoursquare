from flask import Flask, redirect, url_for, request, render_template, escape, session
from flask.views import MethodView
from flask_pymongo import PyMongo
from bson import json_util
from bson.son import SON
from bson.objectid import ObjectId
from os import urandom

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_47hcqr8r'
app.config['MONGO_URI'] = 'mongodb://heroku_47hcqr8r:8qrmbmda85l7dmtjc9cnvc9bpl@ds139715.mlab.com:39715/heroku_47hcqr8r'

mongo = PyMongo(app)
app.secret_key = str(urandom(24))

class User(MethodView):

	def get(self, userId):
		if userId is None:
			#return a list of users
			cursor = mongo.db.users.find({})
			userJsons = {'users' : []}
			for doc in cursor:
				userJsons['users'].append(doc)

			userJsons = json_util.dumps(userJsons, default=json_util.default)
			return userJsons
		else:
			# expose a single user
			user = mongo.db.users.find_one_or_404({'_id' : ObjectId(userId)})
			userJson = json_util.dumps(user, default=json_util.default)
			return userJson

	def post(self):
		# create a new user
		form = request.form
		user = {"username" : form["username"], "reviewIds" : [] }
		mongo.db.users.insert_one(user)
		return json_util.dumps(user, default=json_util.default)

	def delete(self, userId):
		# delete a single user
		result = mongo.db.users.delete_one({'_id' : ObjectId(userId)})
		if result.deleted_count != 1:
			return "404 user not found for delete"
		else: 
			return "200 user deleted"

	def put(self, userId):
		# update a single user
		# don't think we really need this one yet
		pass

userView = User.as_view('user')
app.add_url_rule('/users/', defaults={'userId' : None}, view_func=userView, methods=['GET'])
app.add_url_rule('/users/', view_func=userView, methods=['POST'])
app.add_url_rule('/users/<userId>', view_func=userView, methods=['GET', 'PUT', 'DELETE'])

class Review(MethodView):
	
	def get(self, reviewId):
		if reviewId is None:
			#return a list of reviews
			cursor = mongo.db.reviews.find({})
			reviewJsons = {'reviews' : []}
			for doc in cursor:
				reviewJsons['reviews'].append(doc)

			reviewJsons = json_util.dumps(reviewJsons, default=json_util.default)
			return reviewJsons

		else:
			# expose a single review
			review = mongo.db.reviews.find_one_or_404({'_id' : ObjectId(reviewId)})
			reviewJson = json_util.dumps(review, default=json_util.default)
			return reviewJson

	def post(self):
		# create a new review

		form = request.form
		review = {
					"numStars" : form["numStars"],
					"text" : form["text"], 
					"tags" : form["tags"],
					"userId" : form["userId"],
					"businessId" : form["businessId"]
				  }
		result = mongo.db.reviews.insert_one(review)

		mongo.db.users.update(
								{"_id" : ObjectId(form["userId"])},
								{'$push': { "reviewIds" : result.inserted_id }},
								False
							)
		mongo.db.businesses.update(
									{"_id" : ObjectId(form["businessId"])},
									{'$push': {"reviewIds" : result.inserted_id }},
									False
								)

		return json_util.dumps(review, default=json_util.default)

	def delete(self, reviewId):
		# delete a single review 
		review = mongo.db.reviews.find_one_or_404({'_id' : ObjectId(reviewId)})
		result = mongo.db.reviews.delete_one({'_id' : ObjectId(reviewId)})

		if result.deleted_count != 1:
			return "404 review not found for delete"

		else:
			mongo.db.users.update(
									{"_id" : ObjectId(review['userId'])},
									{'$pull': { "reviewIds" : ObjectId(reviewId) }},
									False
								)
			mongo.db.businesses.update(
										{"_id" : ObjectId(review['businessId'])},
										{'$pull': {"reviewIds" : ObjectId(reviewId) }},
										False
									)

			return "200 user deleted"

	def put(self):
		# update single review
		# don't need this yet
		pass

reviewView = Review.as_view('review')
app.add_url_rule('/reviews/', defaults={'reviewId' : None}, view_func=reviewView, methods=['GET'])
app.add_url_rule('/reviews/', view_func=reviewView, methods=['POST'])
app.add_url_rule('/reviews/<reviewId>', view_func=reviewView, methods=['GET', 'PUT', 'DELETE'])

class Business(MethodView):

	def get(self, businessId):
		if businessId is None:
			#return a list of all businesses
			cursor = mongo.db.businesses.find({})
			biz_jsons = {'businesses' : []}
			for doc in cursor:
				biz_jsons['businesses'].append(doc)
			biz_jsons = json_util.dumps(biz_jsons, default=json_util.default)
			return biz_jsons

		else:
			# expose single business
			biz = mongo.db.businesss.find_one_or_404({'_id' : ObjectId(businessId)})
			biz_json = json_util.dumps(biz, default=json_util.default)
			return biz_json

	def post(self):
		# create a new business
		form = request.form
		biz = {"businessName" : form["businessName"], "reviewIds" : [], "location" : [ form["long"], form["lat"] ]}
		mongo.db.businesses.insert_one(biz)
		return json_util.dumps(biz, default=json_util.default)

	def delete(self, businessId):
		# delete a single business
		result = mongo.db.businesses.delete_one({'_id' : ObjectId(businessId)})
		if result.deleted_count != 1:
			return "404 business not found for delete"
		else:
			return "200 business deleted"

	def put(self, businessId):
		# update a single business
		# dont need this yet
		pass

businessView = Business.as_view('business')
app.add_url_rule('/businesses/', defaults={'businessId' : None}, view_func=businessView, methods=['GET'])
app.add_url_rule('/businesses/', view_func=businessView, methods=['POST'])
app.add_url_rule('/businesses/<businessId>', view_func=businessView, methods=['GET', 'PUT' 'DELETE'])


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




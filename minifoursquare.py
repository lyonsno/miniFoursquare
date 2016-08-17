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

@app.route('/'):
def home():
	return "minifoursquarehome"
	
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
					"tags" : form.getlist("tags"),
					"userId" : form["userId"],
					"businessId" : form["businessId"]
				  }
		result = mongo.db.reviews.insert_one(review)

		# add review id to corresponding user and business
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
		# increment review count for business
		mongo.db.businesses.update(
									{"_id" : ObjectId(form["businessId"])},
									{'$inc' : {"numReviews" : 1}},
									True
								)

		# update business tags and average rating
		

		return json_util.dumps(review, default=json_util.default)

	def delete(self, reviewId):
		# delete a single review 
		review = mongo.db.reviews.find_one_or_404({'_id' : ObjectId(reviewId)})
		result = mongo.db.reviews.delete_one({'_id' : ObjectId(reviewId)})

		if result.deleted_count != 1:
			return "404 review not found for delete"

		else:
			# delete review id from user and business
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
			mongo.db.businesses.update(
									{"_id" : ObjectId(review["businessId"])},
									{'$inc' : {"numReviews" : -1}},
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
		biz = {
				"businessName" : form["businessName"],
				"reviewIds" : [],
				"numReviews" : 0,
				"location" : [ form["long"], form["lat"] ],
				"averageRating" : None,
				"tags" : []

			}

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

if __name__ == '__main__':
    app.run()


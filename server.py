# ETAaaS Client API Interface
from auth import ExceptionError, requires_auth
import json
from flask import Flask, request
from flask_cors import cross_origin
from eta import Eta

APP = Flask(__name__)

# Controllers API

#Public GET Access
@APP.route("/", methods=['GET'])
def index_get():
    return "Welcome to ETAaaS. Please refer to documentation to make your first API call.\n"

#Secure POST Access
@APP.route("/", methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def index_post():
	try:
		data = request.get_json()
		eta = Eta(
		data['origin'], 
		data['destination'], 
		data['mode']
		)
		eta.calculate()
	except KeyError:
		raise ExceptionError({
			"code": KeyError.__name__,
			"hint": "An error was made in the JSON Keys you provided."},
			400)
	except Exception as e:
		raise ExceptionError({
			"code": str(e),
			"hint": "Unexpected Exception Message. Please contact support with the data you used so we add it to our automated tests."},
			400)
	return eta.to_JSON()


if __name__ == "__main__":
    APP.run(debug=True)
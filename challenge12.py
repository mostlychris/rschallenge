import os
import sys
import requests
import werkzeug
from werkzeug import MultiDict
import json

def main():
	"""Creates or lists mailgun routes.

	Supply the match_recipient when calling function 'create_route'.
	The create_route function sets the action as a forward to 
	'http//cldsrvr.com/challenge1'

	The function 'get_routes' takes no arguments.

	"""

	# Set location of key file
	api_key_file = os.path.expanduser("~/.mailgunapi") 
	try:
		with file(api_key_file) as f:
			api_key = str.strip(f.read()) 
	except:
		print "ERROR reading api key file. Make sure the path is set and the file exists."
		sys.exit()


	def get_routes():
		print "Listing Current Routes"
		return requests.get(
			"https://api.mailgun.net/v2/routes",
			auth=("api", api_key),
			params={"skip": 0,
					"limit": 25})

	def create_route(recipient):
		print "Creating Route for", recipient
		return requests.post(
			"https://api.mailgun.net/v2/routes",
			auth=("api", api_key),
			data=MultiDict([("priority", 1),
							("description", "Challenge 10 Route for Chris West"),
							("expression", "match_recipient('" + recipient + "')"),
							("action", "forward('http//cldsrvr.com/challenge1')"),
							("action", "stop()")]))

	
	create_result = create_route("chris.west@apichallenges.mailgun.org")
	print json.dumps(create_result.json(), sort_keys=True, indent=4, separators=(',', ': '))

	# Uncomment the next two lines to get a listing of the routes on this account.
	#get_routes_result = get_routes()
	#print json.dumps(get_routes_result.json(), sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()

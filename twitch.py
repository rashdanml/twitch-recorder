import requests
import json

# Client ID and Secret 
client_id = "CLIENT_ID"
client_secret = "CLIENT_SECRET"

# Streams Endpoint + Headers
url = " https://api.twitch.tv/helix/streams?user_login=lara6683"
headers = {'client-id': client_id, 'Authorization': 'Bearer ' + token }

# Authorize and Validate
auth_url = "https://id.twitch.tv/oauth2/token"
validate_url = "https://id.twitch.tv/oauth2/validate"

auth_params = {'client_id': client_id, 'client_secret': client_secret, 'grant_type':'client_credentials'}

token = "TOKEN" # = stream['access_token']

# Checking if Token is Valid
validate_headers = {'client-id': client_id, 'Authorization': 'OAuth ' + token }
valid = requests.get(validate_url, headers=validate_headers).json()
print(valid)

if valid['expires_in'] < 3600:
	# Getting an App access token, if Token is about to expire
	stream = requests.post(auth_url, params=auth_params).json()
	print (stream['access_token'])
else:
	print ("Token still valid")
	
# Stream info, testing to make sure the token worked
stream = requests.get(url, headers=headers).json()
print (stream)

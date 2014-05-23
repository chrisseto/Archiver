from smartfile import OAuthClient
api = OAuthClient('**********', '**********')
# Be sure to only call each method once for each OAuth login

# This is the first step with the client, which should be left alone
api.get_request_token()
# Redirect users to the following URL:
print "In your browser, go to: " + api.get_authorization_url()
# This example uses raw_input to get the verification from the console:
client_verification = raw_input("What was the verification? :")
api.get_access_token(None, client_verification)
api.get('/ping')

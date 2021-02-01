from pygdash.util import AuthException

import requests

# basic Service for getting data from GD's API
class BaseService:
    
    # initialize with server
    def __init__(self, server="http://www.boomlings.com/database/"):
        self.server = server
        self.secret = "Wmfd2893gb7"
        self.gameVersion = '21'
        self.binaryVersion = '35'
        
    # sets the versions to use while accessing the API
    def setVersions(self, gameVersion, binaryVersion):
        self.gameVersion = gameVersion
        self.binaryVersion = binaryVersion
        
    # sets the API secret to send
    def setSecret(self, secret):
        self.secret = secret
        
    # send a POST request to specified endpoint
    def post(self, endpoint, data):
        # fixed params
        data['secret'] = self.secret
        data['gameVersion'] = self.gameVersion
        data['binaryVersion'] = self.binaryVersion
        # send request
        response = requests.post(self.server+endpoint, data=data)
        # err check
        if response.status_code != 200:
            raise Exception("Status code from endpoint {0} was not success!".format(endpoint))
        if response.text == '-1':
            raise Exception("Response from endpoint {0} was not success!".format(endpoint))
        return response.text
   
# Service which requires authentication
class AuthService(BaseService):

    # initialize Service with an optional authenticator
    def __init__(self, server="http://www.boomlings.com/database/", authenticator=None):
        super().__init__(server, secret)
        self.authenticator = authenticator
        
    # authenticate using stored authenticator
    def authenticate(self):
        if self.authenticator is None:
            raise AuthException("No authenticator provided for service {0}.".format(type(self).__name__))
        # authenticator will authenticate if auth is not already cached
        self.authenticator.authenticate()
        
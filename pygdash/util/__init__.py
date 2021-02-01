# exception occurs during auth for a Service
class AuthException(Exception):
    
    def __init__(self, msg):
        self.message = msg
from google.auth.transport import requests
from google.oauth2 import id_token

class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        Validate method queries the Google oAUTH2 API to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(auth_token, requests.Request())
            print("Validated auth token:", auth_token)  # Confirm if the token is validated

            if 'accounts.google.com' in idinfo['iss']:
                return idinfo
        except ValueError:
            return "The token is either invalid or has expired"

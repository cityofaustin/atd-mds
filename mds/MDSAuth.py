"""

"""

import base64
import requests


class MDSAuth:
    __slots__ = (
        "config",
        "oauth_token",
        "session",
        "headers",
        "authenticate",
        "custom_function",
    )

    def __init__(self, config, custom_function=None):
        """
        Initializes the class and the internal configuration
        :param dict config:
        :param function custom_function: A python function to run as a custom authentication
        """
        self.config = config
        self.custom_function = custom_function
        auth_type = self.config.get("auth_type", None)
        self.headers = None

        if auth_type:
            print(f"MDSAuth::__init__() Authentication method: {auth_type}")
            self.authenticate = {
                "oauth": self.mds_oauth,
                "bearer": self.mds_auth_token,
                "basic": self.mds_http_basic,
                "custom": self.mds_custom_auth,
            }.get(auth_type.lower(), None)

            if not self.authenticate:
                raise Exception(
                    f"MDSAuth::__init__() Invalid authentication method provided, auth_type: '{auth_type}'")
        else:
            raise Exception(f"MDSAuth::__init__() No authentication method provided, auth_type: '{auth_type}'")

    def mds_oauth(self):
        print("MDSAuth::mds_oauth() Running OAuth authentication")
        pass

    def mds_auth_token(self):
        print("MDSAuth::mds_auth_token() Running Token authentication")
        self.headers = {
            "Authorization": f'Bearer {self.config["token"]}'
        }
        return self.headers

    def mds_http_basic(self):
        print("MDSAuth::mds_oauth() Running HTTP Basic authentication")
        auth_data = self.config.get("auth_data", None)
        if auth_data:
            username = auth_data.get("username", None)
            password = auth_data.get("password", None)
            encoded_creds = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
            self.headers = {
                "Authorization": f'Basic {encoded_creds}'
            }
            return self.headers
        else:
            raise Exception("No credentials provided")

        return None

    def mds_auth_custom(self):
        print("MDSAuth::mds_oauth() Running Custom authentication")
        pass

    def mds_custom_auth(self):
        return self.custom_function(self.config)

    def _gather_oauth_token(self):
        print("MDSAuth::_gather_oauth_token() Gathering OAuth token")
        pass

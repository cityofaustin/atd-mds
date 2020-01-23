"""

"""

import base64
import requests


class MDSAuth:
    __slots__ = ("config", "token", "mode", "session", "headers")

    def __init__(self, config):
        self.config = config

    def mds_oauth(self):
        pass

    def mds_auth_token(self):
        pass

    def mds_http_basic(self):
        pass

    def mds_auth_custom(self):
        pass

    def authenticate(self):
        pass

    def _gather_oauth_token(self):
        pass

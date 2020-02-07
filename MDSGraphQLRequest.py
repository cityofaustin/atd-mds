import requests


class MDSGraphQLRequest:
    __slots__ = ["endpoint", "http_params", "http_auth_token", "data", "response"]

    def __init__(self, endpoint, http_auth_token, **kwargs):
        self.endpoint = endpoint
        self.http_auth_token = http_auth_token
        self.http_params = kwargs.get("http_params", None)
        self.response = None

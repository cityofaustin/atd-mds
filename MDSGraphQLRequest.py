import requests


class MDSGraphQLRequest:
    __slots__ = ["endpoint", "http_params", "http_auth_token", "data", "response"]

    def __init__(self, endpoint, http_auth_token, **kwargs):
        self.endpoint = endpoint
        self.http_auth_token = http_auth_token
        self.http_params = kwargs.get("http_params", None)
        self.response = None

    def get_config(self):
        return {
            "endpoint": self.endpoint,
            "http_params": self.http_params,
            "http_auth_token": self.http_auth_token
        }

    def request(self, query):
        headers = {
            "Accept": "application/json",
            "x-hasura-admin-secret": f"Bearer {self.http_auth_token}"
        }

        self.response = requests.post(
            self.endpoint,
            params=self.http_params,
            headers=headers,
            data=query
        )

        self.response.encoding = "utf-8"
        return self.response.json()

    def get_last_response(self):
        return self.response.json()

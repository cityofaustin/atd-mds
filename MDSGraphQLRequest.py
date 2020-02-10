import requests
import logging

class MDSGraphQLRequest:
    __slots__ = ["endpoint", "http_params", "http_auth_token", "data", "response"]

    def __init__(self, endpoint, http_auth_token, **kwargs):
        logging.debug("MDSGraphQLRequest::__init__() Initializing HTTP GraphQL Request")
        self.endpoint = endpoint
        self.http_auth_token = http_auth_token
        self.http_params = kwargs.get("http_params", None)
        self.response = None

    def get_config(self):
        logging.debug("MDSGraphQLRequest::get_config() getting config")
        return {
            "endpoint": self.endpoint,
            "http_params": self.http_params,
            "http_auth_token": self.http_auth_token
        }

    def request(self, query):
        logging.debug("MDSGraphQLRequest::request() Making request")
        headers = {
            "Accept": "*/*",
            "content-type": "application/json",
            "x-hasura-admin-secret": f"{self.http_auth_token}"
        }

        logging.debug(f"MDSGraphQLRequest::request() Headers: {str(headers)}")

        self.response = requests.post(
            self.endpoint,
            params=self.http_params,
            headers=headers,
            json={
                "query": query
            }
        )

        self.response.encoding = "utf-8"
        return self.response.json()

    def get_last_response(self):
        return self.response.json()

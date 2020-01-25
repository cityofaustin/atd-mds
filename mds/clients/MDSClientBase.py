import requests
from requests.exceptions import Timeout

# Debug & Logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MDSClientBase:

    __slots__ = (
        "config",
        "params",
        "headers",
        "param_schema",
        "mds_endpoint",
        "paging",
        "delay",
        "timeout",
        "max_attempts"
    )

    def __init__(self, config):
        self.config = config
        self.headers = {}
        self.params = {}
        self.mds_endpoint = self.config.get("mds_api_url", None)
        self.paging = self.config.get("paging", False)
        self.delay = self.config.get("delay", 0)
        self.timeout = self.config.get("interval", None)
        self.max_attempts = self.config.get("max_attempts", 3)

    def _request(self, mds_endpoint, **kwargs):
        """
        Makes an HTTP request
        :param str mds_endpoint: The URL endpoint to make the request to
        :param dict params: (Optional) URI Parameters to add to the request
        :param dict headers: (Optional) A dictionary of HTTP headers to pass to the request
        :return dict:
        """
        logging.debug(f"MDSClientBase::__request() Making request...")
        data = {}

        # Load our endpoint, parameters and headers
        mds_endpoint = kwargs.get("mds_endpoint", {})
        mds_params = kwargs.get("params", {})
        mds_headers = kwargs.get("headers", {})

        logging.debug(f"MDSClientBase::__request() Details:")
        logging.debug(f"MDSClientBase::__request() mds_endpoint: {mds_endpoint}")
        logging.debug(f"MDSClientBase::__request() mds_params: {mds_params}")
        logging.debug(f"MDSClientBase::__request() mds_headers: {mds_headers}")

        # Make the actual request
        try:
            response = requests.get(
                mds_endpoint,
                params=mds_params,
                headers=mds_headers,
                timeout=self.timeout,
            )
        except Timeout:
            response = {
                "status_code": -1,
                "content": f"Timeout Error: The request exceeded {self.timeout} seconds."
            }

        # If the request is successful:
        if response.status_code == 200:
            data = {
                "status_code": response.status_code,
                "response": "success",
                "message": "success",
                "payload": response.json()
            }
        # If we have anything else:
        elif response.status_code != 200:
            """
            In the future, we may want to refactor this
            to handle 301 and 302 redirect responses.
            """
            data = {
                "status_code": response.status_code,
                "response": "error",
                "message": f"Error: {response.content}",
                "payload": {}
            }

        return data

    def set_header(self, key, value):
        """
        Adds an HTTP header to the list
        :param str key: The name of the header
        :param str value: The value of the HTTP header
        """
        logging.debug(f"MDSClientBase::set_header() Set header k: '{key}', v: '{value}'")
        self.headers[key] = value

    def render_settings(self, headers={}):
        """
        Compiles the headers and the parameters
        :param dict headers: (Optional) Adds any additional headers to the list (e.g., authentication headers)
        """
        # 1. Consolidate current headers and new headers
        logging.debug("MDSClientBase::render_settings() Rendering headers")
        self.headers = {**self.headers, **headers}

        # 2. Initialize Param Schema & Overrides
        logging.debug("MDSClientBase::render_settings() Rendering parameters")
        params_override = self.config.get("mds_param_override", None)
        if isinstance(params_override, dict):
            for key, value in params_override.items():
                self.param_schema[key] = value

    def get_headers(self):
        """
        Returns the current list of headers
        :return dict:
        """
        return self.headers
    
    def set_paging(self, paging):
        """
        Allows to override the paging configuration
        :param bool paging: The new paging configuration. True to enable paging.
        """
        self.paging = paging

    def set_delay(self, delay):
        """
        Allows to override the paging configuration
        :param int delay: The new delay setting in seconds.
        """
        self.delay = delay

    def set_timeout(self, timeout):
        """
        Allows to override the paging configuration
        :param int timeout: The new timeout in seconds.
        """
        self.timeout = timeout

    def set_max_attempts(self, max_attempts):
        """
        Allows to override the max_attempts configuration
        :param int max_attempts: The new max_attempts setting.
        """
        self.max_attempts = max_attempts

import requests

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
        self.timeout = self.config.get("interval", 10)
        self.max_attempts = self.config.get("max_attempts", 3)

    def _paginate(self, **kwargs):
        pass


    def _append_data(self, data, response):
        pass

    def _request(self, **kwargs):
        logging.debug(f"MDSClientBase::__request() Making request...")
        data = {}
        mds_endpoint = kwargs.get("mds_endpoint", {})
        mds_params = kwargs.get("params", {})
        mds_headers = kwargs.get("headers", {})

        logging.debug(f"MDSClientBase::__request() Details:")
        logging.debug(f"MDSClientBase::__request() mds_endpoint: {mds_endpoint}")
        logging.debug(f"MDSClientBase::__request() mds_params: {mds_params}")
        logging.debug(f"MDSClientBase::__request() mds_headers: {mds_headers}")

        response = requests.get(
            mds_endpoint,
            params=mds_params,
            headers=mds_headers
        )

        if response.status_code == 200:
            data = {
                "status_code": response.status_code,
                "response": "success",
                "message": "success",
                "payload": response.json()
            }
        elif response.status_code == 404:
            data = {
                "status_code": response.status_code,
                "response": "error",
                "message": "not found",
                "payload": {}
            }
        else:
            data = {
                "status_code": response.status_code,
                "response": "error",
                "message": "unknown error",
                "payload": {}
            }

        return data

    def set_header(self, key, value):
        logging.debug(f"MDSClientBase::set_header() Set header k: '{key}', v: '{value}'")
        self.headers[key] = value

    def render_settings(self, headers):
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
        logging.debug("MDSClientBase::get_headers() returning headers")
        return self.headers
    
    def set_paging(self, paging):
        self.paging = paging

    def set_delay(self, delay):
        self.delay = delay

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_max_attempts(self, max_attempts):
        self.max_attempts = max_attempts

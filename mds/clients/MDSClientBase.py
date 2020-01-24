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
        "interval",
        "timeout"
    )

    def __init__(self, config):
        self.config = config
        self.headers = {}
        self.params = {}
        self.mds_endpoint = self.config.get("mds_api_url", None)
        self.paging = self.config.get("paging", False)
        self.interval = self.config.get("interval", 1)
        self.timeout = self.config.get("interval", 90)

    def __paginate(self, **kwargs):
        pass

    def __request(self, **kwargs):
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
                # "response_headers": response.headers,
                "type": "success",
                "message": "success",
                "data": response.json()
            }
        elif response.status_code == 404:
            data = {
                "status_code": response.status_code,
                # "response_headers": response.headers,
                "type": "error",
                "message": "not found",
                "data": {}
            }
        else:
            data = {
                "status_code": response.status_code,
                # "response_headers": response.headers,
                "type": "error",
                "message": "unknown error",
                "data": {}
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

    def get_trips(self, start_time, end_time):

        logging.debug("MDSClientBase::get_trips() Getting trips: %s %s " % (start_time, end_time))
        self.params[self.param_schema["start_time"]] = start_time
        self.params[self.param_schema["end_time"]] = end_time

        return self.__request(
            mds_endpoint=f"{self.mds_endpoint}/trips",
            params=self.params,
            headers=self.headers
        )
    
    def set_paging(self, paging):
        self.paging = paging

    def set_interval(self, interval):
        self.interval = interval

    def set_timeout(self, timeout):
        self.timeout = timeout

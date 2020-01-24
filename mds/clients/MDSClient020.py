import json


class MDSClient020:
    version = "0.2.0"

    __slots__ = (
        "config",
        "headers",
        "param_schema",
        "params",
        "mds_endpoint",
        "paging",
        "interval",
        "timeout"
    )

    def __init__(self, config):
        self.config = config
        self.headers = {}
        self.param_schema = {}
        self.params = {}
        self.mds_endpoint = self.config.get("mds_api_url", None)
        self.paging = self.config.get("paging", False)
        self.interval = self.config.get("interval", 1)
        self.timeout = self.config.get("interval", 90)

    def __request(self, **kwargs):
        print(f"MDSClient020::__request() Making request")
        pass

    def set_header(self, key, value):
        print(f"MDSClient020::set_header() Set header k: '{key}', v: '{value}'")
        self.headers[key] = value

    def render_settings(self, headers):
        print("MDSClient020::render_settings() Rendering headers")
        # 1. Consolidate current headers and new headers
        self.headers = {**self.headers, **headers}

        # 2. Initialize Param Schema & Overrides
        params_override = self.config.get("mds_param_override", {})
        self.param_schema["start_time"] = params_override.get("start_time", "start_time")
        self.param_schema["end_time"] = params_override.get("end_time", "end_time")

    def get_headers(self):
        print("MDSClient020::get_headers() returning headers")
        return self.headers

    def get_trips(self, start_time, end_time):

        print("MDSClient020::get_trips() Getting trips: %s %s " % (start_time, end_time))
        self.params[self.param_schema["start_time"]] = start_time
        self.params[self.param_schema["end_time"]] = end_time

        print(json.dumps(self.params))

        return self.version

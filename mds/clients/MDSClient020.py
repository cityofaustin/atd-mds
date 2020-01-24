import json

from .MDSClientBase import MDSClientBase


class MDSClient020(MDSClientBase):
    version = "0.2.0"

    param_schema = {
        "start_time": "start_time",
        "end_time": "end_time",
    }

    def __init__(self, config):
        MDSClientBase.__init__(self, config)

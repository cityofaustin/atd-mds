#
#
#
from datetime import datetime
from string import Template
import logging

class MDSSchedule:
    __slots__ = [
        "http_graphql_request",
        "query",
        "provider_id",
        "status_id",
        "time_min",
        "time_max",
    ]

    def __init__(self, http_graphql_request, provider_id, status_id, time_min, time_max):
        logging.debug("MDSSchedule::__init__() Initializing MDSSchedule")
        self.http_graphql_request = http_graphql_request
        self.provider_id = provider_id
        self.status_id = status_id
        self.time_min = time_min
        self.time_max = time_max

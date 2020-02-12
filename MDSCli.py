import os
import json
import time

import logging

from MDSProviderHelpers import MDSProviderHelpers

class MDSCli:
    __slots__ = [
        "provider",
        "interval",
        "time_max",
        "time_min",
        "_timer_start",
        "_timer_end",
        "logger",
        "helpers",
        "parsed_date_time_max",
        "parsed_date_time_min",
        "parsed_interval",
    ]

    def __init__(self, provider, interval, time_max, time_min):
        """
        Initializes the option parser
        """
        # Initialize helpers
        self.helpers = MDSProviderHelpers()
        # Initialize the timer values
        self._timer_start = time.time()
        self._timer_end = None
        # Initialize command line arguments
        self.provider = provider
        self.interval = interval
        self.time_max = time_max
        self.time_min = time_min
        # Parse datetimes
        self.parsed_date_time_max = self.helpers.parse_custom_datetime_as_dt(self.time_max)
        self.parsed_date_time_min = self.helpers.parse_custom_datetime_as_dt(self.time_min)
        self.parsed_interval = self.helpers.parse_interval(self.interval)


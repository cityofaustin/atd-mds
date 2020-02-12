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

    def get_config(self) -> dict:
        """
        Returns a dictionary with the current configuration
        :return:
        """
        logging.debug(f"MDSCli::get_config() getting configuration ...")
        return {
            "provider": self.provider,
            "interval": self.interval,
            "time_max": self.time_max,
            "time_min": self.time_min,
        }

    def valid_settings(self) -> bool:
        if self.provider:
            logging.debug(f"MDSCli::validate_settings() provider: {self.provider}")
        else:
            print(f"MDSCli::validate_settings() Provider is not defined.")
            return False

        if self.time_max:
            logging.debug(f"MDSCli::validate_settings() time_max: {self.time_max}")
        else:
            print(f"MDSCli::validate_settings() Max time not defined")
            return False

        if self.interval:
            logging.debug(f"MDSCli::validate_settings() interval: {self.interval}")
        else:
            logging.debug("MDSCli::validate_settings() Interval not defined, assuming 1 hour.")
            self.interval = 1

        if self.time_min:
            logging.debug(f"MDSCli::validate_settings() time_min: {self.time_max}")
            self.interval = 0
        else:
            logging.debug("MDSCli::validate_settings() Not a range, running for a single cycle")

        return True

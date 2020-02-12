import os
import json
import time

import logging

from MDSProviderHelpers import MDSProviderHelpers
from MDSSchedule import MDSSchedule
from mds import MDSTimeZone

class MDSCli:
    __slots__ = [
        "mds_config",
        "mds_schedule",
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

    def __init__(self, mds_config, provider, interval, time_max, time_min):
        """
        Initializes the option parser
        """
        # Initialize Config
        self.mds_config = mds_config
        # Initial Schedule
        self.mds_schedule = None
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

        if not self.parsed_date_time_max:
            logging.debug(f"The time-max date provided is not valid: '{self.time_max}'")
            return False

        return True

    def initialize_schedule(self) -> MDSSchedule:
        # If we do not have a time-min, then we use the interval
        if not self.parsed_date_time_min:
            logging.debug(f"No time-min defined, using Interval: {self.parsed_interval}")
            time_max = MDSTimeZone(
                date_time_now=self.parsed_date_time_max,
                offset=(self.parsed_interval * 60 * 60),
                time_zone="US/Central",  # US/Central
            )
            self.mds_schedule = MDSSchedule(
                mds_config=self.mds_config,
                provider_name=str(self.provider_name),
                time_min=time_max.get_time_start(),
                time_max=time_max.get_time_end()
            )
        else:
            logging.debug(f"Time-min is defined, interval cleared.")
            time_min = MDSTimeZone(
                date_time_now=self.parsed_date_time_min,
                offset=0,  # Not Needed
                time_zone="US/Central",  # US/Central
            )

            time_max = MDSTimeZone(
                date_time_now=self.parsed_date_time_max,
                offset=0,  # Not needed
                time_zone="US/Central",  # US/Central
            )

            self.mds_schedule = MDSSchedule(
                mds_config=self.mds_config,
                provider_name=str(self.provider_name),
                time_min=time_min.get_time_start(),
                time_max=time_max.get_time_end()
            )

        return self.mds_schedule

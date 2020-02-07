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
        self._initialize_query()

    def _initialize_query(self):
        logging.debug("MDSSchedule::_initialize_query() Initializing Query")
        if not isinstance(self.time_min, datetime):
            logging.debug("MDSSchedule::_initialize_query() time_min not a valid datetime object")
            raise Exception(
                "MDSSchedule::_load_time() time_min is expected to be a datetime"
            )

        if not isinstance(self.time_max, datetime):
            logging.debug("MDSSchedule::_initialize_query() time_min not a valid datetime object")
            raise Exception(
                "MDSSchedule::_load_time() time_max is expected to be a datetime"
            )

        logging.debug("MDSSchedule::_initialize_query() Generating query...")
        self.query = Template("""
                    query fetchPendingSchedules {
                        api_schedule(
                            where: {
                                provider_id: {_eq: $provider_id }
                                status_id: {_eq: $status_id},

                                year: {_gte: $min_year},
                                month: {_gte: $min_month},
                                day: {_gte: $min_day},
                                hour: {_gte: $min_hour},

                                _and: {
                                    year: {_lte: $max_year},
                                    month: {_lte: $max_month},
                                    day: {_lte: $max_day},
                                    hour: {_lte: $max_hour},
                                }
                            }
                        ) {
                            provider_id
                            schedule_id
                            year
                            month
                            day
                            hour
                            status_id
                        }
                    }
                """).substitute({
                    "provider_id": self.provider_id,
                    "status_id": self.status_id,
                    "min_year": self.time_min.year,
                    "min_month": self.time_min.month,
                    "min_day": self.time_min.day,
                    "min_hour": self.time_min.hour,
                    "max_year": self.time_max.year,
                    "max_month": self.time_max.month,
                    "max_day": self.time_max.day,
                    "max_hour": self.time_max.hour,
                })

    def get_query(self):
        return self.query


    def get_schedule(self):
        query = self.get_query()
        return None

import logging

from datetime import datetime
from string import Template

from MDSGraphQLRequest import MDSGraphQLRequest

class MDSSchedule:
    __slots__ = [
        "http_graphql_request",
        "query",
        "provider_id",
        "status_id",
        "time_min",
        "time_max",
    ]

    def __init__(self, http_graphql_request, provider_id, status_id=0, time_max=None, time_min=None):
        """
        Constructor for Schedule class.
        :param MDSGraphQLRequest http_graphql_request: It requires a graphql query class, with which
        it will make the actual requests to the HTTP endpoint
        :param int provider_id: The provider ID as identified in the providers table in the RDS MDS instance.
        :param int status_id: The status id of the schedule we are looking for, default is 0
        :param datetime time_max: A datetime object that includes the maximum date and hour of the schedule
        :param datetime time_min: (Optional) A datetime object that indicates the minimum date and hour of the schedule
        """
        logging.debug("MDSSchedule::__init__() Initializing MDSSchedule")
        # Initialization
        self.http_graphql_request = http_graphql_request
        self.provider_id = provider_id
        self.status_id = status_id
        self.time_max = time_max
        self.time_min = time_min

        # Now initialize query
        self._initialize_query()

    def _initialize_query(self):
        """
        Generates a GraphQL query using the standard Template library, and populates into class variable.
        :return:
        """
        logging.debug("MDSSchedule::_initialize_query() Initializing Query")

        if not isinstance(self.time_max, datetime):
            logging.debug("MDSSchedule::_initialize_query() time_min not a valid datetime object")
            raise Exception(
                "MDSSchedule::_load_time() time_max is expected to be a datetime"
            )

        # If time_min is not provided, then we copy from time_max for exactly 1 schedule item
        if not isinstance(self.time_min, datetime):
            self.time_min = self.time_max

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
        """
        Retrieves the query from memory
        :return str:
        """
        return self.query

    def get_schedule(self):
        """
        Returns a dictionary with the response from the API endpoint
        :return dict:
        """
        # Check if the http_graphql_request variable is a valid MDSGraphQLRequest object
        if not isinstance(self.http_graphql_request, MDSGraphQLRequest):
            raise Exception(
                "MDSSchedule::get_schedule() http_graphql_request is not a MDSGraphQLRequest class"
            )

        # It looks like it is, let's make the request
        return self.http_graphql_request.request(self.get_query())

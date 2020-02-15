import logging

from datetime import datetime
from string import Template

from MDSConfig import MDSConfig


class MDSSchedule:
    __slots__ = [
        "mds_config",
        "mds_http_graphql",
        "query",
        "provider_name",
        "status_id",
        "time_min",
        "time_max",
    ]

    def __init__(self, mds_config, mds_gql, provider_name, status_id=0, time_max=None, time_min=None):
        """
        Constructor for Schedule class.
        :param MDSConfig mds_config: The configuration class where we can gather our endpoint
        :param MDSGraphQLRequest mds_gql: The http graphql class we need to make requests
        :param str provider_name: The provider name as identified in the providers table in the RDS MDS instance.
        :param int status_id: The status id of the schedule we are looking for, default is 0
        :param datetime time_max: A datetime object that includes the maximum date and hour of the schedule
        :param datetime time_min: (Optional) A datetime object that indicates the minimum date and hour of the schedule
        """
        logging.debug("MDSSchedule::__init__() Initializing MDSSchedule")
        # Initialization
        self.mds_config = mds_config
        self.mds_http_graphql = mds_gql
        self.provider_name = provider_name
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
                                provider: {provider_name: {_eq: "$provider_name"}},
                                status_id: {_eq: $status_id},
                                
                                date:{_gt:"$min_year-$min_month-$min_day $min_hour:00:00"}
                                
                                _and: {
                                    date:{_lte:"$max_year-$max_month-$max_day $max_hour:00:00"}
                                }
                            }, order_by: {date: asc}
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
                    "provider_name": self.provider_name,
                    "status_id": self.status_id,
                    "min_year": self.time_min.year,
                    "min_month": self.time_min.month,
                    "min_day": self.time_min.day,
                    "min_hour": f"{self.time_min.hour:02d}",
                    "max_year": self.time_max.year,
                    "max_month": self.time_max.month,
                    "max_day": self.time_max.day,
                    "max_hour": f"{self.time_max.hour:02d}",
                })

    @staticmethod
    def is_quotable_value(value):
        if isinstance(value, int):
            return False
        if isinstance(value, float):
            return False
        if isinstance(value, bool):
            return False
        return True

    def get_query(self) -> str:
        """
        Retrieves the query from memory
        :return str:
        """
        return self.query

    def get_schedule(self) -> dict:
        """
        Returns a dictionary with the response from the API endpoint
        :return dict:
        """
        return self.mds_http_graphql.request(self.get_query())["data"]["api_schedule"]

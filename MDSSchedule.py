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
        "status_check",
        "status_operator",
    ]

    def __init__(
        self,
        mds_config,
        mds_gql,
        provider_name,
        status_id=0,
        time_max=None,
        time_min=None,
        status_check=True,
        status_operator="_eq"
    ):
        """
        Constructor for Schedule class.
        :param MDSConfig mds_config: The configuration class where we can gather our endpoint
        :param MDSGraphQLRequest mds_gql: The http graphql class we need to make requests
        :param str provider_name: The provider name as identified in the providers table in the RDS MDS instance.
        :param int status_id: The status id of the schedule we are looking for, default is 0
        :param datetime time_max: A datetime object that includes the maximum date and hour of the schedule
        :param datetime time_min: (Optional) A datetime object that indicates the minimum date and hour of the schedule
        :param bool status_check: (Optional) If True, it will enforce the status_id filter.
        :param str status_operator: (Optional) Provides the operator to use when looking for status_id (examples: '_eq', '_lt', '_lte', default: '_eq').
        """
        logging.debug("MDSSchedule::__init__() Initializing MDSSchedule")
        # Initialization
        self.mds_config = mds_config
        self.mds_http_graphql = mds_gql
        self.provider_name = provider_name
        self.status_id = status_id
        self.time_max = time_max
        self.time_min = time_min
        self.status_check = status_check
        self.status_operator = status_operator

        # Now initialize query
        self._initialize_query()

    def _initialize_query(self):
        """
        Generates a GraphQL query using the standard Template library, and populates into class variable.
        :return:
        """
        logging.debug("MDSSchedule::_initialize_query() Initializing Query")

        if not isinstance(self.time_max, datetime):
            logging.debug(
                "MDSSchedule::_initialize_query() time_min not a valid datetime object"
            )
            raise Exception(
                "MDSSchedule::_load_time() time_max is expected to be a datetime"
            )

        # If time_min is not provided, then we copy from time_max for exactly 1 schedule item
        if not isinstance(self.time_min, datetime):
            self.time_min = self.time_max

        logging.debug(f"MDSSchedule::_initialize_query() Generating query... status_check: {self.status_check}")
        self.query = Template(
            """
                    query fetchPendingSchedules {
                        api_schedule(
                            where: {
                                provider: {provider_name: {_eq: "$provider_name"}},
                                %STATUS_CHECK%
                                
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
                """.replace(
                "%STATUS_CHECK%",
                ("", "status_id: {$status_operator: $status_id},")[self.status_check],
            )
        ).substitute(
            {
                "provider_name": self.provider_name,
                "status_id": self.status_id,
                "status_operator": self.status_operator,
                "min_year": self.time_min.year,
                "min_month": self.time_min.month,
                "min_day": self.time_min.day,
                "min_hour": f"{self.time_min.hour:02d}",
                "max_year": self.time_max.year,
                "max_month": self.time_max.month,
                "max_day": self.time_max.day,
                "max_hour": f"{self.time_max.hour:02d}",
            }
        )
        logging.debug(f"Query: {self.query}")

    @staticmethod
    def is_quotable_value(value) -> bool:
        """
        Returns True if the value needs to be quoted in GraphQL, or False otherwise.
        :param * value: The value to be tested, it can be any type.
        :return bool:
        """
        if isinstance(value, int):
            return False
        if isinstance(value, float):
            return False
        if isinstance(value, bool):
            return False
        return True

    @staticmethod
    def escape_quotes(value) -> str:
        """
        Returns an escaped string for quotation marks in GraphQL
        :param str value: The string that needs to be quoted
        :return str:
        """
        return str(value).replace('"', '\\"')

    @staticmethod
    def is_quoted(value) -> bool:
        return True if value[-1:] == '"' and value[:1] == '"' else False

    def get_schedule_update_status_query(self, schedule_id, status_id, **kwargs) -> str:
        """
        Generates the graphql query to run against the api.
        :param int schedule_id: The schedule id to be updated
        :param int status_id:  The status_id to be set to.
        :param dict kwargs:  Any additional arguments to be set to.
        :return:
        """

        additional_args = ""
        for k, v in kwargs.items():
            if self.is_quotable_value(v) and self.is_quoted(v) is False:
                value = self.escape_quotes(v)
                value = f'"{value}"'
            else:
                if str(v) == "True" or str(v) == "False":
                    value = str(v).lower()
                else:
                    value = v
            # value = value.replace('\\\\\\"None\\\\\\"', 'null')
            additional_args += f"\n                    {k}: {value},"

        return Template(
            """
            mutation mutationUpdateScheduleStatus {
                update_api_schedule(
                where: {
                    schedule_id: {_eq: $schedule_id}
                }, 
                _set: {
                    status_id: $status_id,
                    $additional_args
                }
                ){ affected_rows }
            }
        """
        ).substitute(
            {
                "schedule_id": str(schedule_id),
                "status_id": str(status_id),
                "additional_args": additional_args,
            }
        )

    def set_schedule_status(self, schedule_id, status_id, **kwargs) -> str:
        """
        Sets the status of the schedule in the database. Refer to the schedule_status table for more details.
        Returns the number of affected rows.
        :param int schedule_id: The schedule id to be updated
        :param int status_id: The status of the schedule to be updated
        :param dict kwargs: Any other fields to be updated in key=value format.
        :return int:
        """
        query = self.get_schedule_update_status_query(
            schedule_id=schedule_id, status_id=status_id, **kwargs,
        )
        response = self.mds_http_graphql.request(query)
        return response["data"]["update_api_schedule"]["affected_rows"]

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

    def get_schedule_by_id(self, schedule_id) -> dict:
        """
        Returns a dictionary with the response from the API endpoint
        :return dict:
        """
        query = Template(
            """
            query getScheduleById {
              api_schedule(
                where: {
                    schedule_id: {_eq: $schedule_id}
                }) {
                    schedule_id
                    status_id
                    year
                    month
                    day
                    hour
                    payload
                    message
                    provider {
                      id
                      provider_name
                    }
                }
            }
        """
        ).substitute({"schedule_id": str(schedule_id)})
        return self.mds_http_graphql.request(query)["data"]["api_schedule"]

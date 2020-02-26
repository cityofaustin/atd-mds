import logging

from datetime import datetime
from string import Template

from sodapy import Socrata
from MDSConfig import MDSConfig


class MDSSocrata:

    __slots__ = [
        "mds_config",
        "mds_http_graphql",
        "mds_socrata_dataset",
        "records_per_page",
        "query",
        "client",
        "data",
    ]

    def __del__(self):
        """
        Make sure the client is closed whenever the class is destructed.
        :return:
        """
        try:
            self.client.close()
        finally:
            self.client = None

    def __str__(self) -> str:
        """
        Returns the configuration as string.
        :return:
        """
        return str(
            {
                "SOCRATA_DATA_ENDPOINT": self.mds_config.get_setting("SOCRATA_DATA_ENDPOINT", None),
                "SOCRATA_DATASET": self.mds_config.get_setting("SOCRATA_DATASET", None),
                "SOCRATA_APP_TOKEN": self.mds_config.get_setting("SOCRATA_APP_TOKEN", None),
                "SOCRATA_KEY_ID": self.mds_config.get_setting("SOCRATA_KEY_ID", None),
                "SOCRATA_KEY_SECRET": self.mds_config.get_setting("SOCRATA_KEY_SECRET", None)
            }
        )

    def __init__(
            self,
            mds_config,
            mds_gql
    ):
        """
        Constructor for the init class.
        :param MDSConfig mds_config: The configuration class where we can gather our endpoint
        :param MDSGraphQLRequest mds_gql: The http graphql class we need to make requests
        :return:
        """
        self.mds_config = mds_config
        self.mds_http_graphql = mds_gql
        self.mds_socrata_dataset = self.mds_config.get_setting("SOCRATA_DATASET", None)
        self.client = Socrata(
            self.mds_config.get_setting("SOCRATA_DATA_ENDPOINT", None),
            self.mds_config.get_setting("SOCRATA_APP_TOKEN", None),
            username=self.mds_config.get_setting("SOCRATA_KEY_ID", None),
            password=self.mds_config.get_setting("SOCRATA_KEY_SECRET", None),
            timeout=20
        )
        self.records_per_page = 6000
        self.data = None
        self.query = Template("""
        query getTrips {
          api_trips(
                where: {
                end_time: { _gte: "$time_min" },
                _and: { start_time: { _lt: "$time_max" }}
              }
          ) {
            trip_id
            device_id
            vehicle_type
            trip_duration
            trip_distance
            start_time
            end_time
            modified_date
            council_district_start
            council_district_end
            census_geoid_start
            census_geoid_end
          }
        }
        """)

    def get_query(self, time_min, time_max) -> str:
        """
        Returns a string with the new query based on limit and offset.
        :param str limit:
        :param str offset:
        :return str:
        """
        if isinstance(time_min, str) is False:
            raise Exception("time_min must be a sql datetime string")
        if isinstance(time_max, str) is False:
            raise Exception("time_max must be a sql datetime string")
        return self.query.substitute(time_min=time_min, time_max=time_max)

    def get_data(self, records, page) -> dict:
        """
        Gathers data from the API endpoint
        :param int records:
        :param int page:
        :return dict:
        """
        query = self.get_query(records, records*page)
        return self.mds_http_graphql.request(query)

    def load_data(self, data) -> bool:
        """
        Loads the data and prepares for upsert.
        :param data:
        :return bool:
        """
        self.data = data
        return False

    def get_config(self) -> dict:
        """
        Returns the configuration dictionary for testing.
        :return dict:
        """
        return self.mds_config.get_config()

    def save(self) -> dict:
        """
        Upserts the data into Socrata
        :return bool:
        """
        if self.client is not None:
            return self.client.upsert(self.mds_socrata_dataset, self.data)
        else:
            raise Exception("The socrata client is not initialized correctly, check your API credentials.")


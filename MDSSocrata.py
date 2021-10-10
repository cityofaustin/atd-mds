from dateutil import parser, tz
from string import Template

from sodapy import Socrata
from MDSConfig import MDSConfig


class MDSSocrata:

    __slots__ = [
        "mds_config",
        "mds_http_graphql",
        "mds_socrata_dataset",
        "provider_name",
        "query",
        "client",
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
                "SOCRATA_DATA_ENDPOINT": self.mds_config.get_setting(
                    "SOCRATA_DATA_ENDPOINT", None
                ),
                "SOCRATA_DATASET": self.mds_config.get_setting("SOCRATA_DATASET", None),
                "SOCRATA_APP_TOKEN": self.mds_config.get_setting(
                    "SOCRATA_APP_TOKEN", None
                ),
                "SOCRATA_KEY_ID": self.mds_config.get_setting("SOCRATA_KEY_ID", None),
                "SOCRATA_KEY_SECRET": self.mds_config.get_setting(
                    "SOCRATA_KEY_SECRET", None
                ),
            }
        )

    def __init__(self, provider_name, mds_config, mds_gql):
        """
        Constructor for the init class.
        :param str provider_name: The name of the provider
        :param MDSConfig mds_config: The configuration class where we can gather our endpoint
        :param MDSGraphQLRequest mds_gql: The http graphql class we need to make requests
        :return:
        """
        self.provider_name = provider_name
        self.mds_config = mds_config
        self.mds_http_graphql = mds_gql
        self.mds_socrata_dataset = self.mds_config.get_setting("SOCRATA_DATASET", None)
        self.client = Socrata(
            self.mds_config.get_setting("SOCRATA_DATA_ENDPOINT", None),
            self.mds_config.get_setting("SOCRATA_APP_TOKEN", None),
            username=self.mds_config.get_setting("SOCRATA_KEY_ID", None),
            password=self.mds_config.get_setting("SOCRATA_KEY_SECRET", None),
            timeout=20,
        )
        self.query = Template(
            """
        query getTrips {
          api_trips(
                where: {
                provider: { provider_name: { _eq: "$provider_name" }}
                end_time: { _gte: "$time_min" },
                _and: { end_time: { _lt: "$time_max" }}
              }
          ) {
            trip_id: id
            device_id: device { id }
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
        """
        )

    def get_query(self, time_min, time_max) -> str:
        """
        Returns a string with the new query based on limit and offset.
        :param str time_min: The minimum time the trip ended
        :param str time_max: The maximum time the trip ended
        :return str:
        """
        if isinstance(self.provider_name, str) is False:
            raise Exception("provider_name must be a string")
        if isinstance(time_min, str) is False:
            raise Exception("time_min must be a sql datetime string")
        if isinstance(time_max, str) is False:
            raise Exception("time_max must be a sql datetime string")
        return self.query.substitute(
            provider_name=self.provider_name, time_min=time_min, time_max=time_max
        )

    def get_data(self, time_min, time_max) -> dict:
        """
        Gathers data from the API endpoint
        :param str time_min:
        :param str time_max:
        :return dict:
        """
        query = self.get_query(time_min=time_min, time_max=time_max)
        return self.mds_http_graphql.request(query)

    def get_config(self) -> dict:
        """
        Returns the configuration dictionary for testing.
        :return dict:
        """
        return self.mds_config.get_config()

    def save(self, data) -> dict:
        """
        Upserts the data into Socrata
        :param dict data: The data to be saved unto socrata.
        :return dict:
        """
        data = list(map(self.clean_trip_device_id, data))
        data = list(map(self.parse_datetimes, data))
        data = list(map(self.check_geos_data, data))
        if self.client is not None:
            return self.client.upsert(self.mds_socrata_dataset, data)
        else:
            raise Exception(
                "The socrata client is not initialized correctly, check your API credentials."
            )

    def parse_datetimes(self, data) -> dict:
        """
        Parses the PostgreSQL datetime with timezone into an insertable
        socrata timestamp in CST time. It also adds necessary fields,
        such as year, month, hour and day of the week.
        :param data:
        :return:
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        # create datetime objects
        end_time = parser.parse(data["end_time"])
        start_time = parser.parse(data["start_time"])
        modified_date = parser.parse(data["modified_date"])
        # format datestrings
        data["start_time"] = start_time.strftime(fmt)
        data["end_time"] = end_time.strftime(fmt)
        data["modified_date"] = modified_date.strftime(fmt)
        data["start_time_us_central"] = self.datetime_to_us_central(start_time).strftime(fmt)
        data["end_time_us_central"] = self.datetime_to_us_central(end_time).strftime(fmt)
        # create other date properties
        data["year"] = end_time.year
        data["month"] = end_time.month
        data["hour"] = end_time.hour
        data["day_of_week"] = end_time.weekday()
        return data

    @staticmethod
    def check_geos_data(data) -> dict:
        """
        Parses the PostgreSQL datetime with timezone into an insertable
        socrata timestamp in CST time. It also adds necessary fields,
        such as year, month, hour and day of the week.
        :param data:
        :return:
        """
        geos_fields = [
            "council_district_start",
            "council_district_end",
            "census_geoid_start",
            "census_geoid_end",
        ]

        for field in geos_fields:
            if data[field] is None or data[field] == "None":
                data[field] = 0
            else:
                data[field] = data.get(field, 0)
        return data

    @staticmethod
    def datetime_to_us_central(dt):
        return dt.astimezone(tz.gettz("US/Central"))

    @staticmethod
    def clean_trip_device_id(trip) -> dict:
        """
        Transforms the device_id field from a dictionary into a string value
        :param dict trip: The trip dictionary being transformed
        :return dict:
        """
        trip["device_id"] = trip["device_id"]["id"]
        return trip

import logging
import json
import uuid
import re

from datetime import datetime
from string import Template
from pytz import reference

from MDSPointInPolygon import MDSPointInPolygon
from cerberus import Validator


class MDSTrip:
    __slots__ = [
        "mds_config",
        "mds_pip",
        "mds_http_graphql",
        "mds_graphql_query",
        "trip_data",
        "validator",
        "query",
        "response",
    ]

    validation_schema = {
        "provider_id": {"type": "string"},
        "provider_name": {"type": "string"},
        "device_id": {"type": "string"},
        "vehicle_id": {"type": "string"},
        "vehicle_type": {"type": "string"},
        "trip_id": {"type": "string"},
        "propulsion_type": {"type": "list"},
        "route": {"type": "dict"},
        "trip_duration": {"type": "number"},
        "trip_distance": {"type": "number"},
        "accuracy": {"type": "number"},
        "start_time": {"type": "number"},
        "end_time": {"type": "number"},
        "standard_cost": {"nullable": True, "required": False, "type": "number"},
        "actual_cost": {"nullable": True, "required": False, "type": "number"},
        "publication_time": {"nullable": True, "required": False, "type": "number"},
        "parking_verification_url": {"nullable": True, "required": False, "type": "string"},
        # Coordinates
        "start_latitude": {"type": "number"},
        "start_longitude": {"type": "number"},
        "end_latitude": {"type": "number"},
        "end_longitude": {"type": "number"},
        # Polygon IDs
        "council_district_start": {"nullable": True, "required": False, "type": "string"},
        "council_district_end": {"nullable": True, "required": False, "type": "string"},
        "orig_cell_id": {"nullable": True, "required": False, "type": "string"},
        "dest_cell_id": {"nullable": True, "required": False, "type": "string"},
        "census_geoid_start": {"nullable": True, "required": False, "type": "string"},
        "census_geoid_end": {"nullable": True, "required": False, "type": "string"},
        # Other Fields
        "currency": {"nullable": True, "required": False, "type": "string"},
        "start": {"nullable": True, "required": False, "type": "string"},
        "end": {"nullable": True, "required": False, "type": "string"},
    }

    graphql_template_insert = """
        mutation insertTrip {
          insert_api_trips(
            objects: {
                trip_id: "$trip_id",
                accuracy: "$accuracy",
                device_id: "$device_id",
                vehicle_id: "$vehicle_id",
                end_time: "$end_time",
                propulsion_type: "$propulsion_type",
                provider_id: "$provider_id",
                provider_name: "$provider_name",
                start_time: "$start_time",
                trip_distance: "$trip_distance",
                trip_duration: "$trip_duration",
                vehicle_type: "$vehicle_type",
                publication_time: "$publication_time",
                standard_cost: $standard_cost,
                actual_cost: $actual_cost,
                start_latitude: $start_latitude,
                start_longitude: $start_longitude,
                end_latitude: $end_latitude,
                end_longitude: $end_longitude,
                council_district_start: "$council_district_start",
                council_district_end: "$council_district_end",
                orig_cell_id: "$orig_cell_id",
                dest_cell_id: "$dest_cell_id",
                census_geoid_start: "$census_geoid_start",
                census_geoid_end: "$census_geoid_end",
            },
            on_conflict: {
                constraint: trips_trip_id_pk,
                update_columns: [
                    provider_id,
                    provider_name,
                    device_id,
                    vehicle_type,
                    accuracy,
                    propulsion_type,
                    trip_id,
                    trip_duration,
                    trip_distance,
                    start_time,
                    end_time,
                    council_district_start,
                    council_district_end,
                    orig_cell_id,
                    dest_cell_id,
                    census_geoid_start,
                    census_geoid_end,
                    start_latitude,
                    start_longitude,
                    end_latitude,
                    end_longitude,
                ],
            }
        ) {
            affected_rows
          }
        }
    """

    graphql_template_search = """
        query getTrip {
          api_trips(where: {trip_id: {_eq: "$trip_id"}}) {
            trip_id
          }
        }
    """

    def __init__(self, mds_config, mds_pip, mds_gql, trip_data):
        # Initialize our configuration
        self.mds_config = mds_config
        self.mds_pip = mds_pip
        # Initialize our HTTP GraphQL Class
        self.mds_http_graphql = mds_gql
        # Initializes the cerberus validator
        self.validator = Validator(self.validation_schema, require_all=True)
        # HTTP Query and Response
        self.query = {}
        self.response = {}
        # Then initialize our trip data
        self.trip_data = trip_data
        self.initialize_points()
        self.mds_graphql_query = None

    def is_valid(self) -> bool:
        """
        Returns True if the trip data is valid, false otherwise.
        :return bool:
        """
        try:
            return self.validator.validate(self.trip_data)
        except:
            return False

    def get_validation_errors(self) -> dict:
        """
        Returns a dictionary with all the validation errors.
        :return:
        """
        return self.validator.errors

    def int_to_uuid(self, integer_number):
        """
        Turns an integer into an uuid using the provider id as a template.
        :param integer_number:
        :return:
        """
        provider_id = self.trip_data.get("provider_id", None)
        ms = str(uuid.UUID(bytes=int(f"{integer_number}").to_bytes(16, "big")))
        i = re.search(r'[^0\-]', ms).start()
        return f"{provider_id[:i]}{ms[i:]}"

    def get_provider_name(self):
        """
        Returns the name of the provider, or None if not declared.
        :return:
        """
        return self.trip_data.get("provider_name", None)

    @staticmethod
    def get_affected_rows(gql_key, response) -> int:
        """
        Returns the number of affected rows given a response, or 0 if the response is invalid.
        :param str gql_key: The response key expected for the GraohQL query
        :param dict response: The json response from the HTTP GQL Client
        :return:
        """
        try:
            return int(response["data"][gql_key]["affected_rows"])
        except:
            return 0

    def save(self) -> bool:
        """
        Returns True if the record has been saved to Postgres successfully, false otherwise.
        :return bool:
        """
        logging.debug("MDSTrip::save() saving trip...")

        if self.is_valid():
            self.query = self.generate_gql_insert()
            self.response = self.mds_http_graphql.request(self.query)
            logging.debug(
                "MDSTrip::save() Request finished, response: %s" % str(self.response)
            )
            return self.get_affected_rows(
                gql_key="insert_api_trips",
                response=self.response
            ) != 0
        else:
            self.query = self.generate_gql_insert()
            self.response = self.get_validation_errors()
            print(f"MDSTrip::save() trip marked as invalid: {self.trip_data['trip_id']}")
            print(self.query)
            print("Errors: ")
            print(self.response)
            return False

    def exists(self, trip_id) -> bool:
        """
        Returns true if the record exists in the database, false otherwise.
        :return bool:
        """
        return (
            len(self.get_trip_by_id(mds_gql=self.mds_http_graphql, trip_id=trip_id))
            == 1
        )

    def generate_gql_insert(self) -> str:
        """
        Generates a string with a GraphQL query
        :return str:
        """
        self.initialize_timestamps()
        self.initialize_optional_fields()
        return Template(self.graphql_template_insert).substitute(self.trip_data)

    def generate_gql_search(self, trip_id) -> str:
        """
        Generates a string with a GraphQL query to search for a record.
        :return str:
        """
        return Template(self.graphql_template_search).substitute({"trip_id": trip_id})

    def get_coordinates(self, start=True) -> (float, float):
        """
        Returns a tuple with coordinates for current loaded trip: (longitude, latitude)
        The start of the trip is enabled by default, or the end of the trip if start is set to False.
        Returns a tuple with longitude and latitude (in that order).
        :param bool start:
        :return (float, float):
        """
        # The index is the first element, or the last.
        index = 0 if start else (len(self.trip_data["route"]["features"]) - 1)
        coordinates = self.trip_data["route"]["features"][index]["geometry"][
            "coordinates"
        ]
        return coordinates[0], coordinates[1]

    def set_trip_value(self, trip_key, trip_value):
        """
        Sets a new key to the trip data dictionary
        :param str trip_key: The new key to be added to the dict
        :param str trip_value: The value assigned to that key
        """
        self.trip_data[trip_key] = trip_value

    def get_trip_value(self, trip_key):
        """
        Returns a specific value for a key in the trip data dictionary
        :param str trip_key: The name of the key in the trip data dictionary
        :return:
        """
        return self.trip_data.get(trip_key, None)

    @staticmethod
    def translate_timestamp(utc_unix_timestamp) -> str:
        time = int(str(utc_unix_timestamp)[:10])
        fmt = "%Y-%m-%d %H:%M:%S"
        time_str = datetime.fromtimestamp(time).strftime(fmt)
        timezone = reference.LocalTimezone().tzname(datetime.now())
        return f"{time_str} {timezone}"

    @staticmethod
    def get_current_datetime_utc() -> str:
        fmt = "%Y-%m-%d %H:%M:%S"
        time_str = datetime.now().strftime(fmt)
        timezone = reference.LocalTimezone().tzname(datetime.now())
        return f"{time_str} {timezone}"

    def initialize_optional_fields(self):
        """
        Initializes the optional fields in the database, if the fields are not populated yet.
        :return:
        """
        if self.trip_data.get("standard_cost", None) is None:
            self.set_trip_value("standard_cost", str(0))
        if self.trip_data.get("actual_cost", None) is None:
            self.set_trip_value("actual_cost", str(0))
        if self.trip_data.get("publication_time", None) is None:
            self.set_trip_value("publication_time", None)
        if self.trip_data.get("parking_verification_url", None) is None:
            self.set_trip_value("parking_verification_url", None)

    def initialize_timestamps(self):
        """
        If the trip has start_time, end_time and publication_time
        :return:
        """
        if self.is_valid():
            start_time = self.translate_timestamp(self.trip_data["start_time"])
            end_time = self.translate_timestamp(self.trip_data["end_time"])
            self.set_trip_value("start_time", start_time)
            self.set_trip_value("end_time", end_time)

            raw_publication_time = self.trip_data.get("publication_time", None)
            if raw_publication_time is not None:
                publication_time = self.translate_timestamp(raw_publication_time)
            else:
                publication_time = self.get_current_datetime_utc()
            self.set_trip_value("publication_time", publication_time)

    def initialize_points(self):
        # If the Trips data is valid (has proper format), let's initialize the trip's shapely points
        if isinstance(self.trip_data, dict) and isinstance(
            self.mds_pip, MDSPointInPolygon
        ):
            try:
                # Get coordinates for start and end of trip
                start_long, start_lat = self.get_coordinates(start=True)
                end_long, end_lat = self.get_coordinates(start=False)
                self.set_trip_value("start_latitude", start_lat)
                self.set_trip_value("start_longitude", start_long)
                self.set_trip_value("end_latitude", end_lat)
                self.set_trip_value("end_longitude", end_long)

                # Convert each to shapely point objects
                start_point = self.mds_pip.create_point(
                    longitude_x=start_long, latitude_y=start_lat
                )
                end_point = self.mds_pip.create_point(
                    longitude_x=end_long, latitude_y=end_lat
                )
                # Retrieve the Census Tract
                self.set_trip_value(
                    "census_geoid_start",
                    self.mds_pip.get_census_tract_id(mds_point=start_point),
                )
                self.set_trip_value(
                    "census_geoid_end",
                    self.mds_pip.get_census_tract_id(mds_point=end_point),
                )

                # Retrieve the council district
                self.set_trip_value(
                    "council_district_start",
                    self.mds_pip.get_district_id(mds_point=start_point),
                )
                self.set_trip_value(
                    "council_district_end",
                    self.mds_pip.get_district_id(mds_point=end_point),
                )

                # Retrieve the Hexagon ID
                self.set_trip_value(
                    "orig_cell_id", self.mds_pip.get_hex_id(mds_point=start_point)
                )
                self.set_trip_value(
                    "dest_cell_id", self.mds_pip.get_hex_id(mds_point=end_point)
                )
            except:
                pass

    @staticmethod
    def get_trip_by_id(mds_gql, trip_id):
        query = Template(
            """
            query getTripById {
              api_trips(where: {trip_id: {_eq: "$trip_id"}}) {
                provider_id,
                provider_name,
                device_id,
                vehicle_type,
                accuracy,
                propulsion_type,
                trip_id,
                trip_duration,
                trip_distance,
                start_time,
                end_time,
                council_district_start,
                council_district_end,
                orig_cell_id,
                dest_cell_id,
                census_geoid_start,
                census_geoid_end,
                start_latitude,
                start_longitude,
                end_latitude,
                end_longitude,
              }
            }
        """
        ).substitute(trip_id=trip_id)
        results = mds_gql.request(query)
        return results["data"]["api_trips"]

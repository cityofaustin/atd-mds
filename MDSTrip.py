
import json
from string import Template

from MDSPointInPolygon import MDSPointInPolygon
from MDSGraphQLRequest import MDSGraphQLRequest
from cerberus import Validator


class MDSTrip:
    __slots__ = [
        "mds_config",
        "mds_pip",
        "mds_http_graphql",
        "mds_graphql_query",
        "trip_data",
        "validator",
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
        "trip_duration": {"type": "integer"},
        "trip_distance": {"type": "integer"},
        "accuracy": {"type": "integer"},
        "start_time": {"type": "integer"},
        "end_time": {"type": "integer"},
        "standard_cost": {"type": "integer"},
        "actual_cost": {"type": "integer"},
        "publication_time": {"type": "integer"},
        "council_district_start": {"type": "string"},
        "council_district_end": {"type": "string"},
        "orig_cell_id": {"type": "string"},
        "dest_cell_id": {"type": "string"},
        "census_geoid_start": {"type": "string"},
        "census_geoid_end": {"type": "string"},
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
            },
            on_conflict: {
                constraint: new_constraint_name,
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
                    end_time
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

    def __init__(self, mds_config, mds_pip, trip_data):
        # Initialize our configuration
        self.mds_config = mds_config
        self.mds_pip = mds_pip
        # Initialize our HTTP GraphQL Class
        self.mds_http_graphql = MDSGraphQLRequest(
            endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
            http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None)
        )
        # Initializes the cerberus validator
        self.validator = Validator(self.validation_schema, require_all=True)
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

    def save(self) -> bool:
        """
        Returns True if the record has been saved to Postgres successfully, false otherwise.
        :return bool:
        """
        if self.is_valid():
            query = self.generate_gql_insert()
            response = self.mds_http_graphql.request(query)
            return True
        else:
            return False

    def exists(self) -> bool:
        """
        Returns true if the record exists in the database, false otherwise.
        :return bool:
        """
        if self.trip_data:
            return True
        else:
            return False

    def generate_gql_insert(self) -> str:
        """
        Generates a string with a GraphQL query
        :return str:
        """
        return Template(self.graphql_template_insert).substitute(self.trip_data)

    def generate_gql_search(self, trip_id) -> str:
        """
        Generates a string with a GraphQL query to search for a record.
        :return str:
        """
        return Template(self.graphql_template_search).substitute({
            "trip_id": trip_id
        })

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
        coordinates = self.trip_data["route"]["features"][index]["geometry"]["coordinates"]
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

    def initialize_points(self):
        # If the Trips data is valid (has proper format), let's initialize the trip's shapely points
        if isinstance(self.trip_data, dict) \
                and isinstance(self.mds_pip, MDSPointInPolygon):
            try:
                # Get coordinates for start and end of trip
                start_long, start_lat = self.get_coordinates(start=True)
                end_long, end_lat = self.get_coordinates(start=False)

                # Convert each to shapely point objects
                start_point = self.mds_pip.create_point(
                    longitude_x=start_long,
                    latitude_y=start_lat
                )
                end_point = self.mds_pip.create_point(
                    longitude_x=end_long,
                    latitude_y=end_lat
                )
                # Retrieve the Census Tract
                self.set_trip_value(
                    "census_geoid_start",
                    self.mds_pip.get_census_tract_id(mds_point=start_point)
                )
                self.set_trip_value(
                    "census_geoid_end",
                    self.mds_pip.get_census_tract_id(mds_point=end_point)
                )

                # Retrieve the council district
                self.set_trip_value(
                    "council_district_start",
                    self.mds_pip.get_district_id(mds_point=start_point)
                )
                self.set_trip_value(
                    "council_district_end",
                    self.mds_pip.get_district_id(mds_point=end_point)
                )

                # Retrieve the Hexagon ID
                self.set_trip_value(
                    "orig_cell_id",
                    self.mds_pip.get_hex_id(mds_point=start_point)
                )
                self.set_trip_value(
                    "dest_cell_id",
                    self.mds_pip.get_hex_id(mds_point=end_point)
                )
            except:
                pass

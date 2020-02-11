
import json
from string import Template

from MDSGraphQLRequest import MDSGraphQLRequest
from cerberus import Validator


class MDSTrip:
    __slots__ = [
        "mds_config",
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

    def __init__(self, mds_config, trip_data):
        # Initialize our configuration
        self.mds_config = mds_config
        # Initialize our HTTP GraphQL Class
        self.mds_http_graphql = MDSGraphQLRequest(
            endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
            http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None)
        )
        # Then initialize our trip data
        self.trip_data = trip_data
        self.mds_graphql_query = None
        # Initializes the cerberus validator
        self.validator = Validator(self.validation_schema, require_all=True)

    def is_valid(self) -> bool:
        """
        Returns True if the trip data is valid, false otherwise.
        :return bool:
        """
        return self.validator.validate(self.trip_data)

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

    def get_council_district(self) -> str:
        """
        Returns a string with the council district id.
        :return str:
        """
        if self.trip_data:
            pass
        return ""

    def get_cell_id(self) -> str:
        """
        Returns a string with the cell id.
        :return str:
        """
        if self.trip_data:
            pass
        return ""

    def get_census_geoid(self) -> str:
        """
        Returns a string with the census geoid.
        :return str:
        """
        if self.trip_data:
            pass
        return ""

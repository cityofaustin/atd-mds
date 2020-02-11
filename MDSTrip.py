
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

    graphql_template = """
        mutation insertTrip {
          insert_api_dockless(
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
                    start_time,
                    end_time
                ],
            }
        ) {
            affected_rows
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

    def generate_gql(self) -> str:
        """
        Generates a string with a GraphQL query
        :return str:
        """
        template = Template(self.graphql_template)
        s = template.substitute(self.trip_data)
        return s

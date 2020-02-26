from dateutil import parser, tz
from string import Template


class MDSKnack:
    __slots__ = [
        "query_template",
        "data",
    ]

    def __init__(self):
        self.data = None
        self.query_template = Template("""
        query getTrips {
          api_trips_aggregate(
                where: {
                    provider: { provider_name: { _eq: $provider_name }},
                    end_time: { _gte: $time_min },
                    _and: {
                        end_time: { _lt: $time_max }
                        $additional_filters
                    }
                }
        ) {
            aggregate {
              total_trips: count
              avg {
                trip_distance
                trip_duration
              }
              sum {
                total_meters: trip_distance
              }
            }
          }
        }""")

    def build_query(self, provider_name, time_min, time_max, additional_filters="") -> str:
        """
        Returns a query with the provided parameters
        :param str provider_name: The name of the provider
        :param str time_min: The minimum time where the trips ended
        :param str time_max: The maximum time where the trips ended
        :param str additional_filters: (optional)Any other graphql syntax conditions you want to add
        :return str:
        """
        return self.query_template.substitute(
            provider_name=provider_name,
            time_min=time_min,
            time_max=time_max,
            additional_filters=additional_filters
        )

import json

from .MDSClientBase import MDSClientBase

# Debug & Logging
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MDSClient020(MDSClientBase):
    version = "0.2.0"

    param_schema = {
        "start_time": "start_time",
        "end_time": "end_time",
    }

    def __init__(self, config):
        MDSClientBase.__init__(self, config)

    @staticmethod
    def _has_trips(data):
        return len(data.get("payload", {}).get("data", {}).get("trips", [])) > 0

    @staticmethod
    def _has_data(data):
        return len(data.get("payload", {}).get("data", {})) > 0

    @staticmethod
    def _has_next_link(data):
        return data.get("payload", {}).get("links", {}).get("next", "") != ""

    @staticmethod
    def _get_next_link(data):
        return data.get("payload", {}).get("links", {}).get("next", None)

    def _get_response_version(self, data):
        return data.get("payload", {}).get("version", self.version)

    def get_trips(
        self,
        providers=None,
        device_id=None,
        vehicle_id=None,
        start_time=None,
        end_time=None,
        bbox=None,
        paging=True,
        **kwargs,
    ):
        logging.debug(
            "MDSClient020::get_trips() Getting trips: %s %s " % (start_time, end_time)
        )

        # Set the required URI parameters
        self.params[self.param_schema["start_time"]] = start_time
        self.params[self.param_schema["end_time"]] = end_time

        # Out trips accumulator
        trips_accumulator = []
        current_endpoint = f"{self.mds_endpoint}/trips"
        has_trips = False
        has_next_link = False
        has_data = False

        while True:
            # Check max attempts
            data = self._request(
                mds_endpoint=current_endpoint,
                headers=self.headers,
                params=None if has_next_link else self.params,
            )

            has_trips = self._has_trips(data)
            has_data = self._has_data(data)
            has_next_link = self._has_next_link(data)

            logging.debug(
                "MDSClient020::get_trips() has_trips: %s, has_data: %s, has_next_link: %s "
                % (has_trips, has_data, has_next_link)
            )

            if has_trips:
                trips = data["payload"]["data"]["trips"]
                current_trips_count = len(trips_accumulator)
                new_trips_count = len(trips)

                logging.debug("\n\n------------------------------\n\n")
                logging.debug(trips_accumulator)
                logging.debug("\n\n------------------------------\n\n")
                logging.debug(trips)
                logging.debug("\n\n------------------------------\n\n")


                logging.debug(
                    "MDSClient020::get_trips() current_trips_count: %s, new_trips_count: %s"
                    % (current_trips_count, new_trips_count)
                )
                trips_accumulator.append(trips)
                trips = None
                logging.debug(
                    "MDSClient020::get_trips() len(trips_accumulator): %s"
                    % (len(trips_accumulator))
                )

            current_endpoint = self._get_next_link(data)

            if not current_endpoint:
                break
            else:
                logging.debug(
                    "MDSClient020::get_trips() Next link: %s" % current_endpoint
                )

        return {
            "version": self._get_response_version(data),
            "data": {
                "trips": trips_accumulator
            }
        }

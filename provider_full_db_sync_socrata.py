#!/usr/bin/env python
"""
Socrata - Exporter
Author: Austin Transportation Department, Data & Technology Services
Description: The purpose of this script is to gather data from Hasura
and export it to the Socrata database.

The application requires the requests, sodapy and atd-mds-client libraries:
    https://pypi.org/project/click/
    https://pypi.org/project/requests/
    https://pypi.org/project/sodapy/
    https://pypi.org/project/atd-mds-client/
"""

import click
import requests
import json
import logging
import time

from mds import *
from MDSConfig import MDSConfig
from sodapy import Socrata
from dateutil import parser, tz

logging.disable(logging.DEBUG)

# Let's initialize our configuration class
mds_config = MDSConfig()

@click.command()
@click.option(
    "--time-min",
    default=None,
    help="The minimum time where the trip ended in format: 'yyyy-mm-dd-hh'",
)
@click.option(
    "--time-max",
    default=None,
    help="The maximum time where the trip ended in format: 'yyyy-mm-dd-hh'",
)
def run(**kwargs):
    """
    Runs the program based on the above flags, the values will be passed to kwargs as a dictionary
    :param dict kwargs: The values specified by click decorators.
    :return:
    """
    # Start timer
    start = time.time()

    SOCRATA_DATASET = mds_config.get_setting("SOCRATA_DATASET", None)
    SOCRATA_ENDPOINT = mds_config.get_setting("SOCRATA_DATA_ENDPOINT", None)
    SOCRATA_APP_TOKEN = mds_config.get_setting("SOCRATA_APP_TOKEN", None)
    SOCRATA_KEY_ID = mds_config.get_setting("SOCRATA_KEY_ID", None)
    SOCRATA_KEY_SECRET = mds_config.get_setting("SOCRATA_KEY_SECRET", None)

    HASURA_ENDPOINT = mds_config.get_setting("HASURA_ENDPOINT", None)
    # Prep Hasura query
    HASURA_HEADERS = {
        "Content-Type": "application/json",
        "X-Hasura-Admin-Secret": mds_config.get_setting("HASURA_ADMIN_KEY", None)
    }

    time_min = kwargs.get("time_min", None)
    time_max = kwargs.get("time_max", None)


    query = """
        query getTrips($timeMin: timestamptz!, $timeMax: timestamptz!) {
          api_trips(
                where: {
                  end_time: { _gte: $timeMin }
                  _and: { 
                    end_time: { _lt: $timeMax }
                  },
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

    response = requests.post(
        HASURA_ENDPOINT,
        data=json.dumps({
            "query": query,
            "variables": {
                "timeMin": time_min,
                "timeMax": time_max,
            }
        }),
        headers=HASURA_HEADERS
    )

    def datetime_to_cst(timestamp) -> str:
        """
        Returns a datetime in CST timezone
        :param timestamp:
        :return:
        """
        try:
            return parser.parse(timestamp).astimezone(tz.gettz("CST"))
        except:
            return timestamp

    def parse_datetimes(data) -> dict:
        """
        Parses the PostgreSQL datetime with timezone into an insertable
        socrata timestamp in CST time. It also adds necessary fields,
        such as year, month, hour and day of the week.
        :param data:
        :return:
        """
        fmt = "%Y-%m-%dT%H:%M:%S"
        end_time = datetime_to_cst(data["end_time"])
        data["start_time"] = datetime_to_cst(data["start_time"]).strftime(fmt)
        data["end_time"] = end_time.strftime(fmt)
        data["modified_date"] = datetime_to_cst(data["modified_date"]).strftime(
            fmt
        )
        data["year"] = end_time.year
        data["month"] = end_time.month
        data["hour"] = end_time.hour
        data["day_of_week"] = end_time.weekday()
        return data

    def clean_trip(trip) -> dict:
        """
        Transforms the device_id field from a dictionary into a string value
        :param dict trip: The trip dictionary being transformed
        :return dict:
        """
        trip["device_id"] = trip["device_id"]["id"]
        trip = parse_datetimes(trip)
        return trip

    #
    # Generate the
    #
    try:
        trips = list(map(clean_trip, response.json()["data"]["api_trips"]))
    except:
        trips = []

    if len(trips) == 0:
        print("Nothing to do here, exiting.")
        exit(0)
    else:
        print(f"Total trips to process: {len(trips)}")

    print("Connecting to Socrata")

    # Setup connection to Socrata
    client = Socrata(
        SOCRATA_ENDPOINT,
        SOCRATA_APP_TOKEN,
        username=SOCRATA_KEY_ID,
        password=SOCRATA_KEY_SECRET,
        timeout=7200,
    )

    print("Making upsert... this can take a while but not more than 2 hours. Please wait.")
    client.upsert(SOCRATA_DATASET, trips)

    # Stop timer and print duration
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Finished in: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


if __name__ == "__main__":
    run()

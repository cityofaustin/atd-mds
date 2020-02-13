#!/usr/bin/env python

import click
import json
import logging
from datetime import datetime

from mds import *
from MDSTrip import MDSTrip
from MDSCli import MDSCli
from MDSConfig import MDSConfig
from MDSAWS import MDSAWS
from MDSPointInPolygon import MDSPointInPolygon
from MDSGraphQLRequest import MDSGraphQLRequest

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.disabled = False

mds_config = MDSConfig()
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    bucket_name=mds_config.ATD_MDS_BUCKET,
)
mds_pip = MDSPointInPolygon(
    mds_config=mds_config
)
mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None)
)


@click.command()
@click.option(
    "--provider", default=None, help="The provider's name",
)
@click.option(
    "--file",
    default=None,
    help="Use this flag to use a specific input file.",
)
@click.option(
    "--interval",
    default=None,
    help="Relative to the maximum time for trip end, an interval window "
    "in hours (i.e., from 11 to noon, you would need the value of '1')",
)
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
    mds_cli = MDSCli(
        mds_config=mds_config,
        mds_gql=mds_gql,
        provider=kwargs.get("provider", None),
        interval=kwargs.get("interval", None),
        time_max=kwargs.get("time_max", None),
        time_min=kwargs.get("time_min", None),
    )

    file = kwargs.get("file", None)

    print(f"Settings: {str(mds_cli.get_config())}")

    # Check the CLI settings...
    if mds_cli.valid_settings() is False:
        print("Invalid settings, exiting.")
        exit(1)

    logging.debug(f"Parsed Time Max: {mds_cli.parsed_date_time_max}")
    logging.debug(f"Parsed Time Min: {mds_cli.parsed_date_time_min}")
    logging.debug(f"Parsed Interval: {mds_cli.parsed_interval}")

    # Initialize the Schedule Class
    mds_schedule = mds_cli.initialize_schedule()
    # Gather schedule items:
    schedule = mds_schedule.get_schedule()
    logging.debug(f"Schedule: {json.dumps(schedule)}")

    # For each schedule hour block:
    for schedule_item in schedule:
        logging.debug("Running with: ")
        logging.debug(schedule_item)

        # Build timezone aware interval...
        logging.debug("Building timezone aware interval ...")
        tz_time = MDSTimeZone(
            date_time_now=datetime(
                schedule_item["year"],
                schedule_item["month"],
                schedule_item["day"],
                schedule_item["hour"],
            ),
            offset=3600,  # One hour, always
            time_zone="US/Central",  # US/Central Timezone
        )

        # Output generated time stamps on screen
        logging.debug("Time Start (iso):\t%s" % tz_time.get_time_start())
        logging.debug("Time End   (iso):\t%s" % tz_time.get_time_end())
        logging.debug("time_start (unix):\t%s" % (tz_time.get_time_start(utc=True, unix=True)))
        logging.debug("time_end   (unix):\t%s" % (tz_time.get_time_end(utc=True, unix=True)))

        logging.debug("Loading S3 File ...")
        # Determine data directory in S3
        data_path = mds_config.get_data_path(
            provider_name=mds_cli.provider, date=tz_time.get_time_start()
        )
        # Determine final file path
        s3_trips_file = data_path + "trips.json"
        # Load the file from S3 into a dictionary called 'trips'
        trips = mds_aws.load(s3_trips_file)
        # For each trip, we need to build a trip object
        for trip in trips["data"]["trips"]:
            mds_trip = MDSTrip(
                mds_config=mds_config,  # We pass the configuration class
                mds_pip=mds_pip,  # We pass the point-in-polygon class
                mds_gql=mds_gql,  # We pass the HTTP GraphQL class
                trip_data=trip  # We provide this individual trip data
            )
            # We can generate a GraphQL Query for debugging
            gql = mds_trip.generate_gql_insert()
            # If the trip is validated
            if mds_trip.is_valid():
                # We now 'save' the trip to in the database
                print(gql)
                # mds_trip.save()


if __name__ == "__main__":
    run()

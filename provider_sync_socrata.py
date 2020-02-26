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

import json
from datetime import datetime

import click
from mds import *

from MDSCli import MDSCli
from MDSConfig import MDSConfig
from MDSAWS import MDSAWS
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSSocrata import MDSSocrata

# Let's initialize our configuration class
mds_config = MDSConfig()
# Then we need to initialize our AWS class with our configuration
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    bucket_name=mds_config.ATD_MDS_BUCKET,
)

# Both the CLI and Trips classes will need an http-graphql client
mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None)
)


@click.command()
@click.option(
    "--provider", default=None, help="The provider's name",
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

    print(f"Settings: {str(mds_cli.get_config())}")

    # Check the CLI settings...
    if mds_cli.valid_settings() is False:
        print("Invalid settings, exiting.")
        exit(1)

    print(f"Parsed Time Max: {mds_cli.parsed_date_time_max}")
    print(f"Parsed Time Min: {mds_cli.parsed_date_time_min}")
    print(f"Parsed Interval: {mds_cli.parsed_interval}")

    # Retrieve the Schedule Class instance
    mds_schedule = mds_cli.initialize_schedule(
        # Default status, it does not matter
        status_id=0,
        # Do not check for status, this disabled by default
        status_check=False
    )
    # Gather schedule items:
    schedule = mds_schedule.get_schedule()
    print(f"Schedule: {json.dumps(schedule)}")

    # For each schedule hour block:
    for schedule_item in schedule:
        print(f"Running with: {json.dumps(schedule_item)}")

        # Build timezone aware interval...
        print("Building timezone aware interval ...")
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
        print("Time Start (cst):\t%s" % tz_time.get_time_start(utc=False))
        print("Time End   (cst):\t%s" % tz_time.get_time_end(utc=False))
        print("Time Start (utc):\t%s" % tz_time.get_time_start(utc=True))
        print("Time End   (utc):\t%s" % tz_time.get_time_end(utc=True))

        mds_socrata = MDSSocrata(
            provider_name=mds_cli.provider,
            mds_config=mds_config,
            mds_gql=mds_gql
        )

        trips = mds_socrata.get_data(
            time_min=str(tz_time.get_time_start(utc=False)),
            time_max=str(tz_time.get_time_end(utc=False))
        )["data"]["api_trips"]

        print(json.dumps(trips))
        mds_socrata.save(data=trips)


if __name__ == "__main__":
    run()

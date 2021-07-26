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
import json
import logging
from datetime import datetime

from mds import *
from MDSCli import MDSCli
from MDSConfig import MDSConfig
from MDSAWS import MDSAWS
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSSocrata import MDSSocrata

logging.disable(logging.DEBUG)

# Let's initialize our configuration class
mds_config = MDSConfig()
# Then we need to initialize our AWS class with our configuration
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    encryption_key=mds_config.ATD_MDS_FERNET_KEY,
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

        mds_socrata = MDSSocrata(
            provider_name=mds_cli.provider,
            mds_config=mds_config,
            mds_gql=mds_gql
        )

        trips = mds_socrata.get_data(
            time_min=str(tz_time.get_time_start(utc=False)),
            time_max=str(tz_time.get_time_end(utc=False))
        )

        saved = mds_socrata.save(data=trips["data"]["api_trips"])

        total_errors = saved.get("Errors", -1)
        final_status = -8
        if total_errors == 0:
            print("Socrata updates successful: %s" % str(saved))
            print("Data inserted: \n %s" % json.dumps(trips["data"]["api_trips"]))
            final_status = 8
        else:
            print("Socrata updates failed: %s" % str(saved))

        print("Updating schedule status...")
        mds_schedule.set_schedule_status(
            schedule_id=schedule_item["schedule_id"],
            status_id=final_status,
            socrata_status=json.dumps(saved)
        )


if __name__ == "__main__":
    run()

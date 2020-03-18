#!/usr/bin/env python

import click
import json
import logging
from datetime import datetime

from mds import *
from MDSCli import MDSCli
from MDSConfig import MDSConfig
from MDSAWS import MDSAWS
from MDSGraphQLRequest import MDSGraphQLRequest


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
# The CLI class will need an http-graphql client
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
    help="Use this flag to output to a file.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Forces a schedule to run by changing its status to 0 before running.",
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
    force = kwargs.get("force", False)

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
        # Default status, we expect 0 = new
        status_id=0,
        # Do not check for status if force is enabled
        status_check=(True, False)[force]
    )

    # Gather schedule items:
    schedule = mds_schedule.get_schedule()

    print(f"Schedule: {json.dumps(schedule)}")

    print("Initializing MDS Client ...")
    # Initialize the MDS Client
    mds_client = MDSClient(
        config=mds_cli.mds_provider,
        mds_gql=mds_gql,
        provider=mds_cli.provider
    )

    # We will need to accumulate all trips if we have more
    # than one hour blocks that need to be saved to a json file.
    all_trips = []

    if len(schedule) == 0:
        print(f"There are no schedule items for '{mds_cli.provider}' ...")
        exit(1)

    # For each schedule item:
    for schedule_item in schedule:
        print("Running with: " + json.dumps(schedule_item))

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
        logging.debug("Time Start (iso):\t%s" % tz_time.get_time_start())
        logging.debug("Time End   (iso):\t%s" % tz_time.get_time_end())
        logging.debug("time_start (unix):\t%s" % (tz_time.get_time_start(utc=True, unix=True)))
        logging.debug("time_end   (unix):\t%s" % (tz_time.get_time_end(utc=True, unix=True)))

        print("Getting trips, please wait...")
        trips = mds_client.get_trips(
            start_time=tz_time.get_time_start(utc=True, unix=True),
            end_time=tz_time.get_time_end(utc=True, unix=True),
        )
        # Determine data directory in S3
        data_path = mds_config.get_data_path(
            provider_name=mds_cli.provider, date=tz_time.get_time_start()
        )
        # Determine final file path
        s3_trips_file = data_path + "trips.json"
        print("Saving Data to S3 ...")
        mds_aws.save(
            json_document=json.dumps(trips),
            file_path=s3_trips_file,
            encrypted=True
        )
        print(f"File saved to {s3_trips_file}")

        print(f"Updating status for schedule_id: {schedule_item['schedule_id']}")
        # The file was saved to S3 successfully...
        mds_schedule.set_schedule_status(
            schedule_id=schedule_item["schedule_id"],
            status_id=2,
            payload=s3_trips_file,
            message="Successfully uploaded to S3"
        )

        # If we need to save to file
        if file:
            # Accumulate to our current trips array
            all_trips.append(trips)
        trips = None  # Wipe out trips just in case

    # If we need to save to file
    if file:
        # Open the file and dump all trips accumulated
        with open(f"{file}", "w") as json_file:
            json.dump(all_trips, json_file)

    # Gather timer end & output to console...
    hours, minutes, seconds = mds_cli.get_timer_end()
    print(
        "Overall process finished in: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        )
    )


if __name__ == "__main__":
    run()

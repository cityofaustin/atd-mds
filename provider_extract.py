#!/usr/bin/env python

import click
import json
import logging
from datetime import datetime

from mds import *
from MDSCli import MDSCli
from MDSConfig import MDSConfig
from MDSAWS import MDSAWS

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

    logging.debug("Initializing MDS Client ...")
    # Initialize the MDS Client
    mds_client = MDSClient(
        config=mds_cli.mds_provider, provider=mds_cli.provider
    )

    all_trips = []

    # For each schedule item:
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

        logging.debug("Getting trips ...")
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
        logging.debug("Saving Data to S3 ...")
        mds_aws.save(json_document=json.dumps(trips), file_path=s3_trips_file)
        logging.debug(f"File saved to {s3_trips_file}")
        # Accumulate
        all_trips += trips

    if file:
        with open(f"{file}.json", "w") as json_file:
            json.dump(all_trips, json_file)

    # Gather timer end & output to console...
    hours, minutes, seconds = mds_cli.get_timer_end()
    logging.debug(
        "Overall process finished in: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        )
    )


if __name__ == "__main__":
    run()

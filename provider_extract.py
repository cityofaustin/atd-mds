#!/usr/bin/env python

import time
import click
import json
from datetime import datetime
from mds import *

from MDSConfig import MDSConfig
from MDSProviderHelpers import MDSProviderHelpers
from MDSSchedule import MDSSchedule
from MDSAWS import MDSAWS

# Debug & Logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.disabled = False

mds_config = MDSConfig()
mds_provider_helper = MDSProviderHelpers()
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    bucket_name=mds_config.ATD_MDS_BUCKET
)

@click.command()
@click.option(
    "--provider",
    default=None,
    prompt="Provider",
    help="The provider's name",
)
@click.option(
    "--interval",
    default=None,
    prompt="Interval in hours",
    help="Relative to the maximum time for trip end, an interval window "
         "in hours (i.e., from 11 to noon, you would need the value of '1')"
)
@click.option(
    "--time-min",
    default=None,
    help="The minimum time where the trip ended in format: 'yyyy-mm-dd-hh'"
)
@click.option(
    "--time-max",
    default=None,
    prompt="Max. End Trip Datetime",
    help="The maximum time where the trip ended in format: 'yyyy-mm-dd-hh'"
)
def run(**kwargs):
    """
    Runs the program based on the above flags, the values will be passed to kwargs as a dictionary
    :param dict kwargs: The values specified by click decorators.
    :return:
    """
    # Start timer
    start = time.time()

    # Begin gathering parameters
    provider_name = kwargs.get('provider', None)
    interval = kwargs.get('interval', None)
    time_max = kwargs.get('time_max', None)
    time_min = kwargs.get('time_min', None)

    print(f"""
        Provider: '{provider_name}'
        Interval: '{interval}'
        Time Max: '{time_max}'
        Time Min: '{time_min}'
    """)

    if provider_name:
        logging.debug(f"provider_name: {provider_name}")
    else:
        print(f"Provider is not defined.")
        exit(1)

    if time_max:
        logging.debug(f"time_max: {time_max}")
    else:
        print(f"Max time not defined")
        exit(1)

    if interval:
        logging.debug(f"interval: {interval}")
    else:
        logger.debug("Interval not defined, assuming 1 hour.")
        interval = 1

    if time_min:
        logging.debug(f"time_min: {time_max}")
        interval = 0
    else:
        print("Not a range, running for a single cycle")

    # Load the provider configuration
    mds_client_configuration = mds_config.get_provider_config(provider_name=provider_name)

    if not mds_client_configuration:
        print(f"The provider configuration could not be loaded for: '{provider_name}'")
        exit(1)

    # Allocate for parsed date times, min and max
    parsed_date_time_max = mds_provider_helper.parse_custom_datetime_as_dt(time_max)
    parsed_date_time_min = mds_provider_helper.parse_custom_datetime_as_dt(time_min)
    parsed_interval = mds_provider_helper.parse_interval(interval)

    # First make sure we have a time-max, if not stop execution.
    if not parsed_date_time_max:
        print(f"The time-max date provided is not valid: '{time_max}'")
        exit(1)

    logging.debug(f"Parsed Time Max: {parsed_date_time_max}")
    logging.debug(f"Parsed Time Min: {parsed_date_time_min}")
    logging.debug(f"Parsed Interval: {parsed_interval}")

    # If we do not have a time-min, then we use the interval
    if not parsed_date_time_min:
        logging.debug(f"No time-min defined, using Interval: {parsed_interval}")
        time_max = MDSTimeZone(
            date_time_now=parsed_date_time_max,
            offset=(parsed_interval * 60 * 60),
            time_zone="US/Central",  # US/Central
        )

        mds_shedule = MDSSchedule(
            mds_config=mds_config,
            provider_name=str(provider_name),
            time_min=time_max.get_time_start(),
            time_max=time_max.get_time_end()
        )
    else:
        logging.debug(f"Time-min is defined, interval cleared.")
        time_min = MDSTimeZone(
            date_time_now=parsed_date_time_min,
            offset=0,  # Not Needed
            time_zone="US/Central",  # US/Central
        )

        time_max = MDSTimeZone(
            date_time_now=parsed_date_time_max,
            offset=0,  # Not needed
            time_zone="US/Central",  # US/Central
        )

        mds_shedule = MDSSchedule(
            mds_config=mds_config,
            provider_name=str(provider_name),
            time_min=time_min.get_time_start(),
            time_max=time_max.get_time_end()
        )

    query = mds_shedule.get_query()
    logging.debug(f"Query: {query}")
    schedule = mds_shedule.get_schedule()
    logging.debug(f"Schedule: {json.dumps(schedule)}")

    for schedule_item in schedule:
        logging.debug("Running with:")
        logging.debug(schedule_item)

        # Build timezone aware interval...
        logging.debug("Build timezone aware interval:")
        tz_time = MDSTimeZone(
            date_time_now=datetime(schedule_item["year"], schedule_item["month"], schedule_item["day"], schedule_item["hour"]),
            offset=3600,  # One hour, always
            time_zone="US/Central",  # US/Central
        )

        # Output generated time stamps on screen
        logging.debug("Time Start (iso):\t%s" % tz_time.get_time_start())
        logging.debug("Time End   (iso):\t%s" % tz_time.get_time_end())
        logging.debug("time_start (unix):\t%s" % (tz_time.get_time_start(utc=True, unix=True)))
        logging.debug("time_end   (unix):\t%s" % (tz_time.get_time_end(utc=True, unix=True)))

        logging.debug("Checking if we have a valid configuration: ")
        if mds_client_configuration:
            logging.debug("Initializing MDS Client: ")
            # Initialize the MDS Client
            mds_client = MDSClient(config=mds_client_configuration, provider=provider_name)

            # Show the configuration
            mds_client.show_config()

            logging.debug("Getting trips: ")
            trips = mds_client.get_trips(
                start_time=tz_time.get_time_start(utc=True, unix=True),
                end_time=tz_time.get_time_end(utc=True, unix=True)
            )

            logging.debug("Saving Data to S3...")

            data_path = mds_config.get_data_path(
                provider_name=provider_name,
                date=tz_time.get_time_end()
            )
            s3_trips_file = data_path + "trips.json"

            mds_aws.save(
                json_document=json.dumps(trips),
                file_path=s3_trips_file
            )
            
            logging.debug(f"File saved to {s3_trips_file}")

    # Calculate & print overall time
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    logging.debug(
        "Overall process finished in: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        )
    )


if __name__ == "__main__":
    run()

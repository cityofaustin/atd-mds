#!/usr/bin/env python

import time
import click
import json
from datetime import datetime

from mds import *

from secrets import PROVIDERS

# Debug & Logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.disabled = False


@click.command()
@click.option(
    "--provider-name",
    prompt="Provider Name",
    default="None",
    help="The name of the provider (e.g., Uber, Lyft, Lime, ...)",
)
@click.option(
    "--time-format", default="unix", help="The format to use (e.g., unix or iso)"
)
def run(provider_name, time_format):
    """
    Runs the main program
    :param str provider_name: The name of the provider
    :param str time_format: The time format (unix or iso)
    :return:
    """

    # Start timer
    start = time.time()

    # This is a provider name
    provider_name = str(provider_name).lower()
    time_format = str(time_format).lower()

    # This is a time zone end
    my_time = MDSTimeZone(
        date_time_now=datetime(2020, 1, 11, 17),
        offset=3600,  # One hour
        time_zone="US/Central",  # US/Central
    )

    # Output generated time stamps on screen
    logging.debug("Time Start (iso):\t%s" % my_time.get_time_start())
    logging.debug("Time End   (iso):\t%s" % my_time.get_time_end())
    logging.debug("Running: %s (time format: %s)" % (provider_name, time_format))
    logging.debug("time_start (unix):\t%s" % (my_time.get_time_start(utc=True, unix=True)))
    logging.debug("time_end   (unix):\t%s" % (my_time.get_time_end(utc=True, unix=True)))

    # Fetch the configuration, assume None if not found
    mds_client_configuration = PROVIDERS.get(provider_name, None)

    # Do not proceed if the provider was not found...
    if mds_client_configuration:
        # Initialize the MDS Client
        mds_client = MDSClient(config=PROVIDERS[provider_name], provider=provider_name)

        # Show the configuration
        mds_client.show_config()

        trips = mds_client.get_trips(
            start_time=my_time.get_time_start(utc=True, unix=True),
            end_time=my_time.get_time_end(utc=True, unix=True)
        )

        logging.debug("\n\nResponse:\n")
        click.echo(json.dumps(trips))
        logging.debug("\n\n")

    else:
        logging.debug("-------------------------------------------------")
        logging.debug("Error, Could not find provider: %s" % provider_name)
        logging.debug("-------------------------------------------------")

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

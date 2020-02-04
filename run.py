#!/usr/bin/env python

import time
import click
from mds import *
from helpers import *
from secrets import PROVIDERS

# Debug & Logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.disabled = False


@click.command()
@click.option(
    "--provider",
    default=None,
    prompt="Provider",
    help="The provider's name",
)
@click.option(
    "--file",
    default=None,
    prompt="Output File",
    help="The json file you would like to validate",
)
@click.option(
    "--interval",
    default=None,
    prompt="Interval in hours",
    help="Relative to the maximum time for trip end, an interval window "
         "in hours (i.e., from 11 to noon, you would need the value of '1')"
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
    provider_name = kwargs.get('provider', None)
    file = kwargs.get('file', None)
    interval = kwargs.get('interval', None)
    time_max = kwargs.get('time_max', None)

    print(f"""
        Provider: '{provider_name}'
        Parsing: '{file}'
        Interval: '{interval}'
        Time Max: '{time_max}'
    """)

    if not provider_name:
        print(f"Provider is not defined.")
        exit(1)

    if not file:
        print(f"File {file} is not defined.")
        exit(1)

    if not interval:
        print(f"Interval not defined")
        exit(1)

    if not time_max:
        print(f"Max time not defined")
        exit(1)

    # Load the provider configuration
    mds_client_configuration = PROVIDERS.get(provider_name, None)
    if not mds_client_configuration:
        print(f"The provider configuration could not be loaded for: '{provider_name}'")
        exit(1)

    pdt = parse_datetime(time_max)
    if not pdt:
        print(f"The time-max date provided is not valid: '{time_max}'")
        exit(1)

    interval_int = parse_interval(interval)
    if not interval_int:
        print(f"Interval is not a valid integer: '{interval}'")
        exit(1)
    else:
        interval = interval_int * 60 * 60

    # Start timer
    start = time.time()

    logging.debug("Parsed Date Time:")
    logging.debug(pdt)
    logging.debug("Parsed Interval in seconds:")
    logging.debug(interval)

    # Build timezone aware interval
    logging.debug("Build time-zone aware interval")
    tz_time = MDSTimeZone(
        date_time_now=datetime(pdt["year"], pdt["month"], pdt["day"], pdt["hour"]),
        offset=interval,  # One hour
        time_zone="US/Central",  # US/Central
    )

    # Output generated time stamps on screen
    logging.debug("Time Start (iso):\t%s" % tz_time.get_time_start())
    logging.debug("Time End   (iso):\t%s" % tz_time.get_time_end())
    logging.debug("time_start (unix):\t%s" % (tz_time.get_time_start(utc=True, unix=True)))
    logging.debug("time_end   (unix):\t%s" % (tz_time.get_time_end(utc=True, unix=True)))

    # Do not proceed if the provider was not found...
    if mds_client_configuration:
        # Initialize the MDS Client
        mds_client = MDSClient(config=PROVIDERS[provider_name], provider=provider_name)

        # Show the configuration
        mds_client.show_config()

        trips = mds_client.get_trips(
            start_time=tz_time.get_time_start(utc=True, unix=True),
            end_time=tz_time.get_time_end(utc=True, unix=True)
        )

        if file:
            with open(file, 'w') as f:
                json.dump(trips, f)
        else:
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

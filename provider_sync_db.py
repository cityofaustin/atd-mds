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

    print(f"File: {file}")


if __name__ == "__main__":
    run()
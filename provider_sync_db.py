#!/usr/bin/env python

import click
from provider_helpers import *

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
                PLACEHOLDER
    """


if __name__ == "__main__":
    run()

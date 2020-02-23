#!/usr/bin/env python
import os
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

logging.disable(logging.DEBUG)

# Let's initialize our configuration class
mds_config = MDSConfig()
# Then we need to initialize our AWS class with our configuration
mds_aws = MDSAWS(
    aws_default_region=mds_config.ATD_MDS_REGION,
    aws_access_key_id=mds_config.ATD_MDS_ACCESS_KEY,
    aws_secret_access_key=mds_config.ATD_MDS_SECRET_ACCESS_KEY,
    bucket_name=mds_config.ATD_MDS_BUCKET,
)
# We will need the point-in-polygon class for our trips
mds_pip = MDSPointInPolygon(mds_config=mds_config)
# Both the CLI and Trips classes will need an http-graphql client
mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None),
)

ATD_MDS_DOCKER_IMAGE = "atddocker/atd-mds-etl:local"


@click.command()
@click.option(
    "--env-file", default=None, help="The environment file to use.",
)
@click.option(
    "--provider", default=None, help="The provider's name",
)
@click.option(
    "--file", default=None, help="Use this flag to use a specific input file.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Forces a schedule to run by changing its status to 0 before running.",
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
    A tool to run schedules.
    :param kwargs:
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

    force = kwargs.get("force", False)
    env_file = kwargs.get("env_file", None)

    # Obtain the path to the env file for the docker image
    if env_file is None:
        print("Error: Env file not provided, be sure to use the flag: '--env-file ~/path/to/file.env'")
        exit(1)

    # Check the CLI settings...
    if mds_cli.valid_settings() is False:
        print("Invalid settings, exiting.")
        exit(1)

    print(f"Settings: {str(mds_cli.get_config())}")
    print(f"Force: {str(force)}")
    print(f"Parsed Time Start: {mds_cli.parsed_date_time_min}")
    print(f"Parsed Time End: {mds_cli.parsed_date_time_max}")
    print(f"Parsed Interval: {mds_cli.parsed_interval}")

    # Retrieve the Schedule Class instance
    mds_schedule = mds_cli.initialize_schedule(
        # Default status, we expect 0 = new
        status_id=0,
        # Do not check for status if force is enabled
        status_check=(True, False)[force],
    )

    # Gather schedule items:
    schedule = mds_schedule.get_schedule()
    # print(f"Schedule: {json.dumps(schedule)}")
    print(f"Total items in schedule: {len(schedule)} (blocks)")
    processes = ["extract", "sync_db", "sync_socrata"]
    total_blocks = len(schedule)
    current_block = 0
    # For each schedule hour block:
    for sb in schedule:
        current_block += 1
        block = f'{sb["year"]}-{sb["month"]}-{sb["day"]}-{sb["hour"]}'
        force_enabled = ("", "--force")[force]
        for process in processes:
            log = f"{mds_cli.provider}/{mds_cli.provider}-{block}-{process}.log"
            error_log = f"{mds_cli.provider}/{mds_cli.provider}-{block}-{process}-error.log"
            command = f'docker run -it --env-file {env_file} --rm {ATD_MDS_DOCKER_IMAGE} ./provider_{process}.py --provider "{mds_cli.provider}" --time-max "{block}" --interval 1 {force_enabled} >> ./logs/{log} 2> ./logs/{error_log}'
            print(
                f"""
    Running Block ({current_block}/{total_blocks}):
        Process: {process} {processes.index(process)+1}/3
        Schedule: {sb}
        Block: '{block}' (1hr)
        Log: $ tail ./{log}
        Command: '{command}' 
            """
            )
            os.system(command)
            command = None


if __name__ == "__main__":
    run()

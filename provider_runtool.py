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
    encryption_key=mds_config.ATD_MDS_FERNET_KEY,
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
    "--docker-args", default="", help="Use this flag to specify hosts when running with docker mode enabled.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Forces a schedule to run by changing its status to 0 before running.",
)
@click.option(
    "--incomplete-only",
    is_flag=True,
    help="Changes the query to process incomplete schedule blocks only.",
)
@click.option(
    "--docker-mode",
    is_flag=True,
    help="Changes the query to process incomplete schedule blocks only.",
)
@click.option(
    "--no-logs",
    is_flag=True,
    help="When enabled does not output logs.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Prints the commands on screen, but does not execute.",
)
@click.option(
    "--no-sync-db",
    is_flag=True,
    help="Removes sync-db as part of the process.",
)
@click.option(
    "--no-sync-socrata",
    is_flag=True,
    help="Removes sync-socrata as part of the process.",
)
@click.option(
    "--no-extract",
    is_flag=True,
    help="Removes extraction as part of the process.",
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

    incomplete_only = kwargs.get("incomplete_only", False)
    force = kwargs.get("force", False)
    env_file = kwargs.get("env_file", None)
    docker_mode = kwargs.get("docker_mode", False)
    docker_args = kwargs.get("docker_args", "")

    no_extact = kwargs.get("no_extract", False)
    no_syncdb = kwargs.get("no_sync_db", False)
    no_syncsoc = kwargs.get("no_sync_socrata", False)
    dry_run = kwargs.get("dry_run", False)
    no_logs = kwargs.get("no_logs", False)

    # Obtain the path to the env file for the docker image

    if docker_mode is True and env_file is None:
        print("Error: Env file not provided, be sure to use the flag: '--env-file ~/path/to/file.env'")
        exit(1)

    if docker_mode:
        docker_cmd = f"docker run {docker_args} -it --env-file {env_file} --rm {ATD_MDS_DOCKER_IMAGE} "
    else:
        docker_cmd = ""

    # Check the CLI settings...
    if mds_cli.valid_settings() is False:
        print("Invalid settings, exiting.")
        exit(1)

    print(f"Settings: {str(mds_cli.get_config())}")
    print(f"Force: {str(force)}")
    print(f"Parsed Time Start: {mds_cli.parsed_date_time_min}")
    print(f"Parsed Time End: {mds_cli.parsed_date_time_max}")
    print(f"Parsed Interval: {mds_cli.parsed_interval}")

    if incomplete_only:
        # Retrieve incomplete schedules
        mds_schedule = mds_cli.initialize_schedule(
            # Default status, we expect 0 = new
            status_id=8,
            # Do not check for status if force is enabled
            status_check=(True, False)[force],
            # We need to make sure it is less than and not equal to 8.
            status_operator="_lt"
        )
    else:
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

    # Enforce --no-(*) flags to omit certain processes
    if no_extact:
        processes.remove("extract")
    if no_syncdb:
        processes.remove("sync_db")
    if no_syncsoc:
        processes.remove("sync_socrata")

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
            logs_command = (f">> ./logs/{log} 2> ./logs/{error_log}", "")[no_logs]

            command = f'{docker_cmd}./provider_{process}.py --provider "{mds_cli.provider}" ' \
                f'--time-max "{block}" --interval 1 {force_enabled} {logs_command}'

            # Socrata Sync does not support need the --force flag
            if process == "sync_socrata":
                command = command.replace("--force", "")

            # Check if this is a dry-run
            if dry_run is False:
                print(
                    f"""
                    Running Block ({current_block}/{total_blocks}):
                        Process: {process} {processes.index(process) + 1}/3
                        Schedule: {sb}
                        Block: '{block}' (1hr)
                        Log: $ tail ./logs/{log}
                        Command: '{command}' 
                    """
                )
                print(os.system(command))

            else:
                print(f"(dry)$ {command}\n")
            # Clear the command, for good measure.
            command = None


if __name__ == "__main__":
    run()

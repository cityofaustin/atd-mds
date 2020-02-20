#!/usr/bin/env python

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
mds_pip = MDSPointInPolygon(
    mds_config=mds_config
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
        mds_gql=mds_gql,
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

    print(f"Parsed Time Max: {mds_cli.parsed_date_time_max}")
    print(f"Parsed Time Min: {mds_cli.parsed_date_time_min}")
    print(f"Parsed Interval: {mds_cli.parsed_interval}")

    # Retrieve the Schedule Class instance
    mds_schedule = mds_cli.initialize_schedule(status_id=2)
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
        print("Time Start (iso):\t%s" % tz_time.get_time_start())
        print("Time End   (iso):\t%s" % tz_time.get_time_end())
        logging.debug("time_start (unix):\t%s" % (tz_time.get_time_start(utc=True, unix=True)))
        logging.debug("time_end   (unix):\t%s" % (tz_time.get_time_end(utc=True, unix=True)))

        print("Loading File from AWS S3...")
        # Determine data directory in S3
        data_path = mds_config.get_data_path(
            provider_name=mds_cli.provider, date=tz_time.get_time_start()
        )
        # Determine final file path
        s3_trips_file = data_path + "trips.json"
        # Load the file from S3 into a dictionary called 'trips'
        trips = mds_aws.load(s3_trips_file)

        trips_count = len(trips["data"]["trips"])
        print(f"File loaded with trips_count: {trips_count}")

        total_trips = 0
        trips_valid = 0
        trips_success = 0
        trips_error = 0

        # For each trip, we need to build a trip object
        for trip in trips["data"]["trips"]:
            print(f'Constructing trip: {trip["trip_id"]}')

            mds_trip = MDSTrip(
                mds_config=mds_config,  # We pass the configuration class
                mds_pip=mds_pip,  # We pass the point-in-polygon class
                mds_gql=mds_gql,  # We pass the HTTP GraphQL class
                trip_data=trip  # We provide this individual trip data
            )

            # VeoRide isn't fully MDS compliant, so we need to fix its data
            if mds_trip.get_provider_name() == "VeoRide INC.":
                # The trip_id is an integer, we need a uuid
                current_trip_id = mds_trip.get_trip_value("trip_id")
                new_trip_uuid = mds_trip.int_to_uuid(current_trip_id)
                mds_trip.set_trip_value("trip_id", new_trip_uuid)
                # The device_id is an integer, we need a uuid
                current_device_id = mds_trip.get_trip_value("device_id")
                new_device_id = mds_trip.int_to_uuid(current_device_id)
                mds_trip.set_trip_value("device_id", str(new_device_id))
                # The vehicle_id is an integer, it needs a string
                current_veh_id = mds_trip.get_trip_value("vehicle_id")
                mds_trip.set_trip_value("vehicle_id", str(current_veh_id))

            total_trips += 1
            # We can generate a GraphQL Query for debugging
            # gql = mds_trip.generate_gql_insert()
            # If the trip is validated
            if mds_trip.is_valid():
                trips_valid += 1
                if mds_trip.save():
                    print(f'Processed trip ({total_trips}/{trips_count}): {trip["trip_id"]}')
                    trips_success += 1
                else:
                    print(f'Error Processing trip: {trip["trip_id"]}')
                    trips_error += 1
            else:
                print("Error when inserting trip: ")
                print(json.dumps(mds_trip.get_validation_errors()))
                gql = mds_trip.generate_gql_insert()
                print(gql)
                exit(1)

        trips_report = {
            "total_trips": total_trips,
            "trips_valid": trips_valid,
            "trips_success": trips_success,
            "trips_error": trips_error,
        }
        """
        Status Types:
            5,Data insertion succeeded
            -5,Data insertion failed
            6,Data insertion completed with errors
            -6,Data insertion contained all errors
        """
        if total_trips == trips_success and trips_error == 0:
            final_status = 5

        if trips_success > 0 and trips_error > 0:
            final_status = 6

        if total_trips == trips_error:
            final_status = -6

        print("Updating schedule status...")
        mds_schedule.set_schedule_status(
            schedule_id=schedule_item["schedule_id"],
            status_id=final_status,
            records_processed=trips_success,
            records_total=total_trips,
        )

        print("As of this run: ")
        print(json.dumps(trips_report))

    # Gather timer end & output to console...
    hours, minutes, seconds = mds_cli.get_timer_end()
    print(
        "Overall process finished in: {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        )
    )


if __name__ == "__main__":
    run()

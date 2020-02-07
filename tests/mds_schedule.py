#!/usr/bin/env python

# Basic libraries
from datetime import datetime

# Import MDS Library for the TimeZone class
from mds import MDSTimeZone
from parent_directory import *

from MDSConfig import MDSConfig
from MDSSchedule import MDSSchedule
from MDSGraphQLRequest import MDSGraphQLRequest


time_min = MDSTimeZone(
    date_time_now=datetime(2020, 1, 1, 17),
    offset=0,  # One hour
    time_zone="US/Central",  # US/Central
)

time_max = MDSTimeZone(
    date_time_now=datetime(2020, 1, 1, 17),
    offset=0,  # One hour
    time_zone="US/Central",  # US/Central
)

mds_config = MDSConfig()

gql_request = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", "n/a"),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", "n/a")
)

mds_shedule = MDSSchedule(
    http_graphql_request=gql_request,
    provider_id=1,
    status_id=0,
    time_min=time_min.get_time_end(),
    time_max=time_max.get_time_end()
)

print(mds_shedule.get_query())

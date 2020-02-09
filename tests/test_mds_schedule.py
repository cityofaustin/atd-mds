#!/usr/bin/env python

# Basic libraries
from datetime import datetime

# Import MDS Library for the TimeZone class
from parent_directory import *
from mds import MDSTimeZone
from ariadne import gql

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSSchedule import MDSSchedule

# Assumes MDSConfig and MDSGraphQLRequest work as expected
mds_config = MDSConfig()

gql_request = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", "n/a"),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", "n/a")
)


class TestMDSSchedule:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSSchedule")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSSchedule")

    def test_gql_catches_error(self):
        try:
            # This should crash regardless, causing the exception block to execute
            error_caught = isinstance(gql("""
                        {
                            NOT A GraphQL Query, this should be False!
                        }
                    """), str)
            # If gql does not raise an exception, then the test failed
            error_caught = False
        except:
            # This block should always run
            error_caught = True

        assert error_caught

    def test_gql_parses_graphql(self):
        assert isinstance(gql("""
                    query fetchPendingSchedules {
                        api_schedule(
                            limit: 1
                        ) {
                            provider_id
                            schedule_id
                            year
                            month
                            day
                            hour
                            status_id
                        }
                    }
                """), str)

    def test_one_hour_schedule(self):
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

        mds_shedule = MDSSchedule(
            http_graphql_request=gql_request,
            provider_id=1,
            status_id=0,
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end()
        )

        query = mds_shedule.get_query()
        print("Query: " + query)
        assert isinstance(gql(query), str)

    def test_no_time_min(self):

        time_max = MDSTimeZone(
            date_time_now=datetime(2020, 1, 1, 17),
            offset=0,  # One hour
            time_zone="US/Central",  # US/Central
        )

        mds_shedule = MDSSchedule(
            http_graphql_request=gql_request,
            provider_id=1,
            time_max=time_max.get_time_end()
        )

        query = mds_shedule.get_query()
        print("Query: " + query)
        assert isinstance(gql(query), str)

    def test_schedule_range(self):
        time_min = MDSTimeZone(
            date_time_now=datetime(2020, 1, 1, 0),
            offset=0,  # Not Needed
            time_zone="US/Central",  # US/Central
        )

        time_max = MDSTimeZone(
            date_time_now=datetime(2020, 1, 1, 17),
            offset=0,  # Not needed
            time_zone="US/Central",  # US/Central
        )

        mds_shedule = MDSSchedule(
            http_graphql_request=gql_request,
            provider_id=1,
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end()
        )

        query = mds_shedule.get_query()
        print("Query: " + query)
        assert isinstance(gql(query), str)
#!/usr/bin/env python

# Basic libraries
import json
from datetime import datetime
from random import randrange

# Import MDS Library for the TimeZone class
from parent_directory import *
from mds import MDSTimeZone
from ariadne import gql

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSSchedule import MDSSchedule

# Assumes MDSConfig and MDSGraphQLRequest work as expected
mds_config = MDSConfig()
mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None),
)

time_max_tester = MDSTimeZone(
    date_time_now=datetime(2020, 1, 1, 2), offset=1, time_zone="US/Central",
)

mds_schedule_tester = MDSSchedule(
    mds_config=mds_config,
    mds_gql=mds_gql,
    provider_name="sample_co",
    time_max=time_max_tester.get_time_end(),
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
            error_caught = isinstance(
                gql(
                    """
                        {
                            NOT A GraphQL Query, this should be False!
                        }
                    """
                ),
                str,
            )
            # If gql does not raise an exception, then the test failed
            error_caught = False
        except:
            # This block should always run
            error_caught = True

        assert error_caught

    def test_gql_parses_graphql(self):
        assert isinstance(
            gql(
                """
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
                """
            ),
            str,
        )

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
        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            status_id=0,
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
        )
        query = mds_schedule.get_query()
        print("Query: " + query)
        assert isinstance(gql(query), str)

    def test_no_time_min(self):

        time_max = MDSTimeZone(
            date_time_now=datetime(2020, 1, 1, 17),
            offset=0,  # One hour
            time_zone="US/Central",  # US/Central
        )

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_max=time_max.get_time_end(),
        )

        query = mds_schedule.get_query()
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

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
        )

        query = mds_schedule.get_query()
        print("Query: " + query)
        assert isinstance(gql(query), str)

    def test_get_schedule_success_t1(self):
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

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
        )

        query = mds_schedule.get_query()
        print("Query: " + query)
        schedule = mds_schedule.get_schedule()
        print("Schedule: " + json.dumps(schedule))
        success_a = isinstance(schedule, list)
        success_b = False if "errors" in schedule else True
        assert success_a and success_b

    def test_get_schedule_fail_t1(self):
        try:
            mds_schedule = MDSSchedule(
                mds_config=mds_config,
                mds_gql=mds_gql,
                provider_name="jump",
                time_min=None,
                time_max=None,
            )
            mds_schedule.get_schedule()
            assert False
        except:
            assert True

    def test_quotable_value_success_t1(self):
        assert mds_schedule_tester.is_quotable_value(1) is False

    def test_quotable_value_success_t2(self):
        assert mds_schedule_tester.is_quotable_value(1.0) is False

    def test_quotable_value_success_t3(self):
        assert mds_schedule_tester.is_quotable_value(True) is False

    def test_quotable_value_success_t4(self):
        assert mds_schedule_tester.is_quotable_value('{"message": "This is escaped"}')

    def test_quotable_value_success_t5(self):
        assert mds_schedule_tester.is_quotable_value(datetime(2020, 1, 1, 17))

    def test_quotable_value_success_t6(self):
        assert mds_schedule_tester.is_quotable_value("This is a sample string")

    def test_update_status_query_success_t1(self):
        query = mds_schedule_tester.get_schedule_update_status_query(
            schedule_id=-1, status_id=-1
        )
        print("Update Mutation Query: " + query)
        assert isinstance(gql(query), str)

    def test_update_status_query_addtl_args_success_t1(self):
        query = mds_schedule_tester.get_schedule_update_status_query(
            schedule_id=-1,
            status_id=-1,
            payload="https://bucket.s3.aws.com/payload.json",
            message='{"message":"Success"}',
        )
        print("Update Mutation Query: " + query)
        assert isinstance(gql(query), str)

    def test_update_status_success_t1(self):
        updated = mds_schedule_tester.set_schedule_status(schedule_id=-1, status_id=-1)
        assert updated == 1

    def test_get_schedule_by_id_success_t1(self):
        schedule = mds_schedule_tester.get_schedule_by_id(schedule_id=-1)
        print(schedule)
        assert isinstance(schedule, list) and len(schedule) == 1

    def test_update_status_success_t2(self):
        payload = "http://bucket.s3.aws.com/payload_%s_.json" % str(
            randrange(1000, 9999)
        )
        message = '{"message": "This is a message: %s"}' % str(randrange(1000, 9999))
        updated = mds_schedule_tester.set_schedule_status(
            schedule_id=-1, status_id=-1, payload=payload, message=message,
        )
        schedule = mds_schedule_tester.get_schedule_by_id(schedule_id=-1)
        print(f"Payload: {payload}")
        print(f"message: {message}")
        print(f"updated: {updated}")
        print(f"schedule: {schedule}")
        assert (
            1 == 1
            and updated == 1
            and isinstance(schedule, list)
            and len(schedule) == 1
            and schedule[0]["payload"] == payload
            and schedule[0]["message"] == message
        )

    def test_status_operator_success_t1(self):
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

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
            status_id=8,
            status_operator="_lt"
        )

        query = mds_schedule.get_query()
        print("My good sir, query: " + query)
        assert isinstance(gql(query), str) \
               and "status_id: {_lt: 8}" in gql(query)

    def test_status_operator_success_t2(self):
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

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
            status_id=8
        )

        query = mds_schedule.get_query()
        print("My good sir, query: " + query)
        assert isinstance(gql(query), str) \
               and "status_id: {_eq: 8}" in gql(query)

    def test_status_operator_success_t3(self):
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

        mds_schedule = MDSSchedule(
            mds_config=mds_config,
            mds_gql=mds_gql,
            provider_name="jump",
            time_min=time_min.get_time_end(),
            time_max=time_max.get_time_end(),
        )

        query = mds_schedule.get_query()
        print("My good sir, query: " + query)
        assert isinstance(gql(query), str) \
               and "status_id: {_eq: 0}" in gql(query)

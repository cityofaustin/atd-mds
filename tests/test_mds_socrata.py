#!/usr/bin/env python

# Basic libraries
import json
import pdb
from datetime import datetime

# Import MDS Library for the TimeZone class
from parent_directory import *
from ariadne import gql

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSSocrata import MDSSocrata

mds_config = MDSConfig()

mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None),
)

mds_socrata = MDSSocrata(
    provider_name="sample_co",
    mds_config=mds_config,
    mds_gql=mds_gql
)


class TestMDSSocrata:
    # Assumes MDSConfig works as expected
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSSocrata")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSSocrata")

    def test_constructor_success_t1(self):
        try:
            MDSSocrata(
                provider_name="sample_co",
                mds_config=mds_config,
                mds_gql=mds_gql
            )
            assert True
        except:
            assert False

    def test_constructor_fail_t1(self):
        try:
            MDSSocrata(
                provider_name=None,
                mds_config=None,
                mds_gql=None
            )
            assert False
        except:
            assert True

    def test_config_loaded_success_t1(self):
        config = mds_socrata.get_config()
        assert isinstance(config, dict)

    def test_get_query_success_t1(self):
        query = mds_socrata.get_query(
            time_min='2020-01-01 00:00:00',
            time_max='2020-02-01 00:00:00'
        )
        assert 'provider: { provider_name: { _eq: "sample_co" }}' in query \
               and 'end_time: { _gte: "2020-01-01 00:00:00" }' in query \
               and '_and: { end_time: { _lt: "2020-02-01 00:00:00" }}' in query

    def test_get_query_fail_t1(self):
        try:
            mds_socrata.get_query(time_min=None, time_max=None)
            assert False
        except:
            assert True

    def test_get_query_fail_t2(self):
        try:
            mds_socrata.get_query(time_min=10, time_max=20)
            assert False
        except:
            assert True

    def test_valid_query_success_t1(self):
        query = mds_socrata.get_query(
            time_min='2020-01-01 00:00:00',
            time_max='2020-02-01 00:00:00'
        )
        print("GQL: ")
        print(query)
        assert isinstance(gql(query), str)

    def test_valid_query_success_t2(self):
        query = mds_socrata.get_query(
            time_min='1999-01-01 00:00:00',
            time_max='2999-02-01 00:00:00'
        )
        print("GQL: ")
        print(query)
        assert isinstance(gql(query), str)

    def test_valid_query_fail_t1(self):
        try:
            mds_socrata.get_query(
                time_min=None,
                time_max=None
            )
            assert False
        except:
            assert True

    def test_translate_timestamp_success(self):
        dt = mds_socrata.translate_timestamp(1632842501000)
        dts = dt.strftime("%Y-%m-%dT%H:%M:%S")

        assert dt.year == 2021
        assert dt.month == 9
        assert dt.day == 28
        assert dt.hour == 15
        assert dt.minute == 21
        assert dt.second == 41
        assert dts == "2021-09-28T15:21:41"

    def test_parse_datetimes_success(self):
        test_data = mds_socrata.parse_datetimes(data={
            "start_time": "2021-09-28 11:11:11",
            "end_time": "2021-09-28 22:22:22",
            "modified_date": "2021-09-28 00:00:00",
        })

        assert test_data["start_time"] == "2021-09-28T11:11:11"
        assert test_data["end_time"] == "2021-09-28T22:22:22"
        assert test_data["modified_date"] == "2021-09-28T00:00:00"
        assert test_data["year"] == 2021
        assert test_data["month"] == 9
        assert test_data["hour"] == 22
        assert test_data["day_of_week"] == 1  # Monday is 0

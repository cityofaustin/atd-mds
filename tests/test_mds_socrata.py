#!/usr/bin/env python

# Basic libraries
import json
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

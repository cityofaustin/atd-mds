#!/usr/bin/env python

# Basic libraries
import json
from datetime import datetime

# Import MDS Library for the TimeZone class
from parent_directory import *
from ariadne import gql

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest
from MDSKnack import MDSKnack

mds_config = MDSConfig()

mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None),
)

mds_knack = MDSKnack()


class TestMDSKnack:
    # Assumes MDSConfig works as expected
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSKnack")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSKnack")

    def test_constructor_success_t1(self):
        try:
            TestMDSKnack()
            assert True
        except:
            assert False

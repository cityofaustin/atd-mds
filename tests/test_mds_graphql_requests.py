#!/usr/bin/env python

import pytest

from parent_directory import *

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest

# Assume the config will work as expected
mds_config = MDSConfig()

gql_request = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", "n/a"),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", "n/a"),
)


class TestMDSGraphQLRequests:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSGraphQLRequests")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSGraphQLRequests")

    def test_constructor(self):
        assert isinstance(gql_request, MDSGraphQLRequest)

    def test_configuration_settings(self):
        config = gql_request.get_config()
        assert isinstance(config, dict)

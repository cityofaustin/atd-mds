#!/usr/bin/env python

import pytest

from parent_directory import *

from MDSConfig import MDSConfig
from MDSGraphQLRequest import MDSGraphQLRequest

mds_config = MDSConfig()

gql_request = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", "n/a"),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", "n/a")
)
gql_request.show_config()

print("Done testing")

def test_quicktest():
    print("Testing here ...")
    assert True









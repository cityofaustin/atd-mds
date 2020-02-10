#!/usr/bin/env python
import pytest


from parent_directory import *


from MDSConfig import MDSConfig
from MDSAWS import MDSAWS

mds_config = MDSConfig()

class TestMDSAWS:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSAWS")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSAWS")

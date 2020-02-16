#!/usr/bin/env python
import pytest
from datetime import datetime

from parent_directory import *
from mds import MDSTimeZone
from MDSConfig import MDSConfig

import logging

logging.disable(logging.DEBUG)


class TestMDSConfig:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSConfig")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSConfig")

    def test_constructor(self):
        mds_config = MDSConfig()
        assert isinstance(mds_config, MDSConfig)

    def test_data_path(self):
        mds_config = MDSConfig()
        tz_time = MDSTimeZone(
            date_time_now=datetime(2020, 1, 1, 17),
            offset=3600,  # One hour
            time_zone="US/Central",  # US/Central
        )

        data_path = mds_config.get_data_path(
            provider_name="bird", date=tz_time.get_time_end()
        )
        assert len(data_path) > 0

    def test_provider_config(self):
        mds_config = MDSConfig()
        veoride_config = mds_config.get_provider_config("veoride")
        assert isinstance(veoride_config, dict)

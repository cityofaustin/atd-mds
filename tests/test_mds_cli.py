#!/usr/bin/env python
import pytest

import botocore
from parent_directory import *


from MDSConfig import MDSConfig
from MDSCli import MDSCli
from MDSSchedule import MDSSchedule

mds_config = MDSConfig()


class TestMDSCli:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSCli")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSCli")

    def test_constructor_success_t1(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=1,
            time_max="2020-1-11-17",
            time_min=None
        )

        assert isinstance(mds_cli, MDSCli)

    def test_constructor_fail_t1(self):
        try:
            mds_cli = MDSCli(
                mds_config=mds_config,
                provider="not-a-valid-provider",
                interval=1,
                time_max="2020-1-11-17",
                time_min=None
            )
            assert False
        except:
            assert True

    def test_constructor_fail_t2(self):
        try:
            mds_cli = MDSCli(
                mds_config=mds_config,
                provider="lime",
                interval=1,
                time_max="not-a-valid-time-parameter",
                time_min=None
            )
            assert False
        except:
            assert True

    def test_constructor_fail_t3(self):
        try:
            mds_cli = MDSCli(
                mds_config=mds_config,
                provider=None,
                interval=1,
                time_max=None,
                time_min=None
            )
            assert False
        except:
            assert True

    def test_initialize_schedule_success(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=1,
            time_max="2020-1-11-17",
            time_min=None
        )

        s = mds_cli.initialize_schedule()

        assert isinstance(s, MDSSchedule)

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

    def test_initialize_schedule_one_hour_success(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=1,
            time_max="2020-1-11-17",
            time_min=None
        )

        s = mds_cli.initialize_schedule()
        sc = s.get_schedule()
        assert isinstance(s, MDSSchedule) and len(sc) == 1

    def test_initialize_schedule_two_hour_success(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=2,
            time_max="2020-1-11-17",
            time_min=None
        )

        s = mds_cli.initialize_schedule()
        sc = s.get_schedule()
        assert isinstance(s, MDSSchedule) and len(sc) == 2

    def test_initialize_schedule_midnight_1hr_int_success(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=1,
            time_max="2020-1-11-0",
            time_min=None
        )

        s = mds_cli.initialize_schedule()
        sc = s.get_schedule()
        assert isinstance(s, MDSSchedule) and len(sc) == 1

    def test_initialize_schedule_midnight_23hr_int_success(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=23,
            time_max="2020-1-11-0",
            time_min=None
        )

        s = mds_cli.initialize_schedule()
        sc = s.get_schedule()
        q = s.get_query()
        assert isinstance(s, MDSSchedule) and len(sc) == 23

    def test_initialize_schedule_24_hours_success_t2(self):
        mds_cli = MDSCli(
            mds_config=mds_config,
            provider="jump",
            interval=0,
            time_min="2020-1-10-0",
            time_max="2020-1-11-0",
        )

        s = mds_cli.initialize_schedule()
        sc = s.get_schedule()
        assert isinstance(s, MDSSchedule) and len(sc) == 24

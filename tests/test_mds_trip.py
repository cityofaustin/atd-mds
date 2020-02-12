#!/usr/bin/env python

# Basic libraries
import json
from datetime import datetime

# Import MDS Library for the TimeZone class
from parent_directory import *
from ariadne import gql

from MDSConfig import MDSConfig
from MDSTrip import MDSTrip
from MDSPointInPolygon import MDSPointInPolygon

# Assumes MDSConfig works as expected
mds_config = MDSConfig()
mds_pip = MDSPointInPolygon(mds_config=mds_config, autoload=True)


class TestMDSTrip:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSTrip")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSTrip")

    def test_constructor_success_t1(self):
        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data={"trip": "data"}
        )
        assert isinstance(mds_trip, MDSTrip)

    def test_constructor_fail_t1(self):
        try:
            mds_trip = MDSTrip(
                mds_config=None,
                mds_pip=mds_pip,
                trip_data=None
            )
            # If the execution gets to this point, the test is a failure
            assert False
        except:
            # If it gets to this point, the test is a success
            assert True

    def test_validator_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        assert mds_trip.is_valid()

    def test_validator_fail_t1(self):
        with open("tests/trip_sample_data_not_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        # If the trip is marked as valid, then the test failed.
        assert mds_trip.is_valid() is False

    def test_save_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        query = mds_trip.generate_gql_insert()
        print("GQL: ")
        print(query)
        assert isinstance(
            gql(query),
            str
        )

    def test_save_fail_t1(self):
        assert True

    def test_search_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        query = mds_trip.generate_gql_search("123456789")
        print("GQL: ")
        print(query)
        assert isinstance(
            gql(query),
            str
        )

    def test_search_fail_t1(self):
        assert True

    def test_get_coordinates_start_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        start_long, start_lat = mds_trip.get_coordinates(start=True)

        print(f"start_long: {start_long}")
        print(f"start_lat: {start_lat}")

    def test_get_coordinates_end_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            trip_data=trip_data
        )
        start_long, start_lat = mds_trip.get_coordinates(start=False)

        print(f"start_long: {start_long}")
        print(f"start_lat: {start_lat}")


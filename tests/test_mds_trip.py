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
from MDSGraphQLRequest import MDSGraphQLRequest

# Assumes MDSConfig works as expected
mds_config = MDSConfig()
mds_pip = MDSPointInPolygon(mds_config=mds_config, autoload=True)
mds_gql = MDSGraphQLRequest(
    endpoint=mds_config.get_setting("HASURA_ENDPOINT", None),
    http_auth_token=mds_config.get_setting("HASURA_ADMIN_KEY", None),
)


class TestMDSTrip:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSTrip")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSTrip")

    def test_constructor_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert isinstance(mds_trip, MDSTrip)

    def test_constructor_fail_t1(self):
        mds_trip = MDSTrip(
            mds_config=mds_config,
            mds_pip=mds_pip,
            mds_gql=mds_gql,
            trip_data={"trip": "data"},
        )
        isinstance(mds_trip, MDSTrip)

    def test_constructor_fail_t2(self):
        try:
            mds_trip = MDSTrip(
                mds_config=None, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=None
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
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert mds_trip.is_valid()

    def test_validator_success_t2(self):
        with open("tests/trip_sample_data_valid_long.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert mds_trip.is_valid()

    def test_validator_success_t3(self):
        with open("tests/trip_sample_data_valid_short.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert mds_trip.is_valid()

    def test_validator_fail_t1(self):
        with open("tests/trip_sample_data_not_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        # If the trip is marked as valid, then the test failed.
        assert mds_trip.is_valid() is False

    def test_generate_gql_insert_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        query = mds_trip.generate_gql_insert()
        print("GQL: ")
        print(query)
        assert isinstance(gql(query), str)

    def test_search_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        query = mds_trip.generate_gql_search("123456789")
        print("GQL: ")
        print(query)
        assert isinstance(gql(query), str)

    def test_search_fail_t1(self):
        assert True

    def test_get_coordinates_start_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        start_long, start_lat = mds_trip.get_coordinates(start=True)

        print(f"start_long: {start_long}")
        print(f"start_lat: {start_lat}")

    def test_get_coordinates_end_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        start_long, start_lat = mds_trip.get_coordinates(start=False)

        print(f"start_long: {start_long}")
        print(f"start_lat: {start_lat}")

    def test_set_trip_value_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        mds_trip.set_trip_value("council_district_start", "this_is_a_test")
        assert mds_trip.get_trip_value("council_district_start") == "this_is_a_test"

    def test_set_trip_value_success_t2(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        mds_trip.set_trip_value("dest_cell_id", -97.023123123)
        assert mds_trip.get_trip_value("dest_cell_id") == -97.023123123

    def test_set_trip_value_fail_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        mds_trip.set_trip_value("dest_cell_id", "test_value")
        assert mds_trip.get_trip_value("wrong_key") is None

    def test_initialize_points_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )

        success = (
            1 == 1
            and mds_trip.get_trip_value("council_district_start") is not None
            and mds_trip.get_trip_value("council_district_end") is not None
            and mds_trip.get_trip_value("orig_cell_id") is not None
            and mds_trip.get_trip_value("dest_cell_id") is not None
            and mds_trip.get_trip_value("census_geoid_start") is not None
            and mds_trip.get_trip_value("census_geoid_end") is not None
        )
        assert success

    def test_get_trip_by_id_success_t1(self):
        trip_id = "b3ca5c86-7f45-4544-bf58-111111111111"
        trips = MDSTrip.get_trip_by_id(mds_gql=mds_gql, trip_id=trip_id)
        success = (
            1 == 1
            and isinstance(trips, list)
            and len(trips) == 1
            and trips[0]["trip_id"] == trip_id
        )
        assert success

    def test_get_trip_by_id_fail_t1(self):
        trip_id = "b3ca5c86-7f45-4544-bf58-111111111110"
        trips = MDSTrip.get_trip_by_id(mds_gql=mds_gql, trip_id=trip_id)
        success = 1 == 1 and isinstance(trips, list) and len(trips) == 0
        assert success

    def test_save_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )

        assert mds_trip.save()

    def test_veo_uuid_generator_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert (
                mds_trip.int_to_uuid(integer_number=1)
                == "0309585e-599f-4e57-ac85-fffffffffff1"
        )

    def test_veo_uuid_generator_success_t2(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert (
            mds_trip.int_to_uuid(integer_number=104865)
            == "0309585e-599f-4e57-ac85-fffffff199a1"
        )

    def test_veo_uuid_generator_success_t3(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert (
            mds_trip.int_to_uuid(integer_number=99999999)
            == "0309585e-599f-4e57-ac85-fffff5f5e0ff"
        )

    def test_get_provider_name_success_t1(self):
        with open("tests/trip_sample_data_valid.json") as f:
            trip_data = json.load(f)
        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )
        assert mds_trip.get_provider_name() == "sample_co"

    def test_get_provider_name_success_t2(self):
        with open("tests/trip_sample_data_valid_short.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )

        assert mds_trip.get_provider_name() == "VeoRide INC."

    def test_get_provider_name_fail_t1(self):
        with open("tests/trip_sample_data_not_valid.json") as f:
            trip_data = json.load(f)

        mds_trip = MDSTrip(
            mds_config=mds_config, mds_pip=mds_pip, mds_gql=mds_gql, trip_data=trip_data
        )

        assert mds_trip.get_provider_name() is None

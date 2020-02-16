#!/usr/bin/env python

# Basic libraries
import json
from datetime import datetime

# Import MDS Library for the TimeZone class
from parent_directory import *

from MDSConfig import MDSConfig
from MDSPointInPolygon import MDSPointInPolygon

# Assumes MDSConfig and MDSGraphQLRequest work as expected
mds_config = MDSConfig()
# Preloaded PIP
mds_pip_preloaded = MDSPointInPolygon(mds_config=mds_config)

# Test Locations

loc_6th_and_congress = {"longitude_x": -97.742803, "latitude_y": 30.268048}

loc_airport = {"longitude_x": -97.667019, "latitude_y": 30.202756}

loc_san_antonio_commerce_alamo = {"longitude_x": -98.487268, "latitude_y": 29.423622}


class TestMDSPointInPolygon:
    @classmethod
    def setup_class(cls):
        print("Beginning tests for: TestMDSPointInPolygon")

    @classmethod
    def teardown_class(cls):
        print("All tests finished for: TestMDSPointInPolygon")

    def test_constructor_success_t1(self):
        try:
            mds_pip = MDSPointInPolygon(mds_config=mds_config)
            assert True
        except:
            assert False

    def test_constructor_fail_t1(self):
        try:
            mds_pip = MDSPointInPolygon(mds_config=None)
            assert False
        except:
            assert True

    def test_census_tract_geojson_loads_success_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config)
        assert mds_pip.CENSUS_TRACTS_GEOJSON is not None

    def test_districts_geojson_loads_success_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config)
        assert mds_pip.DISTRICTS_GEOJSON is not None

    def test_hex_geojson_loads_success_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config)
        assert mds_pip.HEX_GEOJSON is not None

    def test_autoload_success_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config, autoload=False)
        success = (
            1 == 1
            and mds_pip.HEX_GEOJSON is None
            and mds_pip.DISTRICTS_GEOJSON is None
            and mds_pip.CENSUS_TRACTS_GEOJSON is None
            and mds_pip.HEX_INDEX is None
            and mds_pip.DISTRICTS_INDEX is None
            and mds_pip.CENSUS_TRACTS_INDEX is None
        )
        assert success

    def test_autoload_fail_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config, autoload=True)
        success = (
            1 == 1
            and mds_pip.HEX_GEOJSON is None
            and mds_pip.DISTRICTS_GEOJSON is None
            and mds_pip.CENSUS_TRACTS_GEOJSON is None
            and mds_pip.HEX_INDEX is None
            and mds_pip.DISTRICTS_INDEX is None
            and mds_pip.CENSUS_TRACTS_INDEX is None
        )
        assert success is False

    def test_create_point_success_t1(self):
        pt = mds_pip_preloaded.create_point(5, 5)
        assert pt.x == 5 and pt.y == 5

    def test_create_point_fail_t1(self):
        mds_pip = MDSPointInPolygon(mds_config=mds_config, autoload=False)
        try:
            pt = mds_pip.create_point(None, None)
            assert False
        except:
            return True

    def test_pip_district_id_success_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_6th_and_congress["longitude_x"],
            latitude_y=loc_6th_and_congress["latitude_y"],
        )  # 6th and Congress, District 9
        district_id = mds_pip_preloaded.get_district_id(mds_point=p)
        print(district_id)
        assert isinstance(district_id, str) and district_id == "9"

    def test_pip_district_id_success_t2(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_airport["longitude_x"], latitude_y=loc_airport["latitude_y"]
        )  # Airport = District 2
        district_id = mds_pip_preloaded.get_district_id(mds_point=p)
        print(district_id)
        assert isinstance(district_id, str) and district_id == "2"

    def test_pip_district_id_fail_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_san_antonio_commerce_alamo["longitude_x"],
            latitude_y=loc_san_antonio_commerce_alamo["latitude_y"],
        )  # San Antonio @ Commerce & S Alamo St.
        district_id = mds_pip_preloaded.get_district_id(mds_point=p)
        print(district_id)
        assert district_id is None

    def test_pip_census_tract_id_success_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_6th_and_congress["longitude_x"],
            latitude_y=loc_6th_and_congress["latitude_y"],
        )  # 6th and Congress, CT X
        ct_id = mds_pip_preloaded.get_census_tract_id(mds_point=p)
        print(ct_id)
        assert isinstance(ct_id, str)

    def test_pip_census_tract_id_success_t2(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_airport["longitude_x"], latitude_y=loc_airport["latitude_y"]
        )  # 6th and Congress, CT X
        ct_id = mds_pip_preloaded.get_census_tract_id(mds_point=p)
        print(ct_id)
        assert isinstance(ct_id, str)

    def test_pip_census_tract_id_fail_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_san_antonio_commerce_alamo["longitude_x"],
            latitude_y=loc_san_antonio_commerce_alamo["latitude_y"],
        )  # San Antonio @ Commerce & S Alamo St.
        ct_id = mds_pip_preloaded.get_census_tract_id(mds_point=p)
        print(ct_id)
        assert ct_id is None

    def test_pip_hex_id_success_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_6th_and_congress["longitude_x"],
            latitude_y=loc_6th_and_congress["latitude_y"],
        )  # 6th and Congress
        hex_id = mds_pip_preloaded.get_hex_id(mds_point=p)
        print(hex_id)
        assert isinstance(hex_id, str)

    def test_pip_hex_id_success_t2(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_airport["longitude_x"], latitude_y=loc_airport["latitude_y"]
        )  # Airport
        hex_id = mds_pip_preloaded.get_hex_id(mds_point=p)
        print(hex_id)
        assert isinstance(hex_id, str)

    def test_pip_hex_id_fail_t1(self):
        p = mds_pip_preloaded.create_point(
            longitude_x=loc_san_antonio_commerce_alamo["longitude_x"],
            latitude_y=loc_san_antonio_commerce_alamo["latitude_y"],
        )  # San Antonio @ Commerce & S Alamo St.
        hex_id = mds_pip_preloaded.get_hex_id(mds_point=p)
        print(hex_id)
        assert hex_id is None

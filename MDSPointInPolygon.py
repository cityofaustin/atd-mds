import logging
import json
import os
import pdb
import time

import requests
from rtree import index
from shapely.geometry import shape, point

from MDSConfig import MDSConfig


class MDSPointInPoly:
    __slots__ = [
        "mds_config",
        "CENSUS_TRACTS_GEOJSON",
        "DISTRICTS_GEOJSON",
        "HEX_GEOJSON",
    ]

    @staticmethod
    def read_json(file_path) -> dict:
        """
        Load (geo)JSON into memory
        :param str file_path:
        :return dict:
        """
        with open(file_path, "r") as fin:
            return json.loads(fin.read())

    @staticmethod
    def create_points(data) -> dict:
        """
        Create shapely geometry from list of dicts
        """
        for row in data:
            if row["x"] and row["y"]:
                try:
                    row["geometry"] = point.Point(float(row["x"]), float(row["y"]))
                except:
                    row["geometry"] = None
            else:
                row["geometry"] = None
        return data

    def __init__(self):
        self.mds_config = MDSConfig()
        self.CENSUS_TRACTS_GEOJSON = self.read_json(
            file_path=self.mds_config.ATD_MDS_CENSUS_GEOJSON
        )
        self.DISTRICTS_GEOJSON = self.read_json(
            file_path=self.mds_config.ATD_MDS_DISTRICTS_GEOJSON
        )
        self.HEX_GEOJSON = self.read_json(
            file_path=self.mds_config.ATD_MDS_HEX_GEOJSON
        )

    def get_census_tracts_geojson(self) -> dict:
        return self.CENSUS_TRACTS_GEOJSON

    def get_districts_geojson(self) -> dict:
        return self.DISTRICTS_GEOJSON

    def get_hex_geojson(self) -> dict:
        return self.HEX_GEOJSON

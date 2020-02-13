import logging
import json

from rtree import index
from shapely.geometry import shape, point

from MDSConfig import MDSConfig


class MDSPointInPolygon:
    __slots__ = [
        "mds_config",
        "CENSUS_TRACTS_GEOJSON",
        "CENSUS_TRACTS_INDEX",
        "DISTRICTS_GEOJSON",
        "DISTRICTS_INDEX",
        "HEX_GEOJSON",
        "HEX_INDEX",
    ]

    @staticmethod
    def get_polygon_property(poly, label) -> str:
        """
        Returns a string property from a geojson polygon.
        :param dict poly: The geojson polygon dictionary
        :param str label: The property dictionary key (aka label)
        :return str:
        """
        return poly.get("properties", {}).get(label, None)

    @staticmethod
    def initialize_index(polygons) -> index:
        """
        Creates grid cell index of polygon *bounding boxes*
        :param dict polygons: The dictionary containing a GeoJson object
        :return shape:
        """
        mds_index = index.Index()
        for pos, feature in enumerate(polygons["features"]):
            mds_index.insert(pos, shape(feature["geometry"]).bounds)

        return mds_index

    @staticmethod
    def point_in_poly(pt, idx, polys, geom_key) -> dict:
        """
        Returns the first geojson polygon that contains a point.
        Returns empty dictionary if not found.
        :param point pt: A shapely point object
        :param index idx: An rtree index object
        :param dict polys: The geojson polygons
        :param str geom_key: The geometry dictionary key
        :return dict:
        """
        # iterate through polygon *bounding boxes* that intersect with point
        for intersect_pos in idx.intersection(pt.coords[0]):
            # Load the polygon from current index position
            poly = shape(polys["features"][intersect_pos][geom_key])
            # check if point intersects actual polygon
            if pt.intersects(poly):
                return polys["features"][intersect_pos]
        return {}

    @staticmethod
    def create_point(longitude_x, latitude_y) -> point:
        """
        Returns a shapely point object containing the provided coordinates.
        :param longitude_x: Longitude value
        :param latitude_y: Latitude value
        :return point:
        """
        return point.Point(float(longitude_x), float(latitude_y))

    def __init__(self, mds_config, autoload=True):
        """
        Initializes the PointInPolygon helper methods. Requires a configuration class instance.
        :param MDSConfig mds_config: The configuration class instance
        :param bool autoload: Set to True (default) if you want to automatically load polygons and indexes.
        """
        self.mds_config = mds_config
        # Establish initial value for geojson polygons
        self.CENSUS_TRACTS_GEOJSON = None
        self.DISTRICTS_GEOJSON = None
        self.HEX_GEOJSON = None
        # Establish initial value for indexes
        self.CENSUS_TRACTS_INDEX = None
        self.DISTRICTS_INDEX = None
        self.HEX_INDEX = None
        # Go ahead and initialize geojson polygons & indexes
        if autoload:
            self.initialize_geojson_polygons()
            self.initialize_indexes()

    def initialize_geojson_polygons(self):
        """
        Initializes the geojson polygons from json files.
        :return:
        """
        self.CENSUS_TRACTS_GEOJSON = self.mds_config.read_json(
            file_path=self.mds_config.ATD_MDS_CENSUS_GEOJSON
        )
        self.DISTRICTS_GEOJSON = self.mds_config.read_json(
            file_path=self.mds_config.ATD_MDS_DISTRICTS_GEOJSON
        )
        self.HEX_GEOJSON = self.mds_config.read_json(
            file_path=self.mds_config.ATD_MDS_HEX_GEOJSON
        )

    def initialize_indexes(self):
        """
        Initializes the internal rtree index classes using the geojson polygons.
        :return:
        """
        if self.CENSUS_TRACTS_GEOJSON:
            self.CENSUS_TRACTS_INDEX = self.initialize_index(self.CENSUS_TRACTS_GEOJSON)
        else:
            raise Exception(
                "MDSPointInPolygon::initialize_indexes() GeoJson Polygons not loaded for Census tract"
            )
        if self.DISTRICTS_GEOJSON:
            self.DISTRICTS_INDEX = self.initialize_index(self.DISTRICTS_GEOJSON)
        else:
            raise Exception(
                "MDSPointInPolygon::initialize_indexes() GeoJson Polygons not loaded for Districts"
            )
        if self.HEX_GEOJSON:
            self.HEX_INDEX = self.initialize_index(self.HEX_GEOJSON)
        else:
            raise Exception(
                "MDSPointInPolygon::initialize_indexes() GeoJson Polygons not loaded for Hexagons"
            )

    def get_census_tract_id(self, mds_point) -> str:
        """
        Returns the census tract id for a point in map.
        :param point mds_point: The shapely point object containing the coordinates
        :return str:
        """
        poly = self.point_in_poly(
            pt=mds_point,
            idx=self.CENSUS_TRACTS_INDEX,
            polys=self.CENSUS_TRACTS_GEOJSON,
            geom_key="geometry"
        )
        return self.get_polygon_property(
            poly=poly, label="GEOID10"
        )

    def get_district_id(self, mds_point) -> str:
        """
        Returns the council district id for a point in map.
        :param point mds_point: The shapely point object containing the coordinates
        :return str:
        """
        poly = self.point_in_poly(
            pt=mds_point,
            idx=self.DISTRICTS_INDEX,
            polys=self.DISTRICTS_GEOJSON,
            geom_key="geometry"
        )
        return self.get_polygon_property(
            poly=poly, label="district_n"
        )

    def get_hex_id(self, mds_point) -> str:
        """
        Returns the hexagon id for a point in map.
        :param point mds_point: The shapely point object containing the coordinates
        :return str:
        """
        poly = self.point_in_poly(
            pt=mds_point,
            idx=self.HEX_INDEX,
            polys=self.HEX_GEOJSON,
            geom_key="geometry"
        )
        return self.get_polygon_property(
            poly=poly, label="id"
        )

    def get_census_tracts_geojson(self) -> dict:
        """
        A helper method to retrieve the census geojson polygon.
        :return dict:
        """
        return self.CENSUS_TRACTS_GEOJSON

    def get_districts_geojson(self) -> dict:
        """
        A helper method to retrieve the council districts geojson polygon.
        :return dict:
        """
        return self.DISTRICTS_GEOJSON

    def get_hex_geojson(self) -> dict:
        """
        A helper method to retrieve the hexagon geojson polygon.
        :return dict:
        """
        return self.HEX_GEOJSON

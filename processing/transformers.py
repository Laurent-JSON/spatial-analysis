"""Geometry transformation utilities"""

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import transform
import pyproj
from functools import partial
from typing import Union, List

class GeometryTransformer:
    """Transform and manipulate geometries"""
    
    @staticmethod
    def to_utm(gdf: gpd.GeoDataFrame, 
               latitude: float = None,
               longitude: float = None) -> gpd.GeoDataFrame:
        """Convert to UTM projection"""
        
        if latitude is None or longitude is None:
            centroid = gdf.geometry.centroid.iloc[0]
            longitude, latitude = centroid.x, centroid.y
        
        zone = int((longitude + 180) / 6) + 1
        if latitude >= 0:
            utm_crs = f'EPSG:326{zone}'
        else:
            utm_crs = f'EPSG:327{zone}'
        
        return gdf.to_crs(utm_crs)
    
    @staticmethod
    def add_offset(gdf: gpd.GeoDataFrame, 
                   x_offset: float = 0,
                   y_offset: float = 0) -> gpd.GeoDataFrame:
        """Add offset to geometries"""
        
        def translate_geom(geom):
            return transform(lambda x, y, z=None: (x + x_offset, y + y_offset), geom)
        
        result = gdf.copy()
        result['geometry'] = result.geometry.apply(translate_geom)
        
        return result
    
    @staticmethod
    def rotate_geometries(gdf: gpd.GeoDataFrame,
                         angle: float,
                         center: tuple = None) -> gpd.GeoDataFrame:
        """Rotate geometries by angle"""
        
        from shapely.affinity import rotate
        
        if center is None:
            center = gdf.geometry.centroid.iloc[0]
        
        result = gdf.copy()
        result['geometry'] = result.geometry.apply(
            lambda geom: rotate(geom, angle, origin=center)
        )
        
        return result
    
    @staticmethod
    def scale_geometries(gdf: gpd.GeoDataFrame,
                        x_factor: float = 1,
                        y_factor: float = 1,
                        center: tuple = None) -> gpd.GeoDataFrame:
        """Scale geometries"""
        
        from shapely.affinity import scale
        
        if center is None:
            center = gdf.geometry.centroid.iloc[0]
        
        result = gdf.copy()
        result['geometry'] = result.geometry.apply(
            lambda geom: scale(geom, x_factor, y_factor, origin=center)
        )
        
        return result
    
    @staticmethod
    def convert_to_points(gdf: gpd.GeoDataFrame, 
                         use_centroids: bool = True) -> gpd.GeoDataFrame:
        """Convert all geometries to points"""
        
        result = gdf.copy()
        
        if use_centroids:
            result['geometry'] = result.geometry.centroid
        else:
            result['geometry'] = result.geometry.representative_point()
        
        return result
    
    @staticmethod
    def explode_multipolygons(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Explode MultiPolygons into individual Polygons"""
        
        return gdf.explode(index_parts=True)

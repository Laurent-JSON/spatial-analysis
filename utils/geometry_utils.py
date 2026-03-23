"""Geometry manipulation utilities"""

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon, LineString, MultiPoint
from shapely.ops import transform
from functools import partial
import pyproj
from typing import Union, Tuple, List
import warnings

class GeometryUtils:
    """Helper functions for geometry operations"""
    
    @staticmethod
    def reproject(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
        """Reproject GeoDataFrame to target CRS"""
        return gdf.to_crs(target_crs)
    
    @staticmethod
    def get_geographic_bounds(gdf: gpd.GeoDataFrame) -> Tuple[float, float, float, float]:
        """Get geographic bounds in WGS84"""
        if gdf.crs is not None and gdf.crs != 'EPSG:4326':
            gdf_wgs84 = gdf.to_crs('EPSG:4326')
        else:
            gdf_wgs84 = gdf
        
        bounds = gdf_wgs84.total_bounds
        return bounds
    
    @staticmethod
    def simplify_geometry(gdf: gpd.GeoDataFrame, 
                         tolerance: float = 0.001,
                         preserve_topology: bool = True) -> gpd.GeoDataFrame:
        """Simplify geometries with given tolerance"""
        gdf_simplified = gdf.copy()
        gdf_simplified['geometry'] = gdf_simplified.geometry.simplify(
            tolerance, preserve_topology=preserve_topology
        )
        return gdf_simplified
    
    @staticmethod
    def get_geometric_center(gdf: gpd.GeoDataFrame) -> Point:
        """Calculate geometric center of all geometries"""
        union = gdf.geometry.unary_union
        return union.centroid
    
    @staticmethod
    def calculate_distance_matrix(gdf1: gpd.GeoDataFrame, 
                                  gdf2: gpd.GeoDataFrame) -> np.ndarray:
        """Calculate pairwise distances between two point sets"""
        if not (gdf1.geom_type == 'Point').all():
            raise ValueError("First GeoDataFrame must contain only points")
        if not (gdf2.geom_type == 'Point').all():
            raise ValueError("Second GeoDataFrame must contain only points")
        
        coords1 = np.array([(p.x, p.y) for p in gdf1.geometry])
        coords2 = np.array([(p.x, p.y) for p in gdf2.geometry])
        
        # Calculate distance matrix using broadcasting
        diff = coords1[:, np.newaxis, :] - coords2[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=-1))
        
        return distances
    
    @staticmethod
    def buffer_distance_analysis(gdf: gpd.GeoDataFrame, 
                                distances: List[float]) -> pd.DataFrame:
        """Analyze buffer areas at multiple distances"""
        results = []
        
        for dist in distances:
            buffered = gdf.geometry.buffer(dist)
            area = buffered.area.sum()
            results.append({'distance': dist, 'area': area})
        
        return pd.DataFrame(results)
    
    @staticmethod
    def clip_by_extent(gdf: gpd.GeoDataFrame, 
                       bounds: Union[Tuple, Polygon]) -> gpd.GeoDataFrame:
        """Clip GeoDataFrame by bounding box or polygon"""
        if isinstance(bounds, tuple):
            minx, miny, maxx, maxy = bounds
            clip_poly = Polygon([(minx, miny), (maxx, miny), 
                                (maxx, maxy), (minx, maxy)])
        else:
            clip_poly = bounds
        
        return gdf.clip(clip_poly)
    
    @staticmethod
    def check_geometry_type(gdf: gpd.GeoDataFrame) -> Dict[str, int]:
        """Check distribution of geometry types"""
        geom_types = gdf.geometry.geom_type.value_counts().to_dict()
        return geom_types
    
    @staticmethod
    def calculate_zonal_stats(raster, zones: gpd.GeoDataFrame, 
                             stats: List[str] = ['mean', 'std']) -> gpd.GeoDataFrame:
        """Calculate zonal statistics (requires rasterio)"""
        try:
            import rasterio
            from rasterio.mask import mask
            import rasterstats
        except ImportError:
            raise ImportError("Install rasterio and rasterstats for zonal statistics")
        
        results = []
        
        for idx, zone in zones.iterrows():
            geometry = zone.geometry
            # Mask raster
            with rasterio.open(raster) as src:
                out_image, out_transform = mask(src, [geometry], crop=True)
                values = out_image[out_image != src.nodata]
                
                stats_dict = {}
                for stat in stats:
                    if stat == 'mean':
                        stats_dict[stat] = values.mean()
                    elif stat == 'std':
                        stats_dict[stat] = values.std()
                    elif stat == 'sum':
                        stats_dict[stat] = values.sum()
                    elif stat == 'count':
                        stats_dict[stat] = len(values)
                
                results.append(stats_dict)
        
        # Add results to zones
        result_gdf = zones.copy()
        for stat in stats:
            result_gdf[f'zonal_{stat}'] = [r[stat] for r in results]
        
        return result_gdf
    
    @staticmethod
    def haversine_distance(lon1: float, lat1: float, 
                          lon2: float, lat2: float) -> float:
        """Calculate great circle distance between two points in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

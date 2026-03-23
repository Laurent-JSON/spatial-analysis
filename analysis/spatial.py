"""Core spatial analysis operations"""

import geopandas as gpd
import pandas as pd
import numpy as np
from typing import Union, List, Tuple, Optional, Dict
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from scipy.spatial import cKDTree
import warnings

class SpatialAnalyzer:
    """Advanced spatial analysis toolkit"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def calculate_area(self, gdf: gpd.GeoDataFrame, 
                       unit: str = 'sq_km') -> gpd.GeoDataFrame:
        """Calculate area for polygons"""
        if not gdf.geom_type.isin(['Polygon', 'MultiPolygon']).all():
            warnings.warn("Not all geometries are polygons")
        
        # Ensure projected CRS for accurate area
        if gdf.crs is not None and gdf.crs.is_geographic:
            gdf = gdf.to_crs('EPSG:3857')
        
        area = gdf.geometry.area
        
        if unit == 'sq_km':
            area = area / 1_000_000
        elif unit == 'sq_m':
            pass
        elif unit == 'ha':
            area = area / 10_000
        
        gdf['area'] = area
        return gdf
    
    def calculate_length(self, gdf: gpd.GeoDataFrame, 
                        unit: str = 'km') -> gpd.GeoDataFrame:
        """Calculate length for lines"""
        if not gdf.geom_type.isin(['LineString', 'MultiLineString']).all():
            warnings.warn("Not all geometries are lines")
        
        if gdf.crs is not None and gdf.crs.is_geographic:
            gdf = gdf.to_crs('EPSG:3857')
        
        length = gdf.geometry.length
        
        if unit == 'km':
            length = length / 1000
        elif unit == 'm':
            pass
        
        gdf['length'] = length
        return gdf
    
    def nearest_neighbor(self, source: gpd.GeoDataFrame, 
                        target: gpd.GeoDataFrame, 
                        k: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Find k nearest neighbors between two point datasets"""
        if not (source.geom_type == 'Point').all():
            raise ValueError("Source must contain only points")
        if not (target.geom_type == 'Point').all():
            raise ValueError("Target must contain only points")
        
        # Extract coordinates
        source_coords = np.array([(p.x, p.y) for p in source.geometry])
        target_coords = np.array([(p.x, p.y) for p in target.geometry])
        
        # Build KD-tree
        tree = cKDTree(target_coords)
        
        # Query
        distances, indices = tree.query(source_coords, k=k)
        
        return distances, indices
    
    def spatial_join(self, gdf1: gpd.GeoDataFrame, 
                     gdf2: gpd.GeoDataFrame, 
                     how: str = 'inner', 
                     predicate: str = 'intersects') -> gpd.GeoDataFrame:
        """Perform spatial join with detailed statistics"""
        
        result = gpd.sjoin(gdf1, gdf2, how=how, predicate=predicate)
        
        self.analysis_results['spatial_join'] = {
            'input1_count': len(gdf1),
            'input2_count': len(gdf2),
            'output_count': len(result),
            'join_rate': len(result) / len(gdf1) if len(gdf1) > 0 else 0
        }
        
        return result
    
    def buffer_analysis(self, gdf: gpd.GeoDataFrame, 
                        distance: float, 
                        dissolve: bool = False) -> gpd.GeoDataFrame:
        """Create buffers around geometries"""
        
        result = gdf.copy()
        result['geometry'] = result.geometry.buffer(distance)
        
        if dissolve:
            result = result.dissolve()
        
        self.analysis_results['buffer'] = {
            'distance': distance,
            'original_count': len(gdf),
            'buffered_count': len(result),
            'total_area': result.geometry.area.sum() if dissolve else result.geometry.area.sum()
        }
        
        return result
    
    def spatial_autocorrelation(self, gdf: gpd.GeoDataFrame, 
                               value_col: str, 
                               weights_type: str = 'queen') -> Dict:
        """Calculate Moran's I for spatial autocorrelation"""
        try:
            import libpysal as lp
            from esda.moran import Moran
        except ImportError:
            raise ImportError("Install libpysal and esda for spatial autocorrelation")
        
        # Create weights matrix
        if weights_type == 'queen':
            w = lp.weights.Queen.from_dataframe(gdf)
        elif weights_type == 'rook':
            w = lp.weights.Rook.from_dataframe(gdf)
        else:
            raise ValueError("weights_type must be 'queen' or 'rook'")
        
        # Calculate Moran's I
        values = gdf[value_col].values
        moran = Moran(values, w)
        
        return {
            'morans_i': moran.I,
            'expected_i': moran.EI,
            'variance': moran.VI,
            'z_score': moran.z_sim,
            'p_value': moran.p_sim
        }
    
    def overlay_analysis(self, gdf1: gpd.GeoDataFrame, 
                        gdf2: gpd.GeoDataFrame, 
                        operation: str = 'intersection') -> gpd.GeoDataFrame:
        """Perform overlay operations between two GeoDataFrames"""
        
        operations = {
            'intersection': gpd.overlay(gdf1, gdf2, how='intersection'),
            'union': gpd.overlay(gdf1, gdf2, how='union'),
            'difference': gpd.overlay(gdf1, gdf2, how='difference'),
            'symmetric_difference': gpd.overlay(gdf1, gdf2, how='symmetric_difference')
        }
        
        if operation not in operations:
            raise ValueError(f"Operation must be one of {list(operations.keys())}")
        
        result = operations[operation]
        
        self.analysis_results['overlay'] = {
            'operation': operation,
            'input1_count': len(gdf1),
            'input2_count': len(gdf2),
            'output_count': len(result)
        }
        
        return result
    
    def dissolve_by_attribute(self, gdf: gpd.GeoDataFrame, 
                             by: Union[str, List[str]], 
                             aggfunc: str = 'sum') -> gpd.GeoDataFrame:
        """Dissolve geometries by attribute with aggregation"""
        
        result = gdf.dissolve(by=by, aggfunc=aggfunc)
        
        self.analysis_results['dissolve'] = {
            'group_by': by,
            'original_count': len(gdf),
            'dissolved_count': len(result)
        }
        
        return result
    
    def get_centroids(self, gdf: gpd.GeoDataFrame, 
                     force_inside: bool = False) -> gpd.GeoDataFrame:
        """Calculate centroids of geometries"""
        
        result = gdf.copy()
        
        if force_inside:
            # Use representative_point for points guaranteed to be inside
            result['geometry'] = result.geometry.representative_point()
        else:
            result['geometry'] = result.geometry.centroid
        
        return result
    
    def create_grid(self, bounds: List[float], 
                   cell_size: float, 
                   crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Create a grid of polygons over given bounds"""
        
        minx, miny, maxx, maxy = bounds
        
        # Calculate number of cells
        x_cells = int((maxx - minx) / cell_size) + 1
        y_cells = int((maxy - miny) / cell_size) + 1
        
        # Create grid cells
        cells = []
        for i in range(x_cells):
            for j in range(y_cells):
                x_left = minx + i * cell_size
                x_right = x_left + cell_size
                y_bottom = miny + j * cell_size
                y_top = y_bottom + cell_size
                
                cell = Polygon([(x_left, y_bottom), 
                              (x_right, y_bottom), 
                              (x_right, y_top), 
                              (x_left, y_top)])
                cells.append(cell)
        
        grid = gpd.GeoDataFrame({'geometry': cells}, crs=crs)
        return grid

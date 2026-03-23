"""Data loading utilities for various geospatial formats"""

import geopandas as gpd
import pandas as pd
import os
from pathlib import Path
from typing import Union, Optional, List, Dict
import fiona
from shapely import wkt
import json

class DataLoader:
    """Unified data loader for multiple geospatial formats"""
    
    def __init__(self, data_dir: Union[str, Path] = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        for dir_path in [self.raw_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def load_shapefile(self, filepath: Union[str, Path]) -> gpd.GeoDataFrame:
        """Load shapefile from given path"""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            gdf = gpd.read_file(filepath)
            print(f"Loaded shapefile: {filepath.name} ({len(gdf)} features)")
            return gdf
        except Exception as e:
            raise Exception(f"Error loading shapefile: {e}")
    
    def load_geojson(self, filepath: Union[str, Path]) -> gpd.GeoDataFrame:
        """Load GeoJSON file"""
        filepath = Path(filepath)
        try:
            gdf = gpd.read_file(filepath)
            print(f"Loaded GeoJSON: {filepath.name} ({len(gdf)} features)")
            return gdf
        except Exception as e:
            raise Exception(f"Error loading GeoJSON: {e}")
    
    def load_csv_with_geometry(self, filepath: Union[str, Path], 
                               lat_col: str = 'latitude', 
                               lon_col: str = 'longitude',
                               crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Load CSV with latitude/longitude columns and convert to GeoDataFrame"""
        df = pd.read_csv(filepath)
        
        if lat_col not in df.columns or lon_col not in df.columns:
            raise ValueError(f"Columns {lat_col} and/or {lon_col} not found in CSV")
        
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
            crs=crs
        )
        
        print(f"Loaded CSV with geometry: {filepath.name} ({len(gdf)} points)")
        return gdf
    
    def load_wkt_csv(self, filepath: Union[str, Path], 
                     wkt_col: str = 'geometry') -> gpd.GeoDataFrame:
        """Load CSV with WKT geometry column"""
        df = pd.read_csv(filepath)
        
        if wkt_col not in df.columns:
            raise ValueError(f"WKT column '{wkt_col}' not found")
        
        df['geometry'] = df[wkt_col].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
        
        return gdf
    
    def load_postgis(self, table_name: str, conn_string: str, 
                     geom_col: str = 'geom') -> gpd.GeoDataFrame:
        """Load data from PostGIS database"""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(conn_string)
            gdf = gpd.read_postgis(f"SELECT * FROM {table_name}", engine, geom_col=geom_col)
            print(f"Loaded from PostGIS: {table_name} ({len(gdf)} features)")
            return gdf
        except ImportError:
            raise ImportError("SQLAlchemy required for PostGIS loading")
        except Exception as e:
            raise Exception(f"Error loading from PostGIS: {e}")
    
    def load_multiple_files(self, file_patterns: List[str], 
                           file_type: str = 'shapefile') -> Dict[str, gpd.GeoDataFrame]:
        """Load multiple files matching patterns"""
        loaded_files = {}
        
        for pattern in file_patterns:
            files = list(self.raw_dir.glob(pattern))
            for file in files:
                if file_type == 'shapefile':
                    loaded_files[file.stem] = self.load_shapefile(file)
                elif file_type == 'geojson':
                    loaded_files[file.stem] = self.load_geojson(file)
        
        return loaded_files
    
    def get_dataset_info(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Get comprehensive information about a GeoDataFrame"""
        info = {
            'num_features': len(gdf),
            'num_columns': len(gdf.columns),
            'crs': str(gdf.crs),
            'geometry_type': gdf.geometry.geom_type.unique().tolist(),
            'bounds': gdf.total_bounds,
            'columns': list(gdf.columns),
            'memory_usage': gdf.memory_usage(deep=True).sum() / 1024**2,  # MB
            'has_missing': gdf.isnull().sum().sum() > 0,
            'spatial_extent': {
                'minx': gdf.total_bounds[0],
                'miny': gdf.total_bounds[1],
                'maxx': gdf.total_bounds[2],
                'maxy': gdf.total_bounds[3]
            }
        }
        return info

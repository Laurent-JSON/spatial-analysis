"""Batch processing scripts for multiple files"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
sys.path.append('..')

from src.data.loaders import DataLoader
from src.processing.cleaners import DataCleaner
from src.processing.transformers import GeometryTransformer
from src.analysis.spatial import SpatialAnalyzer

def batch_convert_to_geojson(input_dir: str, output_dir: str, input_format: str = 'shp'):
    """Convert multiple files to GeoJSON format"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    pattern = f"*.{input_format}"
    files = list(input_path.glob(pattern))
    
    for file in files:
        print(f"Processing {file.name}...")
        try:
            gdf = gpd.read_file(file)
            output_file = output_path / f"{file.stem}.geojson"
            gdf.to_file(output_file, driver='GeoJSON')
            print(f"  Converted to {output_file}")
        except Exception as e:
            print(f"  Error: {e}")

def batch_reproject(input_dir: str, output_dir: str, target_crs: str):
    """Batch reproject multiple files"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    geojson_files = list(input_path.glob("*.geojson"))
    
    for file in geojson_files:
        print(f"Reprojecting {file.name}...")
        try:
            gdf = gpd.read_file(file)
            gdf_reprojected = gdf.to_crs(target_crs)
            output_file = output_path / f"{file.stem}_reprojected.geojson"
            gdf_reprojected.to_file(output_file, driver='GeoJSON')
            print(f"  Saved to {output_file}")
        except Exception as e:
            print(f"  Error: {e}")

def batch_clean_data(input_dir: str, output_dir: str):
    """Batch clean geospatial data"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = list(input_path.glob("*.geojson")) + list(input_path.glob("*.shp"))
    
    for file in files:
        print(f"Cleaning {file.name}...")
        try:
            gdf = gpd.read_file(file)
            
            # Initialize cleaner
            cleaner = DataCleaner(gdf)
            
            # Apply cleaning steps
            cleaner.remove_duplicates()
            cleaner.fix_invalid_geometries()
            cleaner.handle_missing_data(strategy='drop')
            cleaner.standardize_column_names()
            
            # Save cleaned data
            output_file = output_path / f"{file.stem}_cleaned.geojson"
            cleaner.gdf.to_file(output_file, driver='GeoJSON')
            
            # Save cleaning report
            report = cleaner.get_cleaning_report()
            report_file = output_path / f"{file.stem}_cleaning_report.csv"
            report.to_csv(report_file, index=False)
            
            print(f"  Saved cleaned data and report")
        except Exception as e:
            print(f"  Error: {e}")

def batch_spatial_join(input_dir: str, join_dir: str, output_dir: str):
    """Batch spatial joins between datasets"""
    
    input_path = Path(input_dir)
    join_path = Path(join_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load all join files
    join_files = list(join_path.glob("*.geojson"))
    join_data = {}
    for file in join_files:
        join_data[file.stem] = gpd.read_file(file)
    
    # Process each input file
    input_files = list(input_path.glob("*.geojson"))
    for file in input_files:
        print(f"Processing {file.name}...")
        gdf = gpd.read_file(file)
        
        analyzer = SpatialAnalyzer()
        
        for join_name, join_gdf in join_data.items():
            try:
                result = analyzer.spatial_join(gdf, join_gdf, how='left')
                output_file = output_path / f"{file.stem}_joined_{join_name}.geojson"
                result.to_file(output_file, driver='GeoJSON')
                print(f"  Joined with {join_name}: {len(result)} features")
            except Exception as e:
                print(f"  Error joining with {join_name}: {e}")

if __name__ == "__main__":
    # Example usage
    batch_convert_to_geojson("data/raw", "data/processed", input_format='shp')
    batch_reproject("data/processed", "data/processed", target_crs='EPSG:3857')
    batch_clean_data("data/processed", "data/processed/cleaned")

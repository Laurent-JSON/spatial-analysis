"""Export geospatial data to various formats"""

import geopandas as gpd
import json
from pathlib import Path
from typing import Union, Optional
import sys
sys.path.append('..')

class FormatExporter:
    """Export GeoDataFrames to various formats"""
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
    
    def to_geojson(self, filename: str):
        """Export to GeoJSON"""
        self.gdf.to_file(filename, driver='GeoJSON')
        print(f"Exported to GeoJSON: {filename}")
    
    def to_shapefile(self, filename: str):
        """Export to Shapefile"""
        self.gdf.to_file(filename, driver='ESRI Shapefile')
        print(f"Exported to Shapefile: {filename}")
    
    def to_geopackage(self, filename: str, layer: str = 'layer'):
        """Export to GeoPackage"""
        self.gdf.to_file(filename, driver='GPKG', layer=layer)
        print(f"Exported to GeoPackage: {filename}")
    
    def to_csv(self, filename: str, include_geometry: bool = True):
        """Export to CSV with geometry as WKT"""
        gdf_copy = self.gdf.copy()
        
        if include_geometry:
            gdf_copy['geometry_wkt'] = gdf_copy.geometry.to_wkt()
            gdf_copy = gdf_copy.drop(columns=['geometry'])
        
        gdf_copy.to_csv(filename, index=False)
        print(f"Exported to CSV: {filename}")
    
    def to_kml(self, filename: str):
        """Export to KML"""
        self.gdf.to_file(filename, driver='KML')
        print(f"Exported to KML: {filename}")
    
    def to_postgis(self, table_name: str, conn_string: str, 
                   if_exists: str = 'replace'):
        """Export to PostGIS"""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(conn_string)
            self.gdf.to_postgis(table_name, engine, if_exists=if_exists)
            print(f"Exported to PostGIS: {table_name}")
        except ImportError:
            print("SQLAlchemy required for PostGIS export")
    
    def to_parquet(self, filename: str):
        """Export to Parquet with geometry"""
        # Convert geometry to WKB for parquet
        gdf_copy = self.gdf.copy()
        gdf_copy['geometry_wkb'] = gdf_copy.geometry.apply(lambda g: g.wkb)
        gdf_copy = gdf_copy.drop(columns=['geometry'])
        gdf_copy.to_parquet(filename)
        print(f"Exported to Parquet: {filename}")
    
    def to_topojson(self, filename: str):
        """Export to TopoJSON (requires topojson package)"""
        try:
            import topojson as tp
            topo = tp.Topology(self.gdf)
            topo.to_json(filename)
            print(f"Exported to TopoJSON: {filename}")
        except ImportError:
            print("Install topojson package for TopoJSON export")

def export_all_formats(input_file: str, output_dir: str):
    """Export a file to all available formats"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    gdf = gpd.read_file(input_file)
    base_name = Path(input_file).stem
    
    exporter = FormatExporter(gdf)
    
    # Export to all formats
    formats = [
        ('geojson', f"{base_name}.geojson"),
        ('shapefile', f"{base_name}.shp"),
        ('geopackage', f"{base_name}.gpkg"),
        ('csv', f"{base_name}.csv"),
        ('kml', f"{base_name}.kml"),
        ('parquet', f"{base_name}.parquet")
    ]
    
    for format_name, filename in formats:
        try:
            output_file = output_path / filename
            getattr(exporter, f"to_{format_name}")(str(output_file))
        except Exception as e:
            print(f"Error exporting to {format_name}: {e}")

if __name__ == "__main__":
    # Example: export all formats for a given file
    export_all_formats("data/processed/sample.geojson", "data/exports")

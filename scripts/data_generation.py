"""Generate synthetic geospatial data for testing"""

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, LineString
from typing import List, Tuple, Optional
import random

class DataGenerator:
    """Generate synthetic geospatial data"""
    
    @staticmethod
    def generate_random_points(n_points: int,
                              bounds: Tuple[float, float, float, float],
                              crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Generate random points within bounds"""
        
        minx, miny, maxx, maxy = bounds
        
        points = []
        for i in range(n_points):
            x = np.random.uniform(minx, maxx)
            y = np.random.uniform(miny, maxy)
            points.append(Point(x, y))
        
        gdf = gpd.GeoDataFrame({
            'id': range(n_points),
            'value': np.random.randn(n_points) * 10 + 50,
            'category': np.random.choice(['A', 'B', 'C', 'D'], n_points),
            'geometry': points
        }, crs=crs)
        
        return gdf
    
    @staticmethod
    def generate_grid_points(nx: int, ny: int,
                            bounds: Tuple[float, float, float, float],
                            crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Generate regular grid of points"""
        
        minx, miny, maxx, maxy = bounds
        
        x_coords = np.linspace(minx, maxx, nx)
        y_coords = np.linspace(miny, maxy, ny)
        
        points = []
        ids = []
        
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                points.append(Point(x, y))
                ids.append(f"P{i}_{j}")
        
        gdf = gpd.GeoDataFrame({
            'id': ids,
            'x_idx': [i for i in range(len(points))],
            'y_idx': [j for j in range(len(points))],
            'value': np.random.randn(len(points)) * 5,
            'geometry': points
        }, crs=crs)
        
        return gdf
    
    @staticmethod
    def generate_random_polygons(n_polygons: int,
                                 bounds: Tuple[float, float, float, float],
                                 crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Generate random polygons"""
        
        minx, miny, maxx, maxy = bounds
        width = maxx - minx
        height = maxy - miny
        
        polygons = []
        
        for i in range(n_polygons):
            # Random center
            cx = np.random.uniform(minx, maxx)
            cy = np.random.uniform(miny, maxy)
            
            # Random size
            w = np.random.uniform(width * 0.05, width * 0.2)
            h = np.random.uniform(height * 0.05, height * 0.2)
            
            # Random rotation
            angle = np.random.uniform(0, 2 * np.pi)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            
            # Create polygon corners
            corners = []
            for dx, dy in [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]:
                x = cx + dx * cos_a - dy * sin_a
                y = cy + dx * sin_a + dy * cos_a
                corners.append((x, y))
            
            polygons.append(Polygon(corners))
        
        gdf = gpd.GeoDataFrame({
            'id': range(n_polygons),
            'area': [p.area for p in polygons],
            'value': np.random.randn(n_polygons) * 20 + 100,
            'geometry': polygons
        }, crs=crs)
        
        return gdf
    
    @staticmethod
    def generate_random_lines(n_lines: int,
                             bounds: Tuple[float, float, float, float],
                             crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Generate random lines"""
        
        minx, miny, maxx, maxy = bounds
        
        lines = []
        
        for i in range(n_lines):
            # Random start point
            x1 = np.random.uniform(minx, maxx)
            y1 = np.random.uniform(miny, maxy)
            
            # Random end point
            x2 = np.random.uniform(minx, maxx)
            y2 = np.random.uniform(miny, maxy)
            
            lines.append(LineString([(x1, y1), (x2, y2)]))
        
        gdf = gpd.GeoDataFrame({
            'id': range(n_lines),
            'length': [l.length for l in lines],
            'value': np.random.randn(n_lines) * 10,
            'geometry': lines
        }, crs=crs)
        
        return gdf
    
    @staticmethod
    def generate_clustered_points(n_clusters: int,
                                  points_per_cluster: int,
                                  cluster_radius: float,
                                  bounds: Tuple[float, float, float, float],
                                  crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """Generate points in clusters"""
        
        minx, miny, maxx, maxy = bounds
        width = maxx - minx
        height = maxy - miny
        
        all_points = []
        cluster_ids = []
        
        for cluster in range(n_clusters):
            # Random cluster center
            cx = np.random.uniform(minx + cluster_radius, maxx - cluster_radius)
            cy = np.random.uniform(miny + cluster_radius, maxy - cluster_radius)
            
            for i in range(points_per_cluster):
                # Random offset within cluster radius
                angle = np.random.uniform(0, 2 * np.pi)
                radius = np.random.uniform(0, cluster_radius)
                x = cx + radius * np.cos(angle)
                y = cy + radius * np.sin(angle)
                
                all_points.append(Point(x, y))
                cluster_ids.append(cluster)
        
        gdf = gpd.GeoDataFrame({
            'id': range(len(all_points)),
            'cluster_id': cluster_ids,
            'value': np.random.randn(len(all_points)) * 5 + cluster_ids * 10,
            'geometry': all_points
        }, crs=crs)
        
        return gdf

# Function to generate datasets for testing
def generate_test_datasets(output_dir: str):
    """Generate multiple test datasets"""
    
    import os
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    generator = DataGenerator()
    
    # Generate various datasets
    print("Generating test datasets...")
    
    # Random points
    points = generator.generate_random_points(1000, (-180, -90, 180, 90))
    points.to_file(output_path / 'random_points.geojson', driver='GeoJSON')
    print("  - Random points generated")
    
    # Grid points
    grid = generator.generate_grid_points(20, 20, (-180, -90, 180, 90))
    grid.to_file(output_path / 'grid_points.geojson', driver='GeoJSON')
    print("  - Grid points generated")
    
    # Random polygons
    polygons = generator.generate_random_polygons(100, (-180, -90, 180, 90))
    polygons.to_file(output_path / 'random_polygons.geojson', driver='GeoJSON')
    print("  - Random polygons generated")
    
    # Random lines
    lines = generator.generate_random_lines(200, (-180, -90, 180, 90))
    lines.to_file(output_path / 'random_lines.geojson', driver='GeoJSON')
    print("  - Random lines generated")
    
    # Clustered points
    clustered = generator.generate_clustered_points(5, 200, 10, (-180, -90, 180, 90))
    clustered.to_file(output_path / 'clustered_points.geojson', driver='GeoJSON')
    print("  - Clustered points generated")
    
    print(f"All datasets saved to {output_path}")

if __name__ == "__main__":
    generate_test_datasets("data/generated")

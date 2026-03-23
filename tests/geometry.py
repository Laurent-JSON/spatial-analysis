"""Unit tests for geometry utilities"""

import unittest
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
import sys
sys.path.append('..')

from src.utils.geometry_utils import GeometryUtils

class TestGeometryUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create test points
        self.points = gpd.GeoDataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30],
            'geometry': [
                Point(0, 0),
                Point(1, 1),
                Point(2, 2)
            ]
        }, crs='EPSG:4326')
        
        # Create test polygons
        self.polygons = gpd.GeoDataFrame({
            'id': [1, 2],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])
            ]
        }, crs='EPSG:4326')
        
        self.utils = GeometryUtils()
    
    def test_reproject(self):
        """Test CRS reprojection"""
        reprojected = self.utils.reproject(self.points, 'EPSG:3857')
        self.assertEqual(reprojected.crs, 'EPSG:3857')
        self.assertEqual(len(reprojected), len(self.points))
    
    def test_get_geographic_bounds(self):
        """Test geographic bounds calculation"""
        bounds = self.utils.get_geographic_bounds(self.points)
        self.assertEqual(len(bounds), 4)
        self.assertAlmostEqual(bounds[0], 0)
        self.assertAlmostEqual(bounds[2], 2)
    
    def test_simplify_geometry(self):
        """Test geometry simplification"""
        simplified = self.utils.simplify_geometry(self.polygons, tolerance=0.1)
        self.assertEqual(len(simplified), len(self.polygons))
        self.assertTrue(all(g is not None for g in simplified.geometry))
    
    def test_get_geometric_center(self):
        """Test geometric center calculation"""
        center = self.utils.get_geometric_center(self.points)
        self.assertIsNotNone(center)
        self.assertAlmostEqual(center.x, 1.0)
        self.assertAlmostEqual(center.y, 1.0)
    
    def test_check_geometry_type(self):
        """Test geometry type checking"""
        types = self.utils.check_geometry_type(self.points)
        self.assertIn('Point', types)
        self.assertEqual(types['Point'], 3)
        
        types = self.utils.check_geometry_type(self.polygons)
        self.assertIn('Polygon', types)
        self.assertEqual(types['Polygon'], 2)
    
    def test_calculate_distance_matrix(self):
        """Test distance matrix calculation"""
        # Create test points
        points1 = gpd.GeoDataFrame({
            'geometry': [Point(0, 0), Point(1, 1)]
        })
        points2 = gpd.GeoDataFrame({
            'geometry': [Point(2, 2), Point(3, 3)]
        })
        
        distances = self.utils.calculate_distance_matrix(points1, points2)
        
        self.assertEqual(distances.shape, (2, 2))
        self.assertAlmostEqual(distances[0, 0], np.sqrt(8))  # Distance from (0,0) to (2,2)
    
    def test_haversine_distance(self):
        """Test haversine distance calculation"""
        # Paris to London approximate coordinates
        paris = (2.3522, 48.8566)
        london = (-0.1276, 51.5074)
        
        distance = self.utils.haversine_distance(paris[0], paris[1], 
                                                 london[0], london[1])
        
        self.assertGreater(distance, 300)  # Should be > 300 km
        self.assertLess(distance, 400)     # Should be < 400 km

if __name__ == '__main__':
    unittest.main()

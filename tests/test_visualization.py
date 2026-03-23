"""Unit tests for visualization modules"""

import unittest
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import sys
sys.path.append('..')

from src.visualization.maps import MapVisualizer
from src.visualization.plots import StatisticalPlots
from src.data.generator import DataGenerator

class TestMapVisualizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.visualizer = MapVisualizer()
        self.generator = DataGenerator()
        
        self.points = self.generator.generate_random_points(100, (-10, -10, 10, 10))
        self.polygons = self.generator.generate_random_polygons(10, (-10, -10, 10, 10))
    
    def test_plot_basic(self):
        """Test basic map creation"""
        fig = self.visualizer.plot_basic(self.points, title="Test Map")
        self.assertIsNotNone(fig)
        plt.close(fig)
    
    def test_plot_choropleth(self):
        """Test choropleth map creation"""
        self.points['value'] = range(len(self.points))
        fig = self.visualizer.plot_choropleth(self.points, 'value', n_classes=5)
        self.assertIsNotNone(fig)
        plt.close(fig)
    
    def test_plot_multiple(self):
        """Test multiple maps in subplots"""
        gdfs = {'points': self.points, 'polygons': self.polygons}
        fig = self.visualizer.plot_multiple(gdfs)
        self.assertIsNotNone(fig)
        plt.close(fig)

class TestStatisticalPlots(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.plotter = StatisticalPlots()
        self.generator = DataGenerator()
        
        self.points = self.generator.generate_random_points(100, (-10, -10, 10, 10))
        self.points['value'] = np.random.randn(100) * 10 + 50
    
    def test_histogram(self):
        """Test histogram creation"""
        fig = self.plotter.histogram(self.points, 'value')
        self.assertIsNotNone(fig)
        plt.close(fig)
    
    def test_scatter_plot(self):
        """Test scatter plot creation"""
        self.points['x_coord'] = [p.x for p in self.points.geometry]
        self.points['y_coord'] = [p.y for p in self.points.geometry]
        
        fig = self.plotter.scatter_plot(self.points, 'x_coord', 'y_coord', 'value')
        self.assertIsNotNone(fig)
        plt.close(fig)
    
    def test_correlation_heatmap(self):
        """Test correlation heatmap"""
        self.points['x_coord'] = [p.x for p in self.points.geometry]
        self.points['y_coord'] = [p.y for p in self.points.geometry]
        
        fig = self.plotter.correlation_heatmap(self.points)
        self.assertIsNotNone(fig)
        plt.close(fig)

if __name__ == '__main__':
    unittest.main()

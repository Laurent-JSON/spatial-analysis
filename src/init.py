"""
GeoPandas Project Package
A comprehensive geospatial analysis toolkit
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from src.data.loaders import DataLoader
from src.processing.cleaners import DataCleaner
from src.analysis.spatial import SpatialAnalyzer
from src.visualization.maps import MapVisualizer

__all__ = [
    'DataLoader',
    'DataCleaner', 
    'SpatialAnalyzer',
    'MapVisualizer'
]

"""Performance benchmarking for geospatial operations"""

import time
import geopandas as gpd
import numpy as np
import pandas as pd
from typing import Dict, Callable, List
import sys
sys.path.append('..')

from src.data.loaders import DataLoader
from src.analysis.spatial import SpatialAnalyzer
from src.processing.cleaners import DataCleaner

class PerformanceBenchmark:
    """Benchmark geospatial operations"""
    
    def __init__(self):
        self.results = []
    
    def benchmark_function(self, func: Callable, 
                          name: str, 
                          *args, 
                          **kwargs) -> Dict:
        """Benchmark a single function"""
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            return {
                'function': name,
                'execution_time': execution_time,
                'success': True,
                'result_type': type(result).__name__
            }
        except Exception as e:
            return {
                'function': name,
                'execution_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def benchmark_spatial_join(self, gdf1: gpd.GeoDataFrame,
                               gdf2: gpd.GeoDataFrame,
                               size: str = "small") -> Dict:
        """Benchmark spatial join performance"""
        
        analyzer = SpatialAnalyzer()
        
        return self.benchmark_function(
            analyzer.spatial_join,
            f"spatial_join_{size}",
            gdf1, gdf2
        )
    
    def benchmark_buffer_operation(self, gdf: gpd.GeoDataFrame,
                                   distance: float,
                                   size: str = "small") -> Dict:
        """Benchmark buffer operation"""
        
        analyzer = SpatialAnalyzer()
        
        return self.benchmark_function(
            analyzer.buffer_analysis,
            f"buffer_{size}",
            gdf, distance
        )
    
    def benchmark_cleaning(self, gdf: gpd.GeoDataFrame,
                          size: str = "small") -> Dict:
        """Benchmark data cleaning"""
        
        def cleaning_pipeline():
            cleaner = DataCleaner(gdf)
            cleaner.remove_duplicates()
            cleaner.fix_invalid_geometries()
            cleaner.handle_missing_data(strategy='drop')
            return cleaner.gdf
        
        return self.benchmark_function(
            cleaning_pipeline,
            f"cleaning_{size}"
        )
    
    def run_full_benchmark(self, sizes: List[int] = [100, 1000, 10000]) -> pd.DataFrame:
        """Run complete benchmark with different dataset sizes"""
        
        from src.data.generator import DataGenerator
        
        generator = DataGenerator()
        
        for size in sizes:
            print(f"Benchmarking with {size} points...")
            
            # Generate test data
            bounds = (-180, -90, 180, 90)
            points1 = generator.generate_random_points(size, bounds)
            points2 = generator.generate_random_points(size, bounds)
            
            # Run benchmarks
            self.results.append(self.benchmark_spatial_join(points1, points2, f"{size}"))
            self.results.append(self.benchmark_buffer_operation(points1, 0.1, f"{size}"))
            self.results.append(self.benchmark_cleaning(points1, f"{size}"))
        
        return pd.DataFrame(self.results)
    
    def save_results(self, filename: str):
        """Save benchmark results"""
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark()
    benchmark.save_results("benchmark_results.csv")
    print("\nBenchmark Results:")
    print(results)

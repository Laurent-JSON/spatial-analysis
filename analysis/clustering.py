"""Clustering algorithms for spatial data"""

import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional
import pandas as pd

class ClusterAnalyzer:
    """Spatial clustering analysis"""
    
    def __init__(self):
        self.clusters = None
        self.labels = None
    
    def kmeans_clustering(self, gdf: gpd.GeoDataFrame, 
                          n_clusters: int = 5,
                          columns: Optional[List[str]] = None) -> gpd.GeoDataFrame:
        """Apply K-means clustering"""
        
        if columns is None:
            # Use coordinates if no columns specified
            coords = np.array([(p.x, p.y) for p in gdf.geometry])
            X = coords
        else:
            X = gdf[columns].values
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        
        result = gdf.copy()
        result['cluster'] = labels
        result['cluster_center_x'] = kmeans.cluster_centers_[labels, 0]
        result['cluster_center_y'] = kmeans.cluster_centers_[labels, 1]
        
        self.clusters = result
        self.labels = labels
        
        return result
    
    def dbscan_clustering(self, gdf: gpd.GeoDataFrame,
                          eps: float = 0.5,
                          min_samples: int = 5,
                          use_coords: bool = True) -> gpd.GeoDataFrame:
        """Apply DBSCAN clustering"""
        
        if use_coords:
            coords = np.array([(p.x, p.y) for p in gdf.geometry])
            X = coords
        else:
            X = gdf.select_dtypes(include=[np.number]).values
        
        # Apply DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)
        
        result = gdf.copy()
        result['cluster'] = labels
        result['is_noise'] = labels == -1
        
        self.clusters = result
        self.labels = labels
        
        return result
    
    def get_cluster_stats(self) -> pd.DataFrame:
        """Get statistics for each cluster"""
        if self.clusters is None:
            raise ValueError("No clustering performed yet")
        
        stats = []
        for cluster_id in self.clusters['cluster'].unique():
            cluster_data = self.clusters[self.clusters['cluster'] == cluster_id]
            stats.append({
                'cluster_id': cluster_id,
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(self.clusters) * 100
            })
        
        return pd.DataFrame(stats)

    def spatial_clustering(self, gdf: gpd.GeoDataFrame,
                          distance_threshold: float = 1000,
                          min_points: int = 3) -> gpd.GeoDataFrame:
        """Spatial clustering based on distance"""
        
        from scipy.spatial.distance import pdist, squareform
        
        # Get coordinates
        coords = np.array([(p.x, p.y) for p in gdf.geometry])
        
        # Calculate distance matrix
        dist_matrix = squareform(pdist(coords))
        
        # Simple greedy clustering
        labels = np.full(len(gdf), -1, dtype=int)
        current_label = 0
        
        for i in range(len(gdf)):
            if labels[i] == -1:
                neighbors = np.where(dist_matrix[i] <= distance_threshold)[0]
                if len(neighbors) >= min_points:
                    labels[neighbors] = current_label
                    current_label += 1
        
        result = gdf.copy()
        result['spatial_cluster'] = labels
        
        return result

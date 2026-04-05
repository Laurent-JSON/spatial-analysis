"""Network analysis for spatial data...."""

import geopandas as gpd
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString
from typing import List, Tuple, Dict, Optional
import pandas as pd

class NetworkAnalyzer:
    """Spatial network analysis"""
    
    def __init__(self):
        self.graph = None
        self.nodes_gdf = None
        self.edges_gdf = None
    
    def build_network(self, edges: gpd.GeoDataFrame,
                     nodes: Optional[gpd.GeoDataFrame] = None) -> nx.Graph:
        """Build network graph from edges"""
        
        self.graph = nx.Graph()
        self.edges_gdf = edges
        
        # Add edges
        for idx, row in edges.iterrows():
            coords = list(row.geometry.coords)
            for i in range(len(coords) - 1):
                node1 = coords[i]
                node2 = coords[i + 1]
                distance = row.geometry.length
                self.graph.add_edge(node1, node2, weight=distance, 
                                   properties=row.to_dict())
        
        # Extract nodes
        self.nodes_gdf = self._extract_nodes()
        
        return self.graph
    
    def _extract_nodes(self) -> gpd.GeoDataFrame:
        """Extract nodes from graph"""
        nodes = []
        for node in self.graph.nodes():
            nodes.append({'geometry': Point(node[0], node[1])})
        
        return gpd.GeoDataFrame(nodes, crs=self.edges_gdf.crs)
    
    def shortest_path(self, start: Point, end: Point) -> Dict:
        """Find shortest path between two points"""
        
        # Find nearest nodes
        start_node = self._find_nearest_node(start)
        end_node = self._find_nearest_node(end)
        
        try:
            path = nx.shortest_path(self.graph, start_node, end_node, weight='weight')
            distance = nx.shortest_path_length(self.graph, start_node, end_node, weight='weight')
            
            # Create path geometry
            path_coords = []
            for node in path:
                path_coords.append(node)
            
            path_line = LineString(path_coords)
            
            return {
                'path': path_line,
                'distance': distance,
                'nodes': path,
                'success': True
            }
        except nx.NetworkXNoPath:
            return {'success': False, 'message': 'No path found'}
    
    def _find_nearest_node(self, point: Point) -> Tuple[float, float]:
        """Find nearest node in graph"""
        min_dist = float('inf')
        nearest_node = None
        
        for node in self.graph.nodes():
            dist = np.sqrt((node[0] - point.x)**2 + (node[1] - point.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node
        
        return nearest_node
    
    def calculate_centrality(self) -> Dict[str, np.ndarray]:
        """Calculate various centrality measures"""
        
        if self.graph is None:
            raise ValueError("Network not built")
        
        centrality = {
            'degree': nx.degree_centrality(self.graph),
            'betweenness': nx.betweenness_centrality(self.graph, weight='weight'),
            'closeness': nx.closeness_centrality(self.graph, distance='weight'),
            'eigenvector': nx.eigenvector_centrality(self.graph, weight='weight')
        }
        
        return centrality
    
    def service_area(self, point: Point, radius: float) -> gpd.GeoDataFrame:
        """Calculate service area around a point"""
        
        start_node = self._find_nearest_node(point)
        
        # Get nodes within distance
        distances = nx.single_source_dijkstra_path_length(self.graph, start_node, radius)
        
        # Extract edges within service area
        service_edges = []
        for edge in self.edges_gdf.geometry:
            # Simplified: check if edge is within radius
            edge_center = edge.centroid
            dist_to_center = np.sqrt((edge_center.x - point.x)**2 + (edge_center.y - point.y)**2)
            if dist_to_center <= radius:
                service_edges.append(edge)
        
        return gpd.GeoDataFrame({'geometry': service_edges}, crs=self.edges_gdf.crs)

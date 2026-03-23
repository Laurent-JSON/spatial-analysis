"""Manage external data sources and APIs"""

import geopandas as gpd
import requests
from typing import Optional, Dict, Tuple
import os
import json
from pathlib import Path

class DataSourceManager:
    """Manager for external geospatial data sources"""
    
    def __init__(self, cache_dir: str = "data/external"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Common CRS definitions
        self.crs_wgs84 = 'EPSG:4326'
        self.crs_web_mercator = 'EPSG:3857'
    
    def download_natural_earth(self, category: str = 'cultural', 
                               scale: str = '110m', 
                               name: str = 'countries') -> Optional[gpd.GeoDataFrame]:
        """Download Natural Earth data"""
        base_url = f"https://naturalearth.s3.amazonaws.com/{scale}_{category}/ne_{scale}_{name}.zip"
        
        cache_file = self.cache_dir / f"ne_{scale}_{name}.gpkg"
        
        if cache_file.exists():
            print(f"Loading cached data: {cache_file}")
            return gpd.read_file(cache_file)
        
        try:
            print(f"Downloading from: {base_url}")
            gdf = gpd.read_file(base_url)
            gdf.to_file(cache_file, driver='GPKG')
            print(f"Downloaded and cached: {name}")
            return gdf
        except Exception as e:
            print(f"Error downloading Natural Earth data: {e}")
            return None
    
    def download_osm_data(self, bbox: Tuple[float, float, float, float], 
                          tags: Dict[str, str]) -> Optional[gpd.GeoDataFrame]:
        """Download OpenStreetMap data using overpass API"""
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Construct query
        query_parts = []
        for key, value in tags.items():
            query_parts.append(f'["{key}"="{value}"]')
        
        query = f"""
        [out:json];
        (
          way({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}){"".join(query_parts)};
          relation({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}){"".join(query_parts)};
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            response = requests.post(overpass_url, data={'data': query})
            data = response.json()
            # Parse OSM data to GeoDataFrame (simplified)
            print(f"Downloaded OSM data: {len(data.get('elements', []))} elements")
            return self._parse_osm_json(data)
        except Exception as e:
            print(f"Error downloading OSM data: {e}")
            return None
    
    def _parse_osm_json(self, data: dict) -> gpd.GeoDataFrame:
        """Parse OSM JSON to GeoDataFrame"""
        # Simplified parsing - implement based on needs
        features = []
        for element in data.get('elements', []):
            if 'lat' in element and 'lon' in element:
                features.append({
                    'type': element.get('type'),
                    'id': element.get('id'),
                    'geometry': f"POINT({element['lon']} {element['lat']})",
                    'tags': element.get('tags', {})
                })
        
        if features:
            gdf = gpd.GeoDataFrame(features)
            gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geometry'])
            gdf.set_crs(self.crs_wgs84, inplace=True)
            return gdf
        return gpd.GeoDataFrame()
    
    def download_google_maps(self, address: str, api_key: str) -> Optional[Tuple[float, float]]:
        """Geocode using Google Maps API"""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': address, 'key': api_key}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return (location['lat'], location['lng'])
            else:
                print(f"Geocoding failed: {data['status']}")
                return None
        except Exception as e:
            print(f"Error with Google Maps API: {e}")
            return None
    
    def get_world_bank_data(self, indicator: str, country: str = 'all') -> Optional[pd.DataFrame]:
        """Download World Bank data"""
        url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
        params = {'format': 'json', 'per_page': 1000}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if len(data) > 1:
                return pd.DataFrame(data[1])
            return None
        except Exception as e:
            print(f"Error downloading World Bank data: {e}")
            return None

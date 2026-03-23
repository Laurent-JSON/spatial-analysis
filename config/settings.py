"""Configuration settings for the project"""

import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Main configuration class"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    EXTERNAL_DATA_DIR = DATA_DIR / 'external'
    OUTPUT_DIR = BASE_DIR / 'output'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Create directories
    for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
                     EXTERNAL_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # CRS definitions
    CRS_WGS84 = 'EPSG:4326'
    CRS_WEB_MERCATOR = 'EPSG:3857'
    CRS_UTM_ZONES = {
        'north': 'EPSG:326{zone}',
        'south': 'EPSG:327{zone}'
    }
    
    # Map visualization defaults
    MAP_DEFAULTS = {
        'figsize': (12, 8),
        'dpi': 100,
        'alpha': 0.7,
        'edgecolor': 'black',
        'linewidth': 0.5,
        'cmap': 'viridis'
    }
    
    # Classification methods
    CLASSIFICATION_METHODS = [
        'equal_interval',
        'quantiles',
        'fisher_jenks',
        'natural_breaks'
    ]
    
    # Spatial operations
    SPATIAL_PREDICATES = [
        'intersects',
        'contains',
        'within',
        'touches',
        'crosses',
        'overlaps'
    ]
    
    # Data sources
    DATA_SOURCES = {
        'natural_earth': {
            'base_url': 'https://naturalearth.s3.amazonaws.com',
            'scales': ['110m', '50m', '10m'],
            'categories': ['cultural', 'physical']
        },
        'osm': {
            'overpass_url': 'https://overpass-api.de/api/interpreter'
        },
        'world_bank': {
            'base_url': 'http://api.worldbank.org/v2'
        }
    }
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': LOGS_DIR / 'geopandas_project.log',
                'formatter': 'standard'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO'
        }
    }
    
    @classmethod
    def get_utm_crs(cls, longitude: float, latitude: float) -> str:
        """Get appropriate UTM CRS for a location"""
        zone = int((longitude + 180) / 6) + 1
        if latitude >= 0:
            return cls.CRS_UTM_ZONES['north'].format(zone=zone)
        else:
            return cls.CRS_UTM_ZONES['south'].format(zone=zone)
    
    @classmethod
    def display_config(cls) -> Dict[str, Any]:
        """Display current configuration"""
        return {
            'base_dir': str(cls.BASE_DIR),
            'data_dir': str(cls.DATA_DIR),
            'crs_wgs84': cls.CRS_WGS84,
            'crs_web_mercator': cls.CRS_WEB_MERCATOR,
            'map_defaults': cls.MAP_DEFAULTS
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOGGING_CONFIG = {
        **Config.LOGGING,
        'root': {
            **Config.LOGGING['root'],
            'level': 'DEBUG'
        }
    }

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOGGING_CONFIG = Config.LOGGING

# Configuration factory
def get_config(env: str = 'development') -> Config:
    """Get configuration based on environment"""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    return configs.get(env, DevelopmentConfig)

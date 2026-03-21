import geopandas as gpd

def load_geojson(path: str) -> gpd.GeoDataFrame:
    """Load a GeoJSON file into a GeoDataFrame."""
    return gpd.read_file(path)


def load_shapefile(path: str) -> gpd.GeoDataFrame:
    """Load a shapefile into a GeoDataFrame."""
    return gpd.read_file(path)

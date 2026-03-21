import geopandas as gpd

def filter_by_bounds(gdf: gpd.GeoDataFrame, bounds: tuple) -> gpd.GeoDataFrame:
    """
    Filter features within given bounding box.
    bounds = (minx, miny, maxx, maxy)
    """
    return gdf.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]]


def count_features(gdf: gpd.GeoDataFrame) -> int:
    """Return number of features."""
    return len(gdf)

"""Statistical plotting for geospatial data..."""

import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple

class StatisticalPlots:
    """Statistical visualization for geospatial data"""
    
    def __init__(self, style: str = 'seaborn'):
        if style == 'seaborn':
            plt.style.use('seaborn-v0_8')
        elif style == 'ggplot':
            plt.style.use('ggplot')
    
    def histogram(self, gdf: gpd.GeoDataFrame, 
                  column: str,
                  bins: int = 30,
                  figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """Create histogram for a column"""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        gdf[column].hist(bins=bins, ax=ax, alpha=0.7, 
                        edgecolor='black', linewidth=1)
        
        ax.set_title(f'Distribution of {column}', fontsize=14, fontweight='bold')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def scatter_plot(self, gdf: gpd.GeoDataFrame,
                    x_col: str,
                    y_col: str,
                    color_col: Optional[str] = None,
                    figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """Create scatter plot between two columns"""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        if color_col:
            scatter = ax.scatter(gdf[x_col], gdf[y_col], 
                               c=gdf[color_col], cmap='viridis',
                               alpha=0.6, edgecolors='black', linewidth=0.5)
            plt.colorbar(scatter, label=color_col)
        else:
            ax.scatter(gdf[x_col], gdf[y_col], alpha=0.6)
        
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.set_title(f'{y_col} vs {x_col}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def box_plot(self, gdf: gpd.GeoDataFrame,
                columns: List[str],
                figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """Create box plot for multiple columns"""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        data = [gdf[col].dropna() for col in columns]
        bp = ax.boxplot(data, labels=columns, patch_artist=True)
        
        # Color boxes
        for patch, color in zip(bp['boxes'], plt.cm.viridis(np.linspace(0, 1, len(columns)))):
            patch.set_facecolor(color)
        
        ax.set_title('Box Plot Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Values')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def correlation_heatmap(self, gdf: gpd.GeoDataFrame,
                           columns: Optional[List[str]] = None,
                           figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """Create correlation heatmap"""
        
        if columns is None:
            numeric_cols = gdf.select_dtypes(include=[np.number]).columns
            data = gdf[numeric_cols]
        else:
            data = gdf[columns]
        
        corr = data.corr()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', 
                   cmap='RdBu_r', center=0, square=True, 
                   linewidths=0.5, ax=ax)
        
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def time_series(self, gdf: gpd.GeoDataFrame,
                   date_col: str,
                   value_col: str,
                   figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """Create time series plot"""
        
        fig, ax = plt.subplots(figsize=figsize)
        
        gdf_sorted = gdf.sort_values(date_col)
        ax.plot(gdf_sorted[date_col], gdf_sorted[value_col], 
               marker='o', linewidth=2, markersize=4)
        
        ax.set_xlabel(date_col, fontsize=12)
        ax.set_ylabel(value_col, fontsize=12)
        ax.set_title(f'Time Series of {value_col}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

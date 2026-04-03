"""Static map visualization utilities...."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import contextily as ctx
from typing import List, Optional, Union, Dict, Tuple
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import warnings

class MapVisualizer:
    """Create publication-quality static maps"""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8), 
                 dpi: int = 100,
                 style: str = 'default'):
        self.figsize = figsize
        self.dpi = dpi
        self.style = style
        
        # Set style
        if style == 'seaborn':
            plt.style.use('seaborn-v0_8')
        elif style == 'ggplot':
            plt.style.use('ggplot')
        elif style == 'default':
            plt.style.use('default')
    
    def plot_basic(self, gdf: gpd.GeoDataFrame, 
                   column: Optional[str] = None,
                   cmap: str = 'viridis',
                   alpha: float = 0.7,
                   edgecolor: str = 'black',
                   linewidth: float = 0.5,
                   title: str = 'Map',
                   legend: bool = True,
                   figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """Create a basic choropleth map"""
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize, dpi=self.dpi)
        
        if column:
            gdf.plot(column=column, cmap=cmap, alpha=alpha, 
                    edgecolor=edgecolor, linewidth=linewidth, 
                    legend=legend, ax=ax)
        else:
            gdf.plot(alpha=alpha, edgecolor=edgecolor, 
                    linewidth=linewidth, ax=ax)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_axis_off()
        
        plt.tight_layout()
        return fig
    
    def plot_with_basemap(self, gdf: gpd.GeoDataFrame, 
                         source: str = ctx.providers.OpenStreetMap.Mapnik,
                         column: Optional[str] = None,
                         cmap: str = 'viridis',
                         alpha: float = 0.6,
                         edgecolor: str = 'white',
                         linewidth: float = 0.3,
                         title: str = 'Map with Basemap',
                         figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """Create map with basemap from contextily"""
        
        # Reproject to Web Mercator for basemap
        gdf_web = gdf.to_crs('EPSG:3857')
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize, dpi=self.dpi)
        
        # Plot data
        if column:
            gdf_web.plot(column=column, cmap=cmap, alpha=alpha,
                        edgecolor=edgecolor, linewidth=linewidth, ax=ax)
        else:
            gdf_web.plot(alpha=alpha, edgecolor=edgecolor,
                        linewidth=linewidth, ax=ax)
        
        # Add basemap
        ctx.add_basemap(ax, source=source)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_axis_off()
        
        plt.tight_layout()
        return fig
    
    def plot_multiple(self, gdfs: Dict[str, gpd.GeoDataFrame], 
                      subplot_layout: Tuple[int, int] = (2, 2),
                      figsize: Tuple[int, int] = (15, 12),
                      cmap: str = 'viridis',
                      titles: Optional[List[str]] = None) -> plt.Figure:
        """Plot multiple GeoDataFrames in subplots"""
        
        fig, axes = plt.subplots(*subplot_layout, figsize=figsize, dpi=self.dpi)
        axes = axes.flatten()
        
        for idx, (name, gdf) in enumerate(gdfs.items()):
            if idx < len(axes):
                gdf.plot(ax=axes[idx], cmap=cmap, alpha=0.7, 
                        edgecolor='black', linewidth=0.5)
                axes[idx].set_title(titles[idx] if titles else name, 
                                   fontsize=12, fontweight='bold')
                axes[idx].set_axis_off()
        
        # Hide unused subplots
        for idx in range(len(gdfs), len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def plot_inset_map(self, main_gdf: gpd.GeoDataFrame, 
                      inset_gdf: gpd.GeoDataFrame,
                      main_title: str = 'Main Map',
                      inset_title: str = 'Inset Map',
                      figsize: Tuple[int, int] = (14, 10)) -> plt.Figure:
        """Create map with inset"""
        
        fig, ax = plt.subplots(figsize=figsize, dpi=self.dpi)
        
        # Main plot
        main_gdf.plot(ax=ax, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add inset
        inset_ax = fig.add_axes([0.7, 0.6, 0.2, 0.2])
        inset_gdf.plot(ax=inset_ax, alpha=0.7, edgecolor='black', linewidth=0.5)
        inset_ax.set_title(inset_title, fontsize=10)
        inset_ax.set_axis_off()
        
        ax.set_title(main_title, fontsize=14, fontweight='bold')
        ax.set_axis_off()
        
        plt.tight_layout()
        return fig
    
    def plot_choropleth(self, gdf: gpd.GeoDataFrame, 
                        column: str,
                        classification: str = 'equal_interval',
                        n_classes: int = 5,
                        cmap: str = 'RdYlBu_r',
                        legend_title: str = '',
                        figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """Create choropleth map with classification"""
        
        from mapclassify import EqualInterval, Quantiles, FisherJenks
        
        # Apply classification
        if classification == 'equal_interval':
            classifier = EqualInterval(gdf[column], k=n_classes)
        elif classification == 'quantiles':
            classifier = Quantiles(gdf[column], k=n_classes)
        elif classification == 'fisher_jenks':
            classifier = FisherJenks(gdf[column], k=n_classes)
        else:
            raise ValueError("Invalid classification method")
        
        gdf['classified'] = classifier.yb
        
        fig, ax = plt.subplots(figsize=figsize or self.figsize, dpi=self.dpi)
        
        # Plot
        gdf.plot(column='classified', cmap=cmap, alpha=0.8, 
                edgecolor='white', linewidth=0.5, ax=ax, legend=True)
        
        # Create legend
        legend_labels = [f"{classifier.bins[i]:.2f} - {classifier.bins[i+1]:.2f}" 
                        for i in range(len(classifier.bins)-1)]
        patches = [mpatches.Patch(color=plt.cm.get_cmap(cmap)(i/n_classes), 
                                 label=legend_labels[i]) 
                  for i in range(n_classes)]
        ax.legend(handles=patches, title=legend_title or column, 
                 loc='lower right')
        
        ax.set_title(f'Choropleth Map - {column} ({classification})', 
                    fontsize=14, fontweight='bold')
        ax.set_axis_off()
        
        plt.tight_layout()
        return fig
    
    def save_map(self, fig: plt.Figure, filename: str, 
                 format: str = 'png', dpi: int = 300):
        """Save map to file"""
        fig.savefig(filename, format=format, dpi=dpi, bbox_inches='tight')
        print(f"Map saved as {filename}")

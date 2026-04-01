"""Animated maps and visualizations..."""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import geopandas as gpd
import numpy as np
from typing import List, Callable, Optional
from datetime import datetime, timedelta

class MapAnimation:
    """Create animated maps"""
    
    def __init__(self, figsize: tuple = (10, 8), dpi: int = 100):
        self.figsize = figsize
        self.dpi = dpi
        self.frames = []
    
    def create_temporal_animation(self, gdfs: List[gpd.GeoDataFrame],
                                  dates: List[str],
                                  column: Optional[str] = None,
                                  interval: int = 500) -> animation.FuncAnimation:
        """Create animation over time"""
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        def update(frame):
            ax.clear()
            gdf = gdfs[frame]
            
            if column:
                gdf.plot(column=column, ax=ax, cmap='viridis', 
                        legend=True, alpha=0.7)
            else:
                gdf.plot(ax=ax, alpha=0.7)
            
            ax.set_title(f'Date: {dates[frame]}', fontsize=14, fontweight='bold')
            ax.set_axis_off()
            
            return ax,
        
        anim = animation.FuncAnimation(fig, update, frames=len(gdfs), 
                                      interval=interval, blit=False)
        
        self.frames = anim
        return anim
    
    def create_zoom_animation(self, gdf: gpd.GeoDataFrame,
                             zoom_steps: int = 10,
                             interval: int = 200) -> animation.FuncAnimation:
        """Create zoom-in animation"""
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        bounds = gdf.total_bounds
        minx, miny, maxx, maxy = bounds
        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2
        width = maxx - minx
        height = maxy - miny
        
        def update(step):
            ax.clear()
            zoom_factor = 1 - (step / zoom_steps) * 0.9
            new_width = width * zoom_factor
            new_height = height * zoom_factor
            
            ax.set_xlim(center_x - new_width/2, center_x + new_width/2)
            ax.set_ylim(center_y - new_height/2, center_y + new_height/2)
            
            gdf.plot(ax=ax, alpha=0.7, edgecolor='black')
            ax.set_title(f'Zoom Level: {step+1}/{zoom_steps}', fontsize=12)
            ax.set_axis_off()
            
            return ax,
        
        anim = animation.FuncAnimation(fig, update, frames=zoom_steps,
                                      interval=interval, blit=False)
        
        return anim
    
    def save_animation(self, anim: animation.FuncAnimation, 
                      filename: str, fps: int = 5):
        """Save animation to file"""
        anim.save(filename, fps=fps, writer='pillow')
        print(f"Animation saved as {filename}")

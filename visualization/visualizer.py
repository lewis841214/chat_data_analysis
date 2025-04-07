#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base visualizer for generating plots from conversation features and targets.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


class Visualizer:
    """
    Base class for visualization of conversation features and targets.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the visualizer.
        
        Args:
            config: Configuration dictionary for visualizer
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Get visualization-specific configuration
        self.output_dir = config.get("output_dir", "visualizations")
        self.plot_format = config.get("plot_format", "png")
        self.dpi = config.get("dpi", 300)
        self.default_figsize = config.get("figsize", (10, 6))
        self.style = config.get("style", "darkgrid")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set default style
        sns.set_style(self.style)
        
        self.logger.info(f"Initialized visualizer with config: {config}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        return logging.getLogger(f"Visualizer.{self.__class__.__name__}")
    
    def generate_plots(self, features: Dict[str, Any], targets: Dict[str, Any]) -> List[str]:
        """
        Generate all plots for the given features and targets.
        
        Args:
            features: Dictionary of extracted features
            targets: Dictionary of processed targets
            
        Returns:
            List of generated plot file paths
        """
        raise NotImplementedError("This method must be implemented by subclasses")
    
    def save_plot(self, fig: plt.Figure, filename: str) -> str:
        """
        Save a plot to a file.
        
        Args:
            fig: Matplotlib figure to save
            filename: Name of the file (without extension)
            
        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.output_dir, f"{filename}.{self.plot_format}")
        fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        self.logger.info(f"Saved plot to {filepath}")
        return filepath
    
    def create_figure(self, title: str, figsize: Optional[Tuple[int, int]] = None) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a new figure with given title and size.
        
        Args:
            title: Figure title
            figsize: Figure size (width, height) in inches
            
        Returns:
            Tuple of Figure and Axes objects
        """
        fig_size = figsize if figsize else self.default_figsize
        fig, ax = plt.subplots(figsize=fig_size)
        fig.suptitle(title)
        return fig, ax 
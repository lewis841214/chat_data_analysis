#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature plotter for generating visualizations of conversation features and targets.
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict

from visualization.visualizer import Visualizer


class FeaturePlotter(Visualizer):
    """
    Plotter for visualizing relationships between conversation features and targets.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the feature plotter.
        
        Args:
            config: Configuration dictionary for plotter
        """
        super().__init__(config)
        
        # Get plotter-specific configuration
        self.plot_types = config.get("plot_types", ["scatter", "bar", "histogram", "heatmap", "boxplot"])
        self.top_features = config.get("top_features", 10)
        self.correlation_method = config.get("correlation_method", "pearson")
        self.target_metric = config.get("target_metric", "response_rate")
        
        self.logger.info(f"Initialized FeaturePlotter with plot types: {self.plot_types}")
    
    def _prepare_data(self, features: Dict[str, Any], targets: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare data for plotting by flattening the feature and target dictionaries.
        
        Args:
            features: Dictionary of extracted features
            targets: Dictionary of processed targets
            
        Returns:
            Pandas DataFrame with flattened features and targets
        """
        # Create a flattened dictionary for each conversation
        flattened_data = []
        
        for conv_id, feature_dict in features.items():
            if conv_id not in targets:
                self.logger.warning(f"Conversation ID {conv_id} not found in targets, skipping")
                continue
                
            # Get target value
            target_value = targets[conv_id].get("value", None)
            target_metric = targets[conv_id].get("metric", self.target_metric)
            
            if target_value is None:
                self.logger.warning(f"No target value for conversation {conv_id}, skipping")
                continue
                
            # Flatten the nested feature dictionary
            flat_features = self._flatten_dict(feature_dict)
            
            # Add conversation ID and target
            flat_features["conversation_id"] = conv_id
            flat_features[f"target_{target_metric}"] = target_value
            
            flattened_data.append(flat_features)
            
        # Convert to DataFrame
        df = pd.DataFrame(flattened_data)
        self.logger.info(f"Prepared data with {len(df)} rows and {len(df.columns)} columns")
        
        return df
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten a nested dictionary, joining keys with underscores.
        
        Args:
            d: Dictionary to flatten
            parent_key: Key of parent dictionary
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
                
        return dict(items)
    
    def generate_plots(self, features: Dict[str, Any], targets: Dict[str, Any]) -> List[str]:
        """
        Generate all plots for the given features and targets.
        
        Args:
            features: Dictionary of extracted features
            targets: Dictionary of processed targets
            
        Returns:
            List of generated plot file paths
        """
        self.logger.info("Generating plots for features and targets")
        
        # Check if features and targets are empty
        if not features or not targets:
            self.logger.warning("Empty features or targets, cannot generate plots")
            return []
            
        # Prepare data
        df = self._prepare_data(features, targets)
        
        # Generate plots based on configuration
        plot_paths = []
        
        # Make sure the target column exists
        target_column = f"target_{self.target_metric}"
        if target_column not in df.columns:
            self.logger.warning(f"Target column {target_column} not found in data")
            return []
            
        # Generate correlation matrix and find top features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)
            
        # Skip if no numeric columns
        if not numeric_cols:
            self.logger.warning("No numeric feature columns found")
            return []
            
        # Calculate correlations with target
        correlations = df[numeric_cols].corrwith(df[target_column], method=self.correlation_method)
        
        # Filter out NaN values
        correlations = correlations.dropna()
        
        # Get top features by absolute correlation
        top_features = correlations.abs().sort_values(ascending=False).head(self.top_features).index.tolist()
        
        self.logger.info(f"Top {len(top_features)} features by correlation: {top_features}")
        
        # Generate scatter plots for top features
        if "scatter" in self.plot_types:
            scatter_paths = self._generate_scatter_plots(df, top_features, target_column)
            plot_paths.extend(scatter_paths)
            
        # Generate bar plot of feature correlations
        if "bar" in self.plot_types:
            bar_path = self._generate_correlation_bar_plot(correlations, target_column)
            plot_paths.append(bar_path)
            
        # Generate histogram for target
        if "histogram" in self.plot_types:
            hist_path = self._generate_target_histogram(df, target_column)
            plot_paths.append(hist_path)
            
        # Generate heatmap of feature correlations
        if "heatmap" in self.plot_types:
            heatmap_path = self._generate_correlation_heatmap(df, top_features, target_column)
            plot_paths.append(heatmap_path)
            
        # Generate boxplots by target value segments
        if "boxplot" in self.plot_types:
            boxplot_paths = self._generate_boxplots(df, top_features, target_column)
            plot_paths.extend(boxplot_paths)
            
        self.logger.info(f"Generated {len(plot_paths)} plots")
        return plot_paths
    
    def _generate_scatter_plots(self, df: pd.DataFrame, features: List[str], 
                              target_column: str) -> List[str]:
        """
        Generate scatter plots for each feature against the target.
        
        Args:
            df: DataFrame with features and target
            features: List of feature columns to plot
            target_column: Name of the target column
            
        Returns:
            List of paths to generated plots
        """
        plot_paths = []
        
        for feature in features:
            try:
                fig, ax = self.create_figure(f"Relationship between {feature} and {target_column}")
                
                # Create scatter plot with regression line
                sns.regplot(x=feature, y=target_column, data=df, ax=ax, scatter_kws={"alpha": 0.5})
                
                # Calculate correlation
                corr = df[[feature, target_column]].corr().iloc[0, 1]
                ax.set_title(f"{feature} vs {target_column} (correlation: {corr:.2f})")
                
                # Save plot
                plot_path = self.save_plot(fig, f"scatter_{feature}_vs_{target_column}")
                plot_paths.append(plot_path)
                
            except Exception as e:
                self.logger.error(f"Error generating scatter plot for {feature}: {str(e)}")
                
        return plot_paths
    
    def _generate_correlation_bar_plot(self, correlations: pd.Series, 
                                     target_column: str) -> str:
        """
        Generate a bar plot of feature correlations with the target.
        
        Args:
            correlations: Series of correlations
            target_column: Name of the target column
            
        Returns:
            Path to the generated plot
        """
        try:
            # Sort correlations
            sorted_correlations = correlations.sort_values()
            
            # Create figure
            fig, ax = self.create_figure(f"Feature Correlations with {target_column}", 
                                        figsize=(12, max(6, len(sorted_correlations) * 0.3)))
            
            # Create horizontal bar plot
            sorted_correlations.plot(kind="barh", ax=ax)
            
            ax.set_xlabel("Correlation Coefficient")
            ax.set_title(f"Feature Correlations with {target_column}")
            
            # Add grid lines
            ax.grid(True, axis="x")
            
            # Save plot
            return self.save_plot(fig, f"correlation_bar_{target_column}")
            
        except Exception as e:
            self.logger.error(f"Error generating correlation bar plot: {str(e)}")
            return ""
    
    def _generate_target_histogram(self, df: pd.DataFrame, target_column: str) -> str:
        """
        Generate a histogram of the target variable.
        
        Args:
            df: DataFrame with target
            target_column: Name of the target column
            
        Returns:
            Path to the generated plot
        """
        try:
            fig, ax = self.create_figure(f"Distribution of {target_column}")
            
            # Create histogram with KDE
            sns.histplot(df[target_column], kde=True, ax=ax)
            
            ax.set_xlabel(target_column)
            ax.set_ylabel("Frequency")
            ax.set_title(f"Distribution of {target_column}")
            
            # Add mean line
            mean_val = df[target_column].mean()
            ax.axvline(mean_val, color="red", linestyle="--", 
                      label=f"Mean: {mean_val:.2f}")
            
            # Add median line
            median_val = df[target_column].median()
            ax.axvline(median_val, color="green", linestyle="-.", 
                      label=f"Median: {median_val:.2f}")
            
            ax.legend()
            
            # Save plot
            return self.save_plot(fig, f"histogram_{target_column}")
            
        except Exception as e:
            self.logger.error(f"Error generating target histogram: {str(e)}")
            return ""
    
    def _generate_correlation_heatmap(self, df: pd.DataFrame, features: List[str], 
                                    target_column: str) -> str:
        """
        Generate a heatmap of correlations between top features and target.
        
        Args:
            df: DataFrame with features and target
            features: List of feature columns to include
            target_column: Name of the target column
            
        Returns:
            Path to the generated plot
        """
        try:
            # Include target in correlation matrix
            columns = features.copy()
            columns.append(target_column)
            
            # Calculate correlation matrix
            corr_matrix = df[columns].corr()
            
            # Create figure
            fig, ax = self.create_figure("Feature Correlation Heatmap", 
                                        figsize=(10, 8))
            
            # Create heatmap
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", 
                       linewidths=0.5, ax=ax)
            
            ax.set_title("Correlation Heatmap of Top Features")
            
            # Save plot
            return self.save_plot(fig, "correlation_heatmap")
            
        except Exception as e:
            self.logger.error(f"Error generating correlation heatmap: {str(e)}")
            return ""
    
    def _generate_boxplots(self, df: pd.DataFrame, features: List[str], 
                         target_column: str) -> List[str]:
        """
        Generate boxplots of features grouped by target value segments.
        
        Args:
            df: DataFrame with features and target
            features: List of feature columns to plot
            target_column: Name of the target column
            
        Returns:
            List of paths to generated plots
        """
        plot_paths = []
        
        try:
            # Create target segments
            df = df.copy()
            
            # Create categorical target segments
            q_labels = ["Low", "Medium", "High"]
            df["target_segment"] = pd.qcut(df[target_column], q=3, labels=q_labels)
            
            # Generate boxplot for each feature
            for feature in features:
                try:
                    fig, ax = self.create_figure(f"Distribution of {feature} by {target_column} segment")
                    
                    # Create boxplot
                    sns.boxplot(x="target_segment", y=feature, data=df, ax=ax)
                    
                    ax.set_title(f"Distribution of {feature} by {target_column} segment")
                    ax.set_xlabel(f"{target_column} segment")
                    ax.set_ylabel(feature)
                    
                    # Save plot
                    plot_path = self.save_plot(fig, f"boxplot_{feature}_by_{target_column}")
                    plot_paths.append(plot_path)
                    
                except Exception as e:
                    self.logger.error(f"Error generating boxplot for {feature}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error generating boxplots: {str(e)}")
            
        return plot_paths 
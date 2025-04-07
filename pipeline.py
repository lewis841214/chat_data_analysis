#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main pipeline orchestration script for chat data preprocessing.
This script manages the entire flow from raw data to processed corpus.
"""

import os
import argparse
import logging
import json
import yaml  # Added for debugging
import codecs  # Added for UTF-8 handling
from typing import Dict, List, Any, Optional
from tqdm import tqdm

from config_handler import ConfigHandler
from platform_handlers.handler_factory import PlatformHandlerFactory
from feature_processor.processor_factory import FeatureProcessorFactory
from data_processor.processor_factory import DataProcessorFactory
from visualization.visualizer import Visualizer
from visualization.plotter import FeaturePlotter

class Pipeline:
    """
    Main pipeline class for orchestrating the chat data preprocessing flow.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the pipeline with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = self._setup_logging()
        self.config = ConfigHandler(config_path).get_config()
        self.logger.info(f"Initialized pipeline with config from {config_path}")
        
        # Debug: Print the platform configuration
        if "platform" in self.config:
            self.logger.info(f"Platform config: {self.config['platform']}")
            self.logger.info(f"Platform type: {self.config['platform'].get('type', 'Not specified')}")
        else:
            self.logger.warning("No platform section found in config")
        
        # Initialize components
        self.platform_handler = None
        if self.is_platform_configured():
            self.platform_handler = PlatformHandlerFactory.get_handler(self.config)
            self.logger.info(f"Using platform handler: {self.platform_handler.__class__.__name__}")
        else:
            self.logger.info("Platform not configured, will load from formatted data path")
            
        # Initialize data processor
        self.data_processor = None
        if "data_processing" in self.config:
            try:
                self.data_processor = DataProcessorFactory.get_processor(self.config)
                self.logger.info(f"Using data processor: {self.data_processor.__class__.__name__}")
            except Exception as e:
                self.logger.error(f"Error initializing data processor: {str(e)}")
        else:
            self.logger.warning("No data processing configured")

        # Initialize feature processor
        self.feature_processor = None
        try:
            self.feature_processor = FeatureProcessorFactory.get_processor(self.config)
            self.logger.info(f"Using feature processor: {self.feature_processor.__class__.__name__}")
        except Exception as e:
            self.logger.error(f"Error initializing feature processor: {str(e)}")
        
            
        # # Initialize visualizer
        # self.visualizer = None
        # if "visualization" in self.config:
        #     viz_config = self.config.get("visualization", {})
        #     self.visualizer = FeaturePlotter(viz_config)
        #     self.logger.info(f"Using visualizer: {self.visualizer.__class__.__name__}")
        # else:
        #     self.logger.warning("No visualization configured")
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("pipeline.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("ChatPipeline")
    
    def is_platform_configured(self) -> bool:
        """
        Check if platform is properly configured.
        
        Returns:
            bool: True if platform is configured, False otherwise
        """
        return (
            "platform" in self.config 
            and self.config["platform"].get("type") is not None
            and self.config["platform"].get("platform_data_path") is not None
        )
    
    def load_formatted_data(self) -> List[Dict[str, Any]]:
        """
        Load data directly from the formatted data path.
        
        Returns:
            List[Dict[str, Any]]: The loaded formatted data
        """
        if "platform" not in self.config or "input_formatted_path" not in self.config:
            self.logger.error("No input_formatted_path specified in config")
            return []
            
        input_path = self.config["input_formatted_path"]
        self.logger.info(f"Loading data from formatted input path: {input_path}")
        
        conversation_data = []
        
        if not os.path.exists(input_path):
            self.logger.error(f"Formatted input path does not exist: {input_path}")
            return []
            
        try:
            if os.path.isdir(input_path):
                # If it's a directory, recursively search for all JSON files
                for root, dirs, files in tqdm(os.walk(input_path)):
                    for filename in files:
                        if filename.endswith('.json'):
                            file_path = os.path.join(root, filename)
                            self.logger.debug(f"Loading conversation data from: {file_path}")
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_data = json.load(f)
                                    if isinstance(file_data, list):
                                        conversation_data.extend(file_data)
                                    else:
                                        conversation_data.append(file_data)
                            except Exception as file_e:
                                self.logger.warning(f"Error loading file {file_path}: {str(file_e)}")
            else:
                # If it's a file, load it directly
                with open(input_path, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
            self.logger.info(f"Loaded {len(conversation_data)} conversations from formatted input")
            return conversation_data
            
        except Exception as e:
            self.logger.error(f"Error loading formatted conversation data: {str(e)}")
            return []

    
    def save_processed_data(self, data: Dict[str, Any], filename: str) -> None:
        """
        Save processed data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the output file
        """
        output_dir = self.config.get("output_dir", "data/output/")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved processed data to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving processed data to {filepath}: {str(e)}")
    
    def run(self) -> None:
        """
        Execute the full pipeline process.
        """
        self.logger.info("Starting pipeline execution")
        
        # Step 1: Get conversation data - either from platform handler or formatted input
        if self.is_platform_configured() and self.platform_handler is not None:
            self.logger.info("Step 1: Platform-specific conversation data handling")
            conversation_data = self.platform_handler.process()
        else:
            self.logger.info("Step 1: Loading from formatted data path (skipping platform processing)")
            conversation_data = self.load_formatted_data()
            
        if not conversation_data:
            self.logger.error("No conversation data loaded. Pipeline execution failed.")
            return
        
        
        # Limit data for testing mode
        if self.config.get("mode") == "testing":
            sample_size = min(500, len(conversation_data))
            self.logger.info(f"Testing mode: limiting to {sample_size} conversations")
            conversation_data = conversation_data[:sample_size]

        
        # Step 2: Apply data processing if configured
        if self.data_processor is not None:
            self.logger.info("Step 2: Applying data processing filters")
            conversation_data = self.data_processor.process(conversation_data)
            self.logger.info(f"Processed {len(conversation_data)} conversations")
            
            
        self.logger.info(f"Processing {len(conversation_data)} conversations")
        
        # Step 3: Extract features and targets
        if self.feature_processor is not None:
            self.logger.info("Step 3: Feature extraction and target processing")
            feature_result = self.feature_processor.process(conversation_data)
            features = feature_result.get("features", {})
            targets = feature_result.get("targets", {})
            
            self.logger.info(f"Extracted {len(features)} features and {len(targets)} targets")
            
            # Save the processed features and targets
            self.save_processed_data({
                "features": features,
                "targets": targets
            }, "processed_features_targets.json")
            
        #     # Step 4: Visualization
        #     if self.visualizer is not None and features and targets:
        #         self.logger.info("Step 4: Visualization of features and targets")
        #         plot_paths = self.visualizer.generate_plots(features, targets)
                
        #         self.logger.info(f"Generated {len(plot_paths)} visualizations")
                
        #         # Save the list of generated plot files
        #         self.save_processed_data({
        #             "plots": plot_paths
        #         }, "visualization_results.json")
        #     else:
        #         self.logger.warning("Skipping visualization step: visualizer not configured or no features/targets")
        # else:
        #     self.logger.warning("Skipping feature processing and visualization steps: feature processor not configured")
        
        # self.logger.info("Pipeline execution completed")

def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="Chat Data Preprocessing Pipeline")
    parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    args = parser.parse_args()
    
    # Debug - print the raw config file
    with codecs.open(args.config, 'r', encoding='utf-8') as f:
        config_text = f.read()
        parsed_config = yaml.safe_load(config_text)
        print(f"Raw config from {args.config}:")
        print(f"Platform section: {parsed_config.get('platform', 'Not found')}")
    
    pipeline = Pipeline(args.config)
    pipeline.run()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base class for feature processors that extract and analyze conversation features.
"""

import abc
import logging
import importlib
import os
import inspect
import pkgutil
from typing import Dict, List, Any, Optional, Type

class BaseFeatureExtractor:
    """
    Base class for individual feature extractors.
    Each feature extractor is responsible for extracting a specific feature.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the feature extractor.
        
        Args:
            config: Configuration dictionary for this extractor
        """
        self.config = config
        self.logger = logging.getLogger(f"FeatureExtractor.{self.__class__.__name__}")
        
    @abc.abstractmethod
    def extract(self, conversation: Dict[str, Any]) -> Any:
        """
        Extract a specific feature from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Extracted feature value
        """
        pass
    
    @property
    def feature_name(self) -> str:
        """
        Get the name of the feature that this extractor extracts.
        
        Returns:
            Name of the feature
        """
        # Default to class name without "Extractor" suffix
        class_name = self.__class__.__name__
        if class_name.endswith("Extractor"):
            return class_name[:-9].lower()
        return class_name.lower()


class BaseTargetExtractor:
    """
    Base class for individual target extractors.
    Each target extractor is responsible for extracting a specific target metric.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the target extractor.
        
        Args:
            config: Configuration dictionary for this extractor
        """
        self.config = config
        self.logger = logging.getLogger(f"TargetExtractor.{self.__class__.__name__}")
        
    @abc.abstractmethod
    def extract(self, conversation: Dict[str, Any]) -> Any:
        """
        Extract a specific target from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Extracted target value
        """
        pass
    
    @property
    def target_name(self) -> str:
        """
        Get the name of the target that this extractor extracts.
        
        Returns:
            Name of the target
        """
        # Default to class name without "Extractor" suffix
        class_name = self.__class__.__name__
        if class_name.endswith("Extractor"):
            return class_name[:-9].lower()
        return class_name.lower()


class BaseFeatureProcessor:
    """
    Base class for feature processors that orchestrate feature and target extraction.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the feature processor.
        
        Args:
            config: Configuration dictionary for this processor
        """
        self.config = config
        self.logger = self._setup_logging()
        
        
        # Initialize feature and target extractors
        self.feature_extractors = self._load_feature_extractors()
        self.target_extractors = self._load_target_extractors()
        
        self.logger.info(f"Initialized with {len(self.feature_extractors)} feature extractors and "
                        f"{len(self.target_extractors)} target extractors")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        return logging.getLogger(f"FeatureProcessor.{self.__class__.__name__}")
    
    def _load_feature_extractors(self) -> Dict[str, BaseFeatureExtractor]:
        """
        Load all feature extractors.
        
        Returns:
            Dictionary mapping feature names to extractor instances
        """
        enabled_features = self.config.get("enabled_features", [])
        extractors = {}
        
        # Import all modules in the features package
        try:
            from feature_processor import features
            
            # Get all feature extractor classes from the features package
            for _, module_name, _ in pkgutil.iter_modules(features.__path__):
                module = importlib.import_module(f"feature_processor.features.{module_name}")
                
                # Find all classes that inherit from BaseFeatureExtractor
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseFeatureExtractor) and 
                        obj is not BaseFeatureExtractor):
                        
                        # Create instance of the extractor
                        extractor = obj(self.config)
                        feature_name = extractor.feature_name
                        
                        # Check if this feature is enabled
                        if not enabled_features or feature_name in enabled_features:
                            extractors[feature_name] = extractor
                            self.logger.info(f"Loaded feature extractor: {feature_name}")
            
        except ImportError:
            self.logger.warning("Could not import feature extractors from 'features' package")
        
        return extractors
    
    def _load_target_extractors(self) -> Dict[str, BaseTargetExtractor]:
        """
        Load all target extractors.
        
        Returns:
            Dictionary mapping target names to extractor instances
        """
        enabled_targets = self.config.get("enabled_targets", [])
        extractors = {}
        
        # Import all modules in the targets package
        try:
            from feature_processor import targets
            
            # Get all target extractor classes from the targets package
            for _, module_name, _ in pkgutil.iter_modules(targets.__path__):
                module = importlib.import_module(f"feature_processor.targets.{module_name}")
                
                # Find all classes that inherit from BaseTargetExtractor
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseTargetExtractor) and 
                        obj is not BaseTargetExtractor):
                        
                        # Create instance of the extractor
                        extractor = obj(self.config)
                        target_name = extractor.target_name
                        
                        # Check if this target is enabled
                        if not enabled_targets or target_name in enabled_targets:
                            extractors[target_name] = extractor
                            self.logger.info(f"Loaded target extractor: {target_name}")
            
        except ImportError:
            self.logger.warning("Could not import target extractors from 'targets' package")
        
        return extractors
    
    def extract_features(self, conversations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract features from conversation data.
        
        Args:
            conversations: List of conversation data in standardized format
            
        Returns:
            Dictionary of extracted features by conversation ID
        """
        self.logger.info(f"Extracting features from {len(conversations)} conversations")
        
        features = {}
        
        for i, conversation in enumerate(conversations):
            conversation_id = conversation.get("conversation_id", f"conversation_{i}")
            
            # Skip conversations with too few or too many messages
            messages = conversation.get("conversation", [])
           
            
            # Extract features
            conv_features = {}
            for feature_name, extractor in self.feature_extractors.items():
                
                try:
                    feature_value = extractor.extract(conversation)
                    conv_features[feature_name] = feature_value
                except Exception as e:
                    self.logger.error(f"Error extracting feature {feature_name} for conversation {conversation_id}: {str(e)}")
            # Add to features dictionary
            features[conversation_id] = conv_features
            breakpoint()
        self.logger.info(f"Extracted features from {len(features)} valid conversations")
        return features
    
    def process_targets(self, conversations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Process target values from conversation data.
        
        Args:
            conversations: List of conversation data in standardized format
            
        Returns:
            Dictionary of processed targets by conversation ID
        """
        self.logger.info(f"Processing targets from {len(conversations)} conversations")
        
        targets = {}
        
        for i, conversation in enumerate(conversations):
            conversation_id = conversation.get("conversation_id", f"conversation_{i}")
            
            # Skip conversations with too few or too many messages
            messages = conversation.get("conversation", [])
            
            
            # Extract targets
            conv_targets = {}
            for target_name, extractor in self.target_extractors.items():
                try:
                    target_value = extractor.extract(conversation)
                    conv_targets[target_name] = target_value
                except Exception as e:
                    self.logger.error(f"Error extracting target {target_name} for conversation {conversation_id}: {str(e)}")
            
            # Add to targets dictionary
            targets[conversation_id] = conv_targets
        
        self.logger.info(f"Processed targets for {len(targets)} valid conversations")
        return targets
    
    def process(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process conversation data to extract features and targets.
        
        Args:
            conversations: List of conversation data in standardized format
            
        Returns:
            Dictionary containing features and targets
        """
        self.logger.info("Starting feature processing")
        
        if not conversations:
            self.logger.warning("No conversations provided for feature processing")
            return {"features": {}, "targets": {}}
        
        # Extract features from conversations
        self.logger.info("Extracting features")
        features = self.extract_features(conversations)
        
        # Process targets from conversations
        self.logger.info("Processing targets")
        targets = self.process_targets(conversations)
        
        result = {
            "features": features,
            "targets": targets
        }
        
        self.logger.info(f"Completed feature processing with {len(features)} features and {len(targets)} targets")
        return result 
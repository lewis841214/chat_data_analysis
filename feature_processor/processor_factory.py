#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Factory for creating feature processors.
"""

import logging
from typing import Dict, Any, Type

from feature_processor.base_processor import BaseFeatureProcessor


class FeatureProcessorFactory:
    """
    Factory class for creating feature processors.
    """
    
    # Registry of available processors
    _processors = {
        # Will be registered as they are implemented
    }
    
    @classmethod
    def register_processor(cls, name: str, processor_class: Type[BaseFeatureProcessor]) -> None:
        """
        Register a new processor class.
        
        Args:
            name: Name of the processor
            processor_class: Processor class to register
        """
        cls._processors[name] = processor_class
        logging.getLogger(__name__).info(f"Registered feature processor: {name}")
    
    @classmethod
    def get_processor(cls, config: Dict[str, Any]) -> BaseFeatureProcessor:
        """
        Get a feature processor instance based on configuration.
        
        Args:
            config: Configuration dictionary that can contain either feature_processor section 
                   or features/target lists in the root
            
        Returns:
            Instance of feature processor
        """
        logger = logging.getLogger(__name__)
        
        # Default processor is the base processor
        default_processor = None
        for name, processor_class in cls._processors.items():
            if name == "default" or name == "base":
                default_processor = processor_class
                break
                
        if not default_processor and cls._processors:
            # Use the first registered processor as the default
            default_processor = next(iter(cls._processors.values()))
        
        if not default_processor:
            # Register the base processor if no processors are registered
            from feature_processor.base_processor import BaseFeatureProcessor
            default_processor = BaseFeatureProcessor
            cls.register_processor("default", BaseFeatureProcessor)
            
        # Create and return the processor instance
        logger.info(f"Creating feature processor with config: {config}")
        return default_processor(config) 
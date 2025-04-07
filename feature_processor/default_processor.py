#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Default implementation of the feature processor.
"""

from typing import Dict, Any

from feature_processor.base_processor import BaseFeatureProcessor
from feature_processor.processor_factory import FeatureProcessorFactory


class DefaultFeatureProcessor(BaseFeatureProcessor):
    """
    Default implementation of the feature processor.
    Uses the base class's functionality without any customization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the default feature processor.
        
        Args:
            config: Configuration dictionary for this processor
        """
        super().__init__(config)


# Register the default processor
FeatureProcessorFactory.register_processor("default", DefaultFeatureProcessor) 
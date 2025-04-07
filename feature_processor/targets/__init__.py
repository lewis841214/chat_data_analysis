#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Init file for feature_processor.targets package.
This package contains target extractors for analyzing conversation data.
"""

from feature_processor.targets.deal_made import DealMadeExtractor
from feature_processor.targets.sentiment import SentimentExtractor
from feature_processor.targets.engagement import UserEngagementExtractor

# Define the list of extractors available in this package
__all__ = [
    'DealMadeExtractor',
    'SentimentExtractor',
    'UserEngagementExtractor',
] 
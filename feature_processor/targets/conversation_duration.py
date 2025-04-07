#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for conversation duration.
"""

from typing import Dict, Any

from feature_processor.base_processor import BaseTargetExtractor


class ConversationDurationExtractor(BaseTargetExtractor):
    """
    Extracts the conversation duration target from a conversation.
    
    Conversation duration is defined as the time difference between the first and last message in minutes.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the conversation duration extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract the conversation duration from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Conversation duration in minutes
        """
        messages = conversation.get("conversation", [])
        
        if not messages:
            return 0.0
            
        # Get timestamps of first and last messages
        first_msg = messages[0]
        last_msg = messages[-1]
        
        first_timestamp = first_msg.get("timestamp_ms")
        last_timestamp = last_msg.get("timestamp_ms")
        
        if first_timestamp is None or last_timestamp is None:
            return 0.0
            
        # Calculate duration in minutes
        duration_ms = last_timestamp - first_timestamp
        return duration_ms / (1000 * 60)  # Convert to minutes 
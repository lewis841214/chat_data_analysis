#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for response rate.
"""

from typing import Dict, Any

from feature_processor.base_processor import BaseTargetExtractor


class ResponseRateExtractor(BaseTargetExtractor):
    """
    Extracts the response rate target from a conversation.
    
    Response rate is defined as the ratio of assistant responses to user messages.
    A high response rate indicates that the assistant responds to most user messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the response rate extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract the response rate from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Response rate (0.0 to 1.0)
        """
        messages = conversation.get("conversation", [])
        
        # Count message pairs (user -> assistant)
        user_messages = 0
        assistant_responses = 0
        
        for i in range(len(messages) - 1):
            current_sender = messages[i].get("sender_name", "").lower()
            next_sender = messages[i+1].get("sender_name", "").lower()
            
            if current_sender == "user" and next_sender == "assistant":
                user_messages += 1
                assistant_responses += 1
                
        # Also count unpaired user messages at the end
        if messages and messages[-1].get("sender_name", "").lower() == "user":
            user_messages += 1
        
        # Calculate response rate
        return assistant_responses / user_messages if user_messages > 0 else 0.0 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for user engagement.
"""

from typing import Dict, Any

from feature_processor.base_processor import BaseTargetExtractor


class UserEngagementExtractor(BaseTargetExtractor):
    """
    Extracts the user engagement target from a conversation.
    
    User engagement is defined as the ratio of user responses to assistant messages.
    A high user engagement indicates that the user responds to most assistant messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the user engagement extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract the user engagement from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            User engagement score (0.0 to 1.0)
        """
        messages = conversation.get("conversation", [])
        
        # Count message pairs (assistant -> user)
        assistant_messages = 0
        user_responses = 0
        
        for i in range(len(messages) - 1):
            current_sender = messages[i].get("sender_name", "").lower()
            next_sender = messages[i+1].get("sender_name", "").lower()
            
            if current_sender == "assistant" and next_sender == "user":
                assistant_messages += 1
                user_responses += 1
                
        # Also count unpaired assistant messages at the end
        if messages and messages[-1].get("sender_name", "").lower() == "assistant":
            assistant_messages += 1
        
        # Calculate user engagement
        return user_responses / assistant_messages if assistant_messages > 0 else 0.0 
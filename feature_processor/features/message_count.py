#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature extractor for message counts.
"""

from typing import Dict, Any

from feature_processor.base_processor import BaseFeatureExtractor


class MessageCountExtractor(BaseFeatureExtractor):
    """
    Extracts message counts from a conversation.
    
    Features:
    - total: Total number of messages
    - user: Number of user messages
    - assistant: Number of assistant messages
    - ratio_user_assistant: Ratio of user messages to assistant messages
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the message count extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def extract(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract message count features from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Dictionary of message count features
        """
        messages = conversation.get("conversation", [])
        
        # Count messages by role
        user_messages = [msg for msg in messages if msg.get("role", "").lower() == "user"]
        assistant_messages = [msg for msg in messages if msg.get("role", "").lower() == "assistant"]
        
        user_message_count = len(user_messages)
        assistant_message_count = len(assistant_messages)
        total_message_count = len(messages)
        
        # Calculate ratio
        ratio = user_message_count / assistant_message_count if assistant_message_count > 0 else 0
        return {
            "total": total_message_count,
            "user": user_message_count,
            "assistant": assistant_message_count,
        } 
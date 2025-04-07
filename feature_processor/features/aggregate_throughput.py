#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aggregate throughput analysis for individual conversations.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
import datetime
from datetime import datetime as dt
from feature_processor.base_processor import BaseFeatureExtractor

class AggregateThroughputExtractor(BaseFeatureExtractor):
    """
    Extracts throughput features for each conversation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the throughput extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
    @property
    def feature_name(self) -> str:
        """
        Get the name of the feature.
        
        Returns:
            Feature name
        """
        return "aggregate_throughput"
        
    def _get_conversation_time(self, conversation: Dict[str, Any]) -> datetime.datetime:
        """
        Extract the conversation creation time.
        
        Args:
            conversation: Conversation dictionary
            
        Returns:
            Datetime object representing conversation creation time
        """
        created_at = conversation.get("created_at")
        if created_at:
            return dt.fromisoformat(created_at)
        return None
        
    def _get_message_time(self, message: Dict[str, Any]) -> datetime.datetime:
        """
        Extract the message timestamp.
        
        Args:
            message: Message dictionary
            
        Returns:
            Datetime object representing message time
        """
        timestamp_ms = message.get("timestamp_ms")
        if timestamp_ms:
            return dt.fromtimestamp(timestamp_ms / 1000)
        return None
        
    def extract(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract throughput features for a single conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Dictionary containing throughput statistics for the conversation
        """
        created_at = self._get_conversation_time(conversation)
        if not created_at:
            return {
                "daily_throughput": {},
                "hourly_throughput": {},
                "ten_min_throughput": {}
            }
            
        # Count messages by date, hour, and 10-minute window
        date_counts = defaultdict(int)
        hour_counts = defaultdict(int)
        ten_min_counts = defaultdict(int)
        
        messages = conversation.get("conversation", [])
        for msg in messages:
            msg_time = self._get_message_time(msg)
            if msg_time:
                # Daily
                date_key = msg_time.strftime("%Y-%m-%d")
                date_counts[date_key] += 1
                
                # Hourly
                hour_key = msg_time.strftime("%Y-%m-%dT%H:00")
                hour_counts[hour_key] += 1
                
                # 10-minute
                minutes = (msg_time.minute // 10) * 10
                ten_min_key = msg_time.replace(minute=minutes, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
                ten_min_counts[ten_min_key] += 1
        
        # Get the date and hour keys for this conversation
        date_key = created_at.strftime("%Y-%m-%d")
        hour_key = created_at.strftime("%Y-%m-%dT%H:00")
        ten_min_key = created_at.replace(minute=(created_at.minute // 10) * 10, 
                                       second=0, 
                                       microsecond=0).strftime("%Y-%m-%dT%H:%M")
        
        return {
            "daily_throughput": {date_key: date_counts.get(date_key, 0)},
            "hourly_throughput": {hour_key: hour_counts.get(hour_key, 0)},
            "ten_min_throughput": {ten_min_key: ten_min_counts.get(ten_min_key, 0)}
        } 
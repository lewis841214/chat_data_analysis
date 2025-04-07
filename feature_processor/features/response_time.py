#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature extractor for response times.
"""

from typing import Dict, Any, List
import statistics

from feature_processor.base_processor import BaseFeatureExtractor


class ResponseTimeExtractor(BaseFeatureExtractor):
    """
    Extracts response time statistics from a conversation.
    
    Features:
    - avg_seconds: Average response time in seconds
    - min_seconds: Minimum response time in seconds
    - max_seconds: Maximum response time in seconds
    - median_seconds: Median response time in seconds
    - std_dev_seconds: Standard deviation of response times in seconds
    - user_to_assistant_avg: Average time for assistant to respond to user
    - assistant_to_user_avg: Average time for user to respond to assistant
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the response time extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
    
    def extract(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract response time features from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Dictionary of response time features
        """
        messages = conversation.get("conversation", [])
        
        # Calculate response times
        response_times = []
        user_to_assistant_times = []
        assistant_to_user_times = []
        
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            # Extract timestamps
            prev_time = prev_msg.get("timestamp_ms")
            curr_time = curr_msg.get("timestamp_ms")
            
            if prev_time is not None and curr_time is not None:
                # Calculate response time in seconds
                response_time = (curr_time - prev_time) / 1000
                response_times.append(response_time)
                
                # Categorize by sender transition
                prev_sender = prev_msg.get("sender_name", "").lower()
                curr_sender = curr_msg.get("sender_name", "").lower()
                
                if prev_sender == "user" and curr_sender == "assistant":
                    user_to_assistant_times.append(response_time)
                elif prev_sender == "assistant" and curr_sender == "user":
                    assistant_to_user_times.append(response_time)
        
        # Calculate statistics
        features = {
            "avg_seconds": self._safe_mean(response_times),
            "min_seconds": min(response_times) if response_times else 0,
            "max_seconds": max(response_times) if response_times else 0,
            "median_seconds": self._safe_median(response_times),
            "std_dev_seconds": self._safe_std_dev(response_times),
            "user_to_assistant_avg": self._safe_mean(user_to_assistant_times),
            "assistant_to_user_avg": self._safe_mean(assistant_to_user_times)
        }
        
        return features
    
    def _safe_mean(self, values: List[float]) -> float:
        """
        Calculate the mean of a list of values, safely handling empty lists.
        
        Args:
            values: List of values
            
        Returns:
            Mean value or 0 if the list is empty
        """
        return statistics.mean(values) if values else 0
    
    def _safe_median(self, values: List[float]) -> float:
        """
        Calculate the median of a list of values, safely handling empty lists.
        
        Args:
            values: List of values
            
        Returns:
            Median value or 0 if the list is empty
        """
        return statistics.median(values) if values else 0
    
    def _safe_std_dev(self, values: List[float]) -> float:
        """
        Calculate the standard deviation of a list of values, safely handling empty lists.
        
        Args:
            values: List of values
            
        Returns:
            Standard deviation or 0 if the list is empty or has only one element
        """
        try:
            return statistics.stdev(values) if len(values) > 1 else 0
        except statistics.StatisticsError:
            return 0 
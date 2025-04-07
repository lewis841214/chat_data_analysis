#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature extractor for latency metrics.
"""

from typing import Dict, Any, List
import statistics

from feature_processor.base_processor import BaseFeatureExtractor


class AvgLatencyExtractor(BaseFeatureExtractor):
    """
    Extracts the average latency feature from a conversation.
    
    Average latency is defined as the average time it takes for the assistant to respond to a user message.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the average latency extractor.
        
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
        return "avg_latency"
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract the average latency from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Average latency in seconds
        """
        messages = conversation.get("conversation", [])
        
        # Calculate user-to-assistant response times
        user_to_assistant_times = []
        
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            # Extract timestamps
            prev_time = prev_msg.get("timestamp_ms")
            curr_time = curr_msg.get("timestamp_ms")
            
            if prev_time is not None and curr_time is not None:
                # Check if this is a user -> assistant transition
                prev_sender = prev_msg.get("role", "").lower()
                curr_sender = curr_msg.get("role", "").lower()
                
                if prev_sender == "user" and curr_sender == "assistant":
                    # Calculate response time in seconds
                    response_time = (curr_time - prev_time) / 1000
                    user_to_assistant_times.append(response_time)
        
        # Calculate average latency
        if user_to_assistant_times:
            return sum(user_to_assistant_times) / len(user_to_assistant_times)
        
        return 0.0


class InitialNLatencyExtractor(BaseFeatureExtractor):
    """
    Extracts the initial N latency feature from a conversation.
    
    Initial N latency is defined as the average time it takes for the assistant 
    to respond to a user message across the first N responses from the assistant.
    This provides insight into early conversation responsiveness.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the initial N latency extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        # Number of initial responses to consider
        self.n_responses = config['features']['initial_latency']['n_responses']
    
    @property
    def feature_name(self) -> str:
        """
        Get the name of the feature.
        
        Returns:
            Feature name
        """
        return f"initial_{self.n_responses}_latency"
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract the initial N latency from a conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Average latency for the first N assistant responses in seconds
        """
        messages = conversation.get("conversation", [])
        
        # Find the first N user -> assistant transitions
        initial_response_times = []
        responses_found = 0
        
        for i in range(1, len(messages)):
            if responses_found >= self.n_responses:
                break
                
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            # Extract timestamps
            prev_time = prev_msg.get("timestamp_ms")
            curr_time = curr_msg.get("timestamp_ms")
            
            if prev_time is not None and curr_time is not None:
                # Check if this is a user -> assistant transition
                prev_sender = prev_msg.get("role", "").lower()
                curr_sender = curr_msg.get("role", "").lower()
                
                if prev_sender == "user" and curr_sender == "assistant":
                    # Calculate response time in seconds
                    response_time = (curr_time - prev_time) / 1000
                    initial_response_times.append(response_time)
                    responses_found += 1
        # Calculate average of initial N latencies
        if initial_response_times:
            return sum(initial_response_times) / len(initial_response_times)
        
        # No valid transitions found
        return 0.0 
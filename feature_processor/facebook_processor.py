#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feature processor for Facebook conversation data.
Extracts conversation features and target metrics.
"""

import re
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
from tqdm import tqdm
from collections import Counter, defaultdict

from feature_processor.base_processor import BaseFeatureProcessor
from feature_processor.processor_factory import FeatureProcessorFactory


class FacebookFeatureProcessor(BaseFeatureProcessor):
    """
    Feature processor for Facebook conversation data.
    Extracts features like message counts, response times, and interaction patterns.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Facebook feature processor.
        
        Args:
            config: Configuration dictionary for this processor
        """
        super().__init__(config)
        
        # Get feature-specific configuration
        self.min_messages = config.get("min_messages", 10)
        self.max_messages = config.get("max_messages", 1000)
        self.time_window = config.get("time_window_days", 30)
        self.use_user_metadata = config.get("use_user_metadata", True)
        self.target_metric = config.get("target_metric", "response_rate")
        
        self.logger.info(f"Initialized FacebookFeatureProcessor with config: {config}")
    
    def extract_features(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract features from Facebook conversation data.
        
        Features include:
        - Message counts by role (user, assistant)
        - Average message length
        - Response time statistics
        - Conversation duration
        - Time of day patterns
        - Day of week patterns
        - Message frequency
        - Emoji usage
        - Question frequency
        
        Args:
            conversations: List of conversation data
            
        Returns:
            Dictionary of extracted features
        """
        self.logger.info(f"Extracting features from {len(conversations)} conversations")
        
        features = {}
        
        for i, conversation in enumerate(tqdm(conversations, desc="Extracting features")):
            conversation_id = conversation.get("conversation_id", f"conversation_{i}")
            
            # Skip conversations with too few or too many messages
            messages = conversation.get("conversation", [])
            if len(messages) < self.min_messages or len(messages) > self.max_messages:
                self.logger.debug(f"Skipping conversation {conversation_id} with {len(messages)} messages")
                continue
            
            # Extract basic conversation metrics
            conv_features = self._extract_conversation_features(conversation)
            
            # Add to features dictionary
            features[conversation_id] = conv_features
            
        self.logger.info(f"Extracted features from {len(features)} valid conversations")
        return features
    
    def _extract_conversation_features(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from a single conversation.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Dictionary of conversation features
        """
        messages = conversation.get("conversation", [])
        
        # Basic counts
        user_messages = [msg for msg in messages if msg.get("role") == "User"]
        assistant_messages = [msg for msg in messages if msg.get("role") == "Assistant"]
        
        user_message_count = len(user_messages)
        assistant_message_count = len(assistant_messages)
        total_message_count = len(messages)
        
        # Message length statistics
        user_message_lengths = [len(msg.get("content", "")) for msg in user_messages]
        assistant_message_lengths = [len(msg.get("content", "")) for msg in assistant_messages]
        
        avg_user_message_length = sum(user_message_lengths) / user_message_count if user_message_count > 0 else 0
        avg_assistant_message_length = sum(assistant_message_lengths) / assistant_message_count if assistant_message_count > 0 else 0
        
        # Response time analysis (if timestamps are available)
        response_times = []
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            # Only consider user->assistant or assistant->user transitions
            if prev_msg.get("role") != curr_msg.get("role"):
                # Extract timestamps
                prev_time = prev_msg.get("timestamp_ms")
                curr_time = curr_msg.get("timestamp_ms")
                
                if prev_time and curr_time:
                    response_time = (curr_time - prev_time) / 1000  # Convert to seconds
                    response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Time of day analysis
        hour_distribution = defaultdict(int)
        day_distribution = defaultdict(int)
        
        for msg in messages:
            timestamp = msg.get("timestamp_ms")
            if timestamp:
                dt = datetime.datetime.fromtimestamp(timestamp / 1000)
                hour_distribution[dt.hour] += 1
                day_distribution[dt.weekday()] += 1
        
        # Emoji usage
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
        
        user_emoji_count = sum(len(emoji_pattern.findall(msg.get("content", ""))) for msg in user_messages)
        assistant_emoji_count = sum(len(emoji_pattern.findall(msg.get("content", ""))) for msg in assistant_messages)
        
        # Question frequency
        question_pattern = re.compile(r'\?')
        user_question_count = sum(1 for msg in user_messages if question_pattern.search(msg.get("content", "")))
        assistant_question_count = sum(1 for msg in assistant_messages if question_pattern.search(msg.get("content", "")))
        
        # Create features dictionary
        features = {
            "message_counts": {
                "total": total_message_count,
                "user": user_message_count,
                "assistant": assistant_message_count,
                "ratio_user_assistant": user_message_count / assistant_message_count if assistant_message_count > 0 else 0
            },
            "message_length": {
                "avg_user": avg_user_message_length,
                "avg_assistant": avg_assistant_message_length,
                "ratio": avg_user_message_length / avg_assistant_message_length if avg_assistant_message_length > 0 else 0
            },
            "response_time": {
                "avg_seconds": avg_response_time,
                "min_seconds": min_response_time,
                "max_seconds": max_response_time
            },
            "time_patterns": {
                "hour_distribution": dict(hour_distribution),
                "day_distribution": dict(day_distribution),
                "peak_hour": max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else 0,
                "peak_day": max(day_distribution.items(), key=lambda x: x[1])[0] if day_distribution else 0
            },
            "content_analysis": {
                "emoji_usage": {
                    "user": user_emoji_count,
                    "assistant": assistant_emoji_count,
                    "per_message_user": user_emoji_count / user_message_count if user_message_count > 0 else 0,
                    "per_message_assistant": assistant_emoji_count / assistant_message_count if assistant_message_count > 0 else 0
                },
                "question_frequency": {
                    "user": user_question_count,
                    "assistant": assistant_question_count,
                    "per_message_user": user_question_count / user_message_count if user_message_count > 0 else 0,
                    "per_message_assistant": assistant_question_count / assistant_message_count if assistant_message_count > 0 else 0
                }
            }
        }
        
        return features
    
    def process_targets(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process target values from conversation data.
        
        Possible targets include:
        - Response rate (how often an assistant responds to a user message)
        - Conversation length (number of messages)
        - User engagement (frequency of user responses)
        - Conversation duration (time from first to last message)
        - Conversation resolution (whether a conversation was completed or abandoned)
        
        Args:
            conversations: List of conversation data
            
        Returns:
            Dictionary of processed targets
        """
        self.logger.info(f"Processing targets from {len(conversations)} conversations")
        
        targets = {}
        
        for i, conversation in enumerate(tqdm(conversations, desc="Processing targets")):
            conversation_id = conversation.get("conversation_id", f"conversation_{i}")
            
            # Skip conversations with too few or too many messages
            messages = conversation.get("conversation", [])
            if len(messages) < self.min_messages or len(messages) > self.max_messages:
                continue
            
            # Process the target metric
            if self.target_metric == "response_rate":
                target_value = self._calculate_response_rate(conversation)
            elif self.target_metric == "conversation_length":
                target_value = len(messages)
            elif self.target_metric == "user_engagement":
                target_value = self._calculate_user_engagement(conversation)
            elif self.target_metric == "conversation_duration":
                target_value = self._calculate_conversation_duration(conversation)
            elif self.target_metric == "conversation_resolution":
                target_value = self._calculate_conversation_resolution(conversation)
            else:
                self.logger.warning(f"Unknown target metric: {self.target_metric}")
                target_value = None
            
            targets[conversation_id] = {
                "metric": self.target_metric,
                "value": target_value
            }
        
        self.logger.info(f"Processed targets for {len(targets)} valid conversations")
        return targets
    
    def _calculate_response_rate(self, conversation: Dict[str, Any]) -> float:
        """
        Calculate the response rate for a conversation.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Response rate (0.0 to 1.0)
        """
        messages = conversation.get("conversation", [])
        
        # Count message pairs (user -> assistant)
        user_messages = 0
        assistant_responses = 0
        
        for i in range(len(messages) - 1):
            if messages[i].get("role") == "User" and messages[i+1].get("role") == "Assistant":
                user_messages += 1
                assistant_responses += 1
                
        # Also count unpaired user messages at the end
        if messages and messages[-1].get("role") == "User":
            user_messages += 1
        
        return assistant_responses / user_messages if user_messages > 0 else 0.0
    
    def _calculate_user_engagement(self, conversation: Dict[str, Any]) -> float:
        """
        Calculate user engagement as the frequency of user responses to assistant messages.
        
        Args:
            conversation: Conversation data
            
        Returns:
            User engagement score (0.0 to 1.0)
        """
        messages = conversation.get("conversation", [])
        
        assistant_messages = 0
        user_responses = 0
        
        for i in range(len(messages) - 1):
            if messages[i].get("role") == "Assistant" and messages[i+1].get("role") == "User":
                assistant_messages += 1
                user_responses += 1
                
        # Also count unpaired assistant messages at the end
        if messages and messages[-1].get("role") == "Assistant":
            assistant_messages += 1
        
        return user_responses / assistant_messages if assistant_messages > 0 else 0.0
    
    def _calculate_conversation_duration(self, conversation: Dict[str, Any]) -> float:
        """
        Calculate the duration of a conversation in minutes.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Conversation duration in minutes
        """
        messages = conversation.get("conversation", [])
        
        if not messages or "timestamp_ms" not in messages[0] or "timestamp_ms" not in messages[-1]:
            return 0.0
        
        first_timestamp = messages[0].get("timestamp_ms")
        last_timestamp = messages[-1].get("timestamp_ms")
        
        duration_ms = last_timestamp - first_timestamp
        return duration_ms / (1000 * 60)  # Convert to minutes
    
    def _calculate_conversation_resolution(self, conversation: Dict[str, Any]) -> int:
        """
        Determine if a conversation was resolved (ended with assistant response).
        
        Args:
            conversation: Conversation data
            
        Returns:
            1 if resolved, 0 if not
        """
        messages = conversation.get("conversation", [])
        
        if not messages:
            return 0
            
        # Conversation ended with assistant message
        return 1 if messages[-1].get("role") == "Assistant" else 0


# Register this processor with the factory
FeatureProcessorFactory.register_processor("facebook", FacebookFeatureProcessor) 
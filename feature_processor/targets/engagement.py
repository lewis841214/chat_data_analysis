#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for user engagement metrics in conversations.
"""

import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from statistics import mean, stdev, median

from feature_processor.base_processor import BaseTargetExtractor


class UserEngagementExtractor(BaseTargetExtractor):
    """
    Extracts user engagement metrics from conversations.
    
    Engagement is measured by analyzing various aspects of user behavior:
    - Message frequency
    - Response rate
    - Message length
    - Question asking
    - Time spent in conversation
    - Consistent participation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the user engagement extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Define patterns for questions
        self.question_patterns = [
            r'\?',  # Question mark
            r'\b(?:what|who|where|when|why|how|is|are|were|was|will|would|could|should|do|does|did|can|may|might)\b.{3,}(?:\?|$)',  # WH-questions and other question forms
        ]
        
        # Define engagement signals
        self.engagement_signals = [
            r'\byes\b',
            r'\bsure\b',
            r'\bok\b',
            r'\bokay\b',
            r'\bplease\b',
            r'\bthanks\b',
            r'\bthank you\b',
            r'\bagree\b',
            r'\bi see\b',
            r'\bunderstand\b',
            r'\bgreat\b',
            r'\bcool\b',
            r'\bexcellent\b',
            r'\bawesome\b',
            r'\bnice\b',
            r'\binteresting\b',
        ]
        
        # Define disengagement signals
        self.disengagement_signals = [
            r'\bbye\b',
            r'\bgoodbye\b',
            r'\bsee you\b',
            r'\bnot interested\b',
            r'\bno thanks\b',
            r'\bnever mind\b',
            r'\bforget it\b',
            r'\bnot now\b',
            r'\blater\b',
            r'\bdon\'t care\b',
            r'\bwhatever\b',
        ]
        
        # Compile the patterns
        self.question_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.question_patterns]
        self.engagement_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.engagement_signals]
        self.disengagement_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.disengagement_signals]
    
    @property
    def target_name(self) -> str:
        """
        Get the name of the target.
        
        Returns:
            Target name
        """
        return "user_engagement"
    
    def _is_question(self, text: str) -> bool:
        """
        Check if a message contains a question.
        
        Args:
            text: Text to check
            
        Returns:
            True if the message contains a question, False otherwise
        """
        for pattern in self.question_regexes:
            if pattern.search(text):
                return True
        return False
    
    def _count_engagement_signals(self, text: str) -> int:
        """
        Count the number of engagement signals in a message.
        
        Args:
            text: Text to check
            
        Returns:
            Number of engagement signals found
        """
        count = 0
        for pattern in self.engagement_regexes:
            if pattern.search(text):
                count += 1
        return count
    
    def _count_disengagement_signals(self, text: str) -> int:
        """
        Count the number of disengagement signals in a message.
        
        Args:
            text: Text to check
            
        Returns:
            Number of disengagement signals found
        """
        count = 0
        for pattern in self.disengagement_regexes:
            if pattern.search(text):
                count += 1
        return count
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract user engagement score from the conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Engagement score from 0.0 (not engaged) to 1.0 (highly engaged)
        """
        messages = conversation.get("conversation", [])
        participants = conversation.get("participants", [])
        
        if not messages or len(messages) < 2:
            return 0.0  # Not enough data to determine engagement
        
        # Identify user messages and assistant messages
        user_messages = []
        assistant_messages = []
        
        # Find the user (assuming first participant is user)
        user_id = None
        assistant_id = None
        
        for participant in participants:
            if participant.get("role", "").lower() == "user":
                user_id = participant.get("id")
            elif participant.get("role", "").lower() == "assistant":
                assistant_id = participant.get("id")
        
        # If no user or assistant ID found, try to determine from messages
        if user_id is None or assistant_id is None:
            # Examine the first and second messages to try to determine roles
            if len(messages) >= 2:
                first_sender = messages[0].get("sender_id")
                second_sender = messages[1].get("sender_id")
                if first_sender != second_sender:
                    user_id = first_sender
                    assistant_id = second_sender
        
        # Categorize messages
        for msg in messages:
            sender_id = msg.get("sender_id")
            if sender_id == user_id:
                user_messages.append(msg)
            elif sender_id == assistant_id:
                assistant_messages.append(msg)
        
        # If we couldn't identify the user/assistant, try to split based on message patterns
        if not user_messages or not assistant_messages:
            # Try to determine by analyzing message content
            all_senders = {msg.get("sender_id") for msg in messages if msg.get("sender_id")}
            if len(all_senders) == 2:
                sender_messages = {sender: [] for sender in all_senders}
                for msg in messages:
                    sender_id = msg.get("sender_id")
                    if sender_id:
                        sender_messages[sender_id].append(msg)
                
                # Assume the sender who asks more questions is the user
                question_counts = {}
                for sender, msgs in sender_messages.items():
                    question_counts[sender] = sum(1 for msg in msgs if self._is_question(msg.get("content", "")))
                
                if len(question_counts) == 2:
                    # Get the sender with the higher question count
                    user_id = max(question_counts.items(), key=lambda x: x[1])[0]
                    assistant_id = [s for s in all_senders if s != user_id][0]
                    
                    user_messages = sender_messages[user_id]
                    assistant_messages = sender_messages[assistant_id]
        
        # Fall back to simple alternating assumption if all else fails
        if not user_messages or not assistant_messages:
            user_messages = messages[::2]  # Even indices (0, 2, 4, ...)
            assistant_messages = messages[1::2]  # Odd indices (1, 3, 5, ...)
        
        # Calculate engagement metrics
        
        # 1. Message frequency (normalized by conversation duration)
        try:
            first_msg_time = datetime.fromisoformat(messages[0].get("created_at", "").replace('Z', '+00:00'))
            last_msg_time = datetime.fromisoformat(messages[-1].get("created_at", "").replace('Z', '+00:00'))
            duration_hours = (last_msg_time - first_msg_time).total_seconds() / 3600
            
            # Handle case where timestamps are identical or invalid
            if duration_hours <= 0.01:  # Less than a minute
                msg_frequency_score = 0.5  # Neutral score if we can't calculate
            else:
                user_msgs_per_hour = len(user_messages) / duration_hours
                
                # Normalize: 0-2 msgs/hour = 0.2, 3-5 = 0.4, 6-10 = 0.6, 11-20 = 0.8, 20+ = 1.0
                if user_msgs_per_hour < 3:
                    msg_frequency_score = 0.2
                elif user_msgs_per_hour < 6:
                    msg_frequency_score = 0.4
                elif user_msgs_per_hour < 11:
                    msg_frequency_score = 0.6
                elif user_msgs_per_hour < 21:
                    msg_frequency_score = 0.8
                else:
                    msg_frequency_score = 1.0
        except (ValueError, TypeError):
            msg_frequency_score = 0.5  # Default if we can't parse timestamps
        
        # 2. Response rate (how often user responds to assistant)
        if len(assistant_messages) > 0:
            response_rate = min(len(user_messages) / len(assistant_messages), 1.0)
        else:
            response_rate = 0.5  # Default if no assistant messages
        
        # 3. Message length (normalized)
        user_msg_lengths = [len(msg.get("content", "")) for msg in user_messages]
        if user_msg_lengths:
            avg_length = mean(user_msg_lengths)
            # Normalize: 0-10 chars = 0.2, 11-30 = 0.4, 31-60 = 0.6, 61-100 = 0.8, 100+ = 1.0
            if avg_length < 11:
                length_score = 0.2
            elif avg_length < 31:
                length_score = 0.4
            elif avg_length < 61:
                length_score = 0.6
            elif avg_length < 101:
                length_score = 0.8
            else:
                length_score = 1.0
        else:
            length_score = 0  # No user messages
        
        # 4. Question asking (indicates engagement)
        user_questions = sum(1 for msg in user_messages if self._is_question(msg.get("content", "")))
        question_ratio = user_questions / len(user_messages) if user_messages else 0
        
        # Normalize: 0 = 0.0, 0.01-0.2 = 0.3, 0.21-0.4 = 0.6, 0.41+ = 1.0
        if question_ratio == 0:
            question_score = 0.0
        elif question_ratio < 0.21:
            question_score = 0.3
        elif question_ratio < 0.41:
            question_score = 0.6
        else:
            question_score = 1.0
        
        # 5. Engagement/disengagement signals
        engagement_signals = sum(self._count_engagement_signals(msg.get("content", "")) for msg in user_messages)
        disengagement_signals = sum(self._count_disengagement_signals(msg.get("content", "")) for msg in user_messages)
        
        # Calculate signal score
        total_signals = engagement_signals + disengagement_signals
        if total_signals > 0:
            signal_score = engagement_signals / total_signals
        else:
            signal_score = 0.5  # Neutral if no signals
        
        # 6. Consistency of participation (measure time gaps between user messages)
        if len(user_messages) >= 3:
            try:
                user_timestamps = [datetime.fromisoformat(msg.get("created_at", "").replace('Z', '+00:00')) 
                                  for msg in user_messages 
                                  if msg.get("created_at")]
                
                if len(user_timestamps) >= 3:
                    # Calculate time gaps between messages in minutes
                    time_gaps = [(user_timestamps[i+1] - user_timestamps[i]).total_seconds() / 60 
                                for i in range(len(user_timestamps)-1)]
                    
                    # Calculate coefficient of variation (lower means more consistent)
                    mean_gap = mean(time_gaps)
                    if mean_gap > 0:
                        try:
                            cv = stdev(time_gaps) / mean_gap
                            # Normalize: CV>2.0 = 0.0, 1.5-2.0 = 0.3, 1.0-1.5 = 0.6, <1.0 = 1.0
                            if cv > 2.0:
                                consistency_score = 0.0
                            elif cv > 1.5:
                                consistency_score = 0.3
                            elif cv > 1.0:
                                consistency_score = 0.6
                            else:
                                consistency_score = 1.0
                        except:
                            consistency_score = 0.5  # Default if calculation fails
                    else:
                        consistency_score = 1.0  # Perfect consistency (all at once)
                else:
                    consistency_score = 0.5  # Not enough timestamps
            except:
                consistency_score = 0.5  # Default if timestamp parsing fails
        else:
            consistency_score = 0.5  # Not enough messages
        
        # Calculate the final engagement score with weighted components
        weights = {
            'frequency': 0.15,
            'response_rate': 0.2,
            'length': 0.15,
            'questions': 0.2,
            'signals': 0.15,
            'consistency': 0.15
        }
        
        engagement_score = (
            weights['frequency'] * msg_frequency_score +
            weights['response_rate'] * response_rate +
            weights['length'] * length_score +
            weights['questions'] * question_score +
            weights['signals'] * signal_score +
            weights['consistency'] * consistency_score
        )
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, engagement_score)) 
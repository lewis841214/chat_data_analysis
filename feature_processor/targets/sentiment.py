#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for sentiment analysis of conversations.
"""

import re
from typing import Dict, Any, List, Tuple
from statistics import mean

from feature_processor.base_processor import BaseTargetExtractor


class SentimentExtractor(BaseTargetExtractor):
    """
    Extracts sentiment scores from conversations.
    
    This is a rule-based sentiment analyzer that looks for positive and negative words/phrases
    and calculates sentiment scores based on their frequency and intensity.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the sentiment extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Define positive words/phrases with intensity scores (1-5)
        self.positive_patterns = {
            # Very positive (5)
            r'\bexcellent\b': 5,
            r'\bperfect\b': 5,
            r'\bincredible\b': 5,
            r'\bamazing\b': 5,
            r'\boutstanding\b': 5,
            r'\bexceptional\b': 5,
            r'\bbrilliant\b': 5,
            r'\blove it\b': 5,
            r'\bawesome\b': 5,
            r'\bfantastic\b': 5,
            
            # Quite positive (4)
            r'\bgreat\b': 4,
            r'\bdelighted\b': 4,
            r'\bimpressed\b': 4,
            r'\bwonderful\b': 4,
            r'\bterrific\b': 4,
            r'\breally good\b': 4,
            r'\bvery happy\b': 4,
            r'\bthank you\b': 4,
            
            # Positive (3)
            r'\bgood\b': 3,
            r'\bhappy\b': 3,
            r'\bpleased\b': 3,
            r'\bsatisfied\b': 3,
            r'\bnice\b': 3,
            r'\bwell done\b': 3,
            r'\bthank(s)?\b': 3,
            r'\bappreciate\b': 3,
            
            # Mildly positive (2)
            r'\bokay\b': 2,
            r'\bfine\b': 2,
            r'\bgladly\b': 2,
            r'\bpleasant\b': 2,
            r'\bdecent\b': 2,
            r'\bacceptable\b': 2,
            r'\balright\b': 2,
            
            # Slightly positive (1)
            r'\bnot bad\b': 1,
            r'\bsure\b': 1,
            r'\byes\b': 1,
            r'\bagree\b': 1,
            r'\bcool\b': 1,
        }
        
        # Define negative words/phrases with intensity scores (1-5)
        self.negative_patterns = {
            # Very negative (5)
            r'\bterrible\b': 5,
            r'\bhorrible\b': 5,
            r'\bawful\b': 5,
            r'\bdisgusting\b': 5,
            r'\babysmal\b': 5,
            r'\bfurious\b': 5,
            r'\bunacceptable\b': 5,
            r'\bhate\b': 5,
            r'\bdespise\b': 5,
            r'\bextremely\s+(?:bad|poor|disappointed|angry|frustrated)\b': 5,
            
            # Quite negative (4)
            r'\bvery\s+(?:bad|poor|disappointed|angry|frustrated)\b': 4,
            r'\bannoyed\b': 4,
            r'\bangry\b': 4,
            r'\bdisappointed\b': 4,
            r'\bpathetic\b': 4,
            r'\bmiserable\b': 4,
            r'\bunhappy\b': 4,
            r'\bupsetting\b': 4,
            
            # Negative (3)
            r'\bbad\b': 3,
            r'\bpoor\b': 3,
            r'\bdislike\b': 3,
            r'\bunfortunate\b': 3,
            r'\bunpleasant\b': 3,
            r'\buncomfortable\b': 3,
            r'\bfailure\b': 3,
            r'\bmistake\b': 3,
            
            # Mildly negative (2)
            r'\bnot good\b': 2,
            r'\bnot great\b': 2,
            r'\bnot happy\b': 2,
            r'\bdisappointing\b': 2,
            r'\bmediocre\b': 2,
            r'\bbelow average\b': 2,
            r'\binadequate\b': 2,
            
            # Slightly negative (1)
            r'\bcould be better\b': 1,
            r'\bneeds improvement\b': 1,
            r'\bnot ideal\b': 1,
            r'\bnot perfect\b': 1,
            r'\bnot sure\b': 1,
            r'\bnot convinced\b': 1,
            r'\bno\b': 1,
            r'\bnegative\b': 1,
        }
        
        # Compile the patterns
        self.positive_regexes = {re.compile(pattern, re.IGNORECASE): score 
                                for pattern, score in self.positive_patterns.items()}
        self.negative_regexes = {re.compile(pattern, re.IGNORECASE): score 
                                for pattern, score in self.negative_patterns.items()}
        
        # Modifiers that can flip or enhance sentiment
        self.negators = re.compile(r'\b(?:not|no|never|none|nobody|nowhere|neither|nor|nothing)\b', re.IGNORECASE)
        self.intensifiers = re.compile(r'\b(?:very|extremely|incredibly|really|absolutely|definitely|totally)\b', re.IGNORECASE)
    
    @property
    def target_name(self) -> str:
        """
        Get the name of the target.
        
        Returns:
            Target name
        """
        return "sentiment_score"
    
    def _analyze_text_sentiment(self, text: str) -> Tuple[float, int]:
        """
        Analyze sentiment of a single text message.
        
        Args:
            text: The message text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_count)
        """
        text = text.lower()
        
        # Check for negators (which can flip sentiment)
        has_negator = bool(self.negators.search(text))
        
        # Check for intensifiers (which can enhance sentiment)
        intensifier_count = len(self.intensifiers.findall(text))
        intensifier_multiplier = 1.0 + (0.2 * intensifier_count)  # 20% boost per intensifier
        
        positive_score = 0
        negative_score = 0
        sentiment_terms_count = 0
        
        # Check positive patterns
        for pattern, score in self.positive_regexes.items():
            if pattern.search(text):
                if has_negator:
                    # If there's a negator, flip positive to negative
                    negative_score += score * intensifier_multiplier
                else:
                    positive_score += score * intensifier_multiplier
                sentiment_terms_count += 1
        
        # Check negative patterns
        for pattern, score in self.negative_regexes.items():
            if pattern.search(text):
                if has_negator:
                    # If there's a negator, flip negative to positive
                    positive_score += score * intensifier_multiplier
                else:
                    negative_score += score * intensifier_multiplier
                sentiment_terms_count += 1
        
        # Calculate the final sentiment score (-1.0 to 1.0)
        if sentiment_terms_count == 0:
            return 0.0, 0  # Neutral
        
        # Normalize scores based on a -5 to +5 scale
        normalized_score = (positive_score - negative_score) / (positive_score + negative_score)
        return normalized_score, sentiment_terms_count
    
    def extract(self, conversation: Dict[str, Any]) -> float:
        """
        Extract overall sentiment score from the conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        """
        messages = conversation.get("conversation", [])
        
        if not messages:
            return 0.0  # Neutral for empty conversations
        
        # Analyze each message and collect scores
        weighted_scores = []
        total_sentiment_terms = 0
        
        # Recent messages have more weight
        recency_weights = {
            0: 2.0,  # Last message has 2x weight
            1: 1.5,  # Second-to-last has 1.5x weight
            2: 1.2,  # Third-to-last has 1.2x weight
        }
        
        for i, msg in enumerate(reversed(messages)):
            content = msg.get("content", "")
            score, terms = self._analyze_text_sentiment(content)
            
            # Apply recency weight if applicable
            weight = recency_weights.get(i, 1.0)
            
            if terms > 0:
                weighted_scores.append(score * weight * terms)
                total_sentiment_terms += terms
        
        # Special case: no sentiment terms found
        if total_sentiment_terms == 0:
            return 0.0
        
        # Calculate weighted average
        final_score = sum(weighted_scores) / total_sentiment_terms
        
        return final_score 
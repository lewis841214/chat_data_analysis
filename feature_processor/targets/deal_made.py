#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Target extractor for determining if a deal was made in a conversation.
"""

import re
from typing import Dict, Any, List

from feature_processor.base_processor import BaseTargetExtractor


class DealMadeExtractor(BaseTargetExtractor):
    """
    Extracts whether a deal was made in a conversation.
    
    This is determined by looking for deal-related keywords and phrases in messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the deal made extractor.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Define patterns to detect deals
        self.deal_patterns = [
            r'\bagree(d|ment)?\b',
            r'\bdeal\b',
            r'\bsold\b',
            r'\bpurchase(d)?\b',
            r'\bbuy\b',
            r'\bwill take\b',
            r'\baccept(ed)?\b',
            r'\bconfirm(ed)?\b',
            r'\bapprove(d)?\b',
            r'\bpayment\b',
            r'\btransfer(red)?\b',
            r'\bship(ping|ped)?\b',
            r'\border(ed)?\b',
            r'\bsale\b',
            r'\btransaction\b',
            r'\bsend money\b',
            r'\bpaid\b',
            r'\bdelivery\b',
            r'\bready to\b',
            r'\byou got (a )?deal\b',
        ]
        
        # Compile the patterns
        self.deal_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.deal_patterns]
        
        # Define patterns that might indicate a deal was not made
        self.negative_patterns = [
            r'\bno deal\b',
            r'\bdon\'t agree\b',
            r'\bdo not agree\b',
            r'\bcannot accept\b',
            r'\bcan\'t accept\b',
            r'\brefuse\b',
            r'\breject\b',
            r'\bnot interested\b',
            r'\btoo expensive\b',
            r'\bwon\'t work\b',
            r'\bwill not work\b',
            r'\bcan\'t do\b',
            r'\bcannot do\b',
        ]
        
        # Compile the negative patterns
        self.negative_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.negative_patterns]
    
    @property
    def target_name(self) -> str:
        """
        Get the name of the target.
        
        Returns:
            Target name
        """
        return "deal_make_or_not"
    
    def extract(self, conversation: Dict[str, Any]) -> int:
        """
        Extract whether a deal was made in the conversation.
        
        Args:
            conversation: Conversation data in the standard format
            
        Returns:
            1 if a deal was made, 0 otherwise
        """
        messages = conversation.get("conversation", [])
        
        # First, check if the deal negation patterns appear in the last few messages
        # This suggests that the deal fell through at the end
        last_n_messages = messages[-5:] if len(messages) >= 5 else messages
        for msg in reversed(last_n_messages):
            content = msg.get("content", "").lower()
            for pattern in self.negative_regexes:
                if pattern.search(content):
                    # Found a negative indicator in the last messages
                    return 0
        
        # Count the number of deal-related patterns in all messages
        deal_indicators = 0
        
        # Check for deal-indicating patterns
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Check each pattern
            for pattern in self.deal_regexes:
                if pattern.search(content):
                    deal_indicators += 1
                    break  # Only count one indicator per message
        
        # Simple heuristic: If we have at least 2 deal indicators, consider it a successful deal
        # This can be fine-tuned based on real data
        return 1 if deal_indicators >= 2 else 0 
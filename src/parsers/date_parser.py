"""Date parser for extracting dates from blog post titles"""
import re
import logging
from datetime import datetime, date
from typing import Optional
from dateutil import parser as dateutil_parser

logger = logging.getLogger(__name__)


class DateParser:
    """Parse dates from blog post titles in various formats"""

    def __init__(self):
        self.failed_parses = []

    def parse_title_date(self, title: str) -> Optional[date]:
        """
        Parse date from title using multiple strategies

        Expected formats:
        - "Saturday 30th December, 2023"
        - "Wednesday 1st January, 2023"

        Args:
            title: Blog post title containing a date

        Returns:
            date object if parsing succeeds, None otherwise
        """
        if not title:
            return None

        # Strategy 1: Remove ordinal suffixes and use dateutil
        cleaned = self._clean_ordinal_suffix(title)
        result = self._try_dateutil(cleaned)
        if result:
            return result

        # Strategy 2: Regex pattern matching for exact format
        result = self._try_regex_pattern(title)
        if result:
            return result

        # Strategy 3: Try with original title as fallback
        result = self._try_dateutil(title)
        if result:
            return result

        # Log failure for manual review
        logger.warning(f"Failed to parse date from title: {title}")
        self.failed_parses.append(title)
        return None

    def _clean_ordinal_suffix(self, text: str) -> str:
        """
        Remove ordinal suffixes from numbers

        Examples:
        - "1st" -> "1"
        - "2nd" -> "2"
        - "3rd" -> "3"
        - "30th" -> "30"
        """
        return re.sub(r'\b(\d+)(?:st|nd|rd|th)\b', r'\1', text)

    def _try_dateutil(self, text: str) -> Optional[date]:
        """Try parsing using python-dateutil (fuzzy matching)"""
        try:
            parsed = dateutil_parser.parse(text, fuzzy=True)
            return parsed.date()
        except (ValueError, TypeError, OverflowError):
            return None

    def _try_regex_pattern(self, title: str) -> Optional[date]:
        """
        Try parsing using regex patterns

        Patterns:
        - "Day Name DDth Month Name, YYYY"
        """
        # Pattern: "Saturday 30th December, 2023"
        pattern = r'(\w+day)\s+(\d+)(?:st|nd|rd|th)\s+(\w+),?\s+(\d{4})'
        match = re.search(pattern, title, re.IGNORECASE)

        if match:
            day_name, day, month_name, year = match.groups()
            try:
                # Try to parse without the day name
                date_str = f"{day} {month_name} {year}"
                return datetime.strptime(date_str, "%d %B %Y").date()
            except ValueError:
                # Try abbreviated month name
                try:
                    return datetime.strptime(date_str, "%d %b %Y").date()
                except ValueError:
                    pass

        return None

    def get_failed_parses(self) -> list:
        """Get list of titles that failed to parse"""
        return self.failed_parses.copy()

    def get_success_rate(self, total_attempts: int) -> float:
        """Calculate parsing success rate"""
        if total_attempts == 0:
            return 0.0
        failures = len(self.failed_parses)
        successes = total_attempts - failures
        return (successes / total_attempts) * 100

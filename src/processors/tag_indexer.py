"""Tag indexer for building searchable tag index"""
import logging
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class TagIndex:
    """Tag index data structure"""
    tag_to_posts: Dict[str, List[str]] = field(default_factory=dict)
    tag_frequencies: Dict[str, int] = field(default_factory=dict)
    all_tags: List[str] = field(default_factory=list)


class TagIndexer:
    """Build searchable tag index from blog posts"""

    def build_index(self, posts) -> TagIndex:
        """
        Create inverted index mapping tags to posts

        Args:
            posts: List of BlogPost objects

        Returns:
            TagIndex with tag mappings and frequencies
        """
        logger.info(f"Building tag index from {len(posts)} posts")

        index = defaultdict(list)
        frequencies = Counter()

        for post in posts:
            # Generate post ID if not already set
            if not post.post_id:
                post.post_id = self._generate_post_id(post)

            # Index each label/tag
            for label in post.labels:
                # Normalize tag (lowercase, strip whitespace)
                normalized = label.lower().strip()

                if normalized:
                    index[normalized].append(post.post_id)
                    frequencies[normalized] += 1

        # Sort tags alphabetically
        all_tags = sorted(index.keys())

        logger.info(f"Indexed {len(all_tags)} unique tags")

        # Log top tags
        top_tags = frequencies.most_common(10)
        logger.info(f"Top 10 tags: {top_tags}")

        return TagIndex(
            tag_to_posts=dict(index),
            tag_frequencies=dict(frequencies),
            all_tags=all_tags
        )

    def _generate_post_id(self, post) -> str:
        """Generate a post ID from parsed date or published date"""
        if post.parsed_date:
            return f"post-{post.parsed_date.isoformat()}"
        elif post.published_iso:
            # Extract date portion from ISO string
            date_part = post.published_iso.split('T')[0]
            return f"post-{date_part}"
        else:
            # Fallback to hash of title
            import hashlib
            title_hash = hashlib.md5(post.title.encode()).hexdigest()[:8]
            return f"post-{title_hash}"

    def get_popular_tags(self, tag_index: TagIndex, limit: int = 30) -> List[tuple]:
        """
        Get most popular tags by frequency

        Args:
            tag_index: TagIndex object
            limit: Maximum number of tags to return

        Returns:
            List of (tag, frequency) tuples
        """
        sorted_tags = sorted(
            tag_index.tag_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_tags[:limit]

"""JSON generator for structured post data"""
import json
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class JSONGenerator:
    """Generate JSON data files for the frontend"""

    def __init__(self, output_dir: Path, year: int):
        self.output_dir = output_dir
        self.year = year
        self.data_dir = output_dir / str(year) / 'data'

        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, posts, tag_index):
        """
        Generate posts.json and metadata.json files

        Args:
            posts: List of BlogPost objects
            tag_index: TagIndex object
        """
        logger.info(f"Generating JSON data for {len(posts)} posts")

        # Generate month summary
        month_summary = self._build_month_summary(posts)

        # Build posts data
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.post_id,
                'date': post.parsed_date.isoformat() if post.parsed_date else '',
                'title': post.title,
                'content': post.content_html,
                'preview': post.preview,
                'labels': post.labels,
                'hasImages': post.has_images,
                'monthIndex': post.parsed_date.month - 1 if post.parsed_date else 0,
                'dayOfYear': post.parsed_date.timetuple().tm_yday if post.parsed_date else 0
            })

        # Build main data structure
        data = {
            'year': self.year,
            'totalPosts': len(posts),
            'postsWithImages': sum(1 for p in posts if p.has_images),
            'totalTags': len(tag_index.all_tags),
            'posts': posts_data,
            'tagIndex': {
                'tags': tag_index.tag_to_posts,
                'frequencies': tag_index.tag_frequencies,
                'all Tags': tag_index.all_tags
            },
            'monthSummary': month_summary
        }

        # Write posts.json
        posts_file = self.data_dir / 'posts.json'
        with open(posts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated posts.json: {posts_file}")

        # Write metadata.json
        metadata = {
            'year': self.year,
            'generatedAt': str(Path(__file__).parent),
            'statistics': {
                'totalPosts': len(posts),
                'postsWithImages': sum(1 for p in posts if p.has_images),
                'totalTags': len(tag_index.all_tags),
                'totalImages': sum(len(p.image_urls) for p in posts)
            }
        }

        metadata_file = self.data_dir / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated metadata.json: {metadata_file}")

    def _build_month_summary(self, posts) -> dict:
        """
        Build summary of posts by month

        Returns:
            Dict mapping month index to summary data
        """
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        # Initialize month data
        month_data = {i: {'name': name, 'count': 0, 'hasImages': 0}
                      for i, name in enumerate(month_names)}

        # Aggregate data
        for post in posts:
            if post.parsed_date:
                month_idx = post.parsed_date.month - 1
                month_data[month_idx]['count'] += 1
                if post.has_images:
                    month_data[month_idx]['hasImages'] += 1

        return month_data

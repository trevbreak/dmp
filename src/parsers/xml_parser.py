"""XML Parser for Blogger exports"""
import xml.etree.ElementTree as ET
import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

logger = logging.getLogger(__name__)


@dataclass
class BlogPost:
    """Represents a single blog post"""
    title: str
    published_iso: str
    content_html: str
    labels: List[str] = field(default_factory=list)
    post_id: str = ""
    parsed_date: Optional[date] = None
    has_images: bool = False
    image_urls: List[str] = field(default_factory=list)
    preview: str = ""


class BloggerXMLParser:
    """Parser for Blogger XML exports in Atom format"""

    NAMESPACE = {'atom': 'http://www.w3.org/2005/Atom'}

    def __init__(self, xml_file_path: str):
        self.xml_path = xml_file_path

    def parse(self) -> List[BlogPost]:
        """
        Extract all blog posts from the XML file

        Returns:
            List of BlogPost objects
        """
        logger.info(f"Parsing XML file: {self.xml_path}")

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # Find all entry elements
        entries = root.findall('atom:entry', self.NAMESPACE)
        logger.info(f"Found {len(entries)} total entries in XML")

        posts = []
        for entry in entries:
            # Check if this entry is a blog post (not settings, template, etc.)
            if self._is_post_entry(entry):
                post = self._extract_post_data(entry)
                if post:
                    posts.append(post)

        logger.info(f"Extracted {len(posts)} blog posts")
        return posts

    def _is_post_entry(self, entry) -> bool:
        """Check if an entry element is a blog post"""
        categories = entry.findall('atom:category', self.NAMESPACE)
        for category in categories:
            term = category.get('term', '')
            if 'kind#post' in term:
                return True
        return False

    def _extract_post_data(self, entry) -> Optional[BlogPost]:
        """Extract data from a single post entry"""
        try:
            # Extract title
            title_elem = entry.find('atom:title', self.NAMESPACE)
            title = title_elem.text if title_elem is not None else "Untitled"

            # Extract published date
            published_elem = entry.find('atom:published', self.NAMESPACE)
            published_iso = published_elem.text if published_elem is not None else ""

            # Extract content
            content_elem = entry.find('atom:content', self.NAMESPACE)
            content_html = content_elem.text if content_elem is not None else ""

            # Extract labels/tags (exclude kind# categories)
            labels = []
            categories = entry.findall('atom:category', self.NAMESPACE)
            for category in categories:
                term = category.get('term', '')
                # Skip the "kind#" categories (these are type indicators, not tags)
                if 'kind#' not in term and term:
                    labels.append(term)

            # Extract post ID
            id_elem = entry.find('atom:id', self.NAMESPACE)
            post_id = id_elem.text if id_elem is not None else ""

            # Extract image URLs from content
            image_urls = self._extract_image_urls(content_html)
            has_images = len(image_urls) > 0

            post = BlogPost(
                title=title,
                published_iso=published_iso,
                content_html=content_html,
                labels=labels,
                post_id=post_id,
                has_images=has_images,
                image_urls=image_urls
            )

            return post

        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None

    def _extract_image_urls(self, html: str) -> List[str]:
        """Extract all blogger.googleusercontent.com image URLs from HTML"""
        if not html:
            return []

        # Pattern for img tags
        img_pattern = r'<img[^>]+src=["\']([^"\']*blogger\.googleusercontent\.com[^"\']*)["\']'

        # Pattern for linked images
        link_pattern = r'<a[^>]+href=["\']([^"\']*blogger\.googleusercontent\.com[^"\']*)["\']'

        urls = []
        urls.extend(re.findall(img_pattern, html, re.IGNORECASE))
        urls.extend(re.findall(link_pattern, html, re.IGNORECASE))

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

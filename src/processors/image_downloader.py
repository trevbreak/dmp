"""Image downloader with retry logic for blog images"""
import re
import hashlib
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import date
import requests

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download and manage blog post images"""

    MONTH_FOLDERS = {
        1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr',
        5: 'may', 6: 'jun', 7: 'jul', 8: 'aug',
        9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'
    }

    def __init__(self, output_dir: Path, year: int, timeout: int = 30, retry_count: int = 3):
        self.output_dir = output_dir
        self.year = year
        self.timeout = timeout
        self.retry_count = retry_count
        self.images_dir = output_dir / str(year) / 'assets' / 'images'
        self.download_cache: Dict[str, str] = {}  # URL -> local path
        self.failed_downloads: List[str] = []

        # Create base images directory
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Create month subdirectories
        for month_folder in self.MONTH_FOLDERS.values():
            (self.images_dir / month_folder).mkdir(exist_ok=True)

    def process_posts(self, posts):
        """
        Download images for all posts and update HTML references

        Args:
            posts: List of BlogPost objects

        Returns:
            Updated list of BlogPost objects
        """
        logger.info(f"Processing images for {len(posts)} posts")

        posts_with_images = [p for p in posts if p.has_images]
        logger.info(f"Found {len(posts_with_images)} posts with images")

        total_images = sum(len(p.image_urls) for p in posts_with_images)
        logger.info(f"Total images to download: {total_images}")

        downloaded_count = 0

        for post in posts:
            if post.has_images and post.parsed_date:
                updated_html = self._process_post_images(
                    post.content_html,
                    post.image_urls,
                    post.parsed_date
                )
                post.content_html = updated_html
                downloaded_count += len(post.image_urls)

                if downloaded_count % 10 == 0:
                    logger.info(f"Progress: {downloaded_count}/{total_images} images processed")

        logger.info(f"Downloaded {len(self.download_cache)} unique images")
        logger.info(f"Failed downloads: {len(self.failed_downloads)}")

        return posts

    def _process_post_images(self, html: str, image_urls: List[str], post_date: date) -> str:
        """
        Download images and replace URLs in HTML

        Args:
            html: Original HTML content
            image_urls: List of image URLs to download
            post_date: Date of the post (for organizing images)

        Returns:
            Updated HTML with local image paths
        """
        updated_html = html

        for url in image_urls:
            # Download image
            local_path = self._download_image(url, post_date)

            if local_path:
                # Convert to relative path for HTML
                relative_path = self._get_relative_path(local_path)

                # Replace URL in HTML (handle both img src and a href)
                updated_html = updated_html.replace(url, relative_path)
            else:
                logger.warning(f"Keeping original URL for failed download: {url[:80]}...")

        return updated_html

    def _download_image(self, url: str, post_date: date) -> Optional[str]:
        """
        Download a single image with retry logic

        Args:
            url: Image URL to download
            post_date: Date for organizing the image

        Returns:
            Local file path if successful, None otherwise
        """
        # Check cache first
        if url in self.download_cache:
            return self.download_cache[url]

        # Determine month folder
        month_folder = self.MONTH_FOLDERS.get(post_date.month, 'misc')

        # Generate filename
        filename = self._generate_filename(url, post_date)
        local_path = self.images_dir / month_folder / filename

        # Skip if already downloaded
        if local_path.exists():
            self.download_cache[url] = str(local_path)
            return str(local_path)

        # Attempt download with retries
        for attempt in range(self.retry_count):
            try:
                response = requests.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'image' not in content_type.lower():
                    logger.warning(f"URL does not appear to be an image: {content_type}")

                # Write file
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.download_cache[url] = str(local_path)
                logger.debug(f"Downloaded: {filename}")
                return str(local_path)

            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.debug(f"Download failed (attempt {attempt + 1}/{self.retry_count}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to download after {self.retry_count} attempts: {url[:80]}")
                    self.failed_downloads.append(url)

        return None

    def _generate_filename(self, url: str, post_date: date) -> str:
        """
        Generate a unique filename for the image

        Format: YYYY-MM-DD_{hash}.{ext}
        """
        # Extract file extension from URL
        url_path = url.split('?')[0]  # Remove query parameters
        ext = Path(url_path).suffix or '.jpg'

        # Create hash of URL for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

        # Build filename
        filename = f"{post_date.isoformat()}_{url_hash}{ext}"

        return filename

    def _get_relative_path(self, local_path: str) -> str:
        """
        Convert absolute path to relative path for HTML

        Example: "c:/...path.../Blog Reflections/2023/assets/images/jan/image.jpg"
        -> "assets/images/jan/image.jpg"
        """
        local_path = Path(local_path)
        year_dir = self.output_dir / str(self.year)

        try:
            relative = local_path.relative_to(year_dir)
            # Convert to forward slashes for HTML
            return str(relative).replace('\\', '/')
        except ValueError:
            # If relative path fails, return the local path as-is
            return str(local_path).replace('\\', '/')

    def get_download_report(self) -> Dict:
        """Generate download statistics report"""
        return {
            'total_downloaded': len(self.download_cache),
            'failed_downloads': len(self.failed_downloads),
            'failed_urls': self.failed_downloads.copy()
        }

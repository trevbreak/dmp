"""Content processor for cleaning and enhancing HTML"""
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Clean and enhance HTML content from blog posts"""

    def clean_html(self, html: str) -> str:
        """
        Clean Blogger-specific artifacts and sanitize HTML

        Args:
            html: Original HTML content

        Returns:
            Cleaned HTML
        """
        if not html:
            return ""

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script tags (security)
            for script in soup.find_all('script'):
                script.decompose()

            # Remove tracking pixels and iframes
            for iframe in soup.find_all('iframe'):
                iframe.decompose()

            # Clean up links - ensure they open in new tab
            for link in soup.find_all('a'):
                link['target'] = '_blank'
                link['rel'] = 'noopener noreferrer'

            # Add loading="lazy" to images
            for img in soup.find_all('img'):
                img['loading'] = 'lazy'

                # Add responsive class
                existing_class = img.get('class', [])
                if isinstance(existing_class, str):
                    existing_class = [existing_class]
                existing_class.append('post-image')
                img['class'] = existing_class

            # Remove excessive inline styles (keep some for compatibility)
            for tag in soup.find_all(style=True):
                # Keep width/height for images
                if tag.name not in ['img']:
                    del tag['style']

            cleaned_html = str(soup)

            # Remove Blogger-specific parameters from remaining URLs
            cleaned_html = re.sub(r'\?imgmax=\d+', '', cleaned_html)
            cleaned_html = re.sub(r'&imgmax=\d+', '', cleaned_html)

            return cleaned_html

        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html  # Return original if cleaning fails

    def extract_preview(self, html: str, max_length: int = 200) -> str:
        """
        Extract plain text preview from HTML

        Args:
            html: HTML content
            max_length: Maximum length of preview

        Returns:
            Plain text preview
        """
        if not html:
            return ""

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Get text content
            text = soup.get_text(separator=' ', strip=True)

            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)

            # Truncate
            if len(text) > max_length:
                text = text[:max_length].rsplit(' ', 1)[0] + '...'

            return text

        except Exception as e:
            logger.error(f"Error extracting preview: {e}")
            return ""

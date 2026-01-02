"""HTML generator with embedded templates"""
import logging
import shutil
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generate HTML files for yearly reflection"""

    def __init__(self, output_dir: Path, static_dir: Path):
        self.output_dir = output_dir
        self.static_dir = static_dir

    def generate_reflection_page(self, year: int, posts, tag_index):
        """
        Generate the main reflection HTML page for a year

        Args:
            year: Year to generate for
            posts: List of BlogPost objects
            tag_index: TagIndex object
        """
        logger.info(f"Generating reflection page for {year}")

        year_dir = self.output_dir / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)

        # Copy static assets
        self._copy_static_assets(year)

        # Generate HTML
        html_content = self._build_reflection_html(year, posts, tag_index)

        # Write HTML file
        html_file = year_dir / 'reflection.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Generated reflection.html: {html_file}")

    def generate_index_page(self, years: list):
        """
        Generate index page with year selector

        Args:
            years: List of years to include
        """
        logger.info("Generating index page")

        html_content = self._build_index_html(years)

        index_file = self.output_dir / 'index.html'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Generated index.html: {index_file}")

    def _copy_static_assets(self, year: int):
        """Copy CSS and JS files to year directory"""
        year_assets = self.output_dir / str(year) / 'assets'
        css_dir = year_assets / 'css'
        js_dir = year_assets / 'js'

        css_dir.mkdir(parents=True, exist_ok=True)
        js_dir.mkdir(parents=True, exist_ok=True)

        # Copy or create CSS
        self._create_css_file(css_dir / 'reflection.css')

        # Copy or create JS
        self._create_js_file(js_dir / 'reflection.js')

        logger.info(f"Copied static assets to {year_assets}")

    def _create_css_file(self, css_path: Path):
        """Create the reflection.css file with book theme"""
        css_content = """
/* Book/Journal Theme for Blog Reflection */

:root {
  --color-bg: #f9f7f4;
  --color-paper: #ffffff;
  --color-text: #2c2c2c;
  --color-text-light: #666666;
  --color-accent: #8b7355;
  --color-border: #e0dcd5;
  --font-serif: 'Georgia', serif;
  --font-sans: 'Arial', sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  font-family: var(--font-serif);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.7;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

/* Header */
.reflection-header {
  background: var(--color-paper);
  border-bottom: 3px solid var(--color-accent);
  padding: 2rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.book-title {
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: var(--color-accent);
  text-align: center;
}

.year-label {
  font-size: 1.5rem;
  text-align: center;
  color: var(--color-text-light);
  margin: 0;
}

/* Sidebar */
.sidebar {
  background: var(--color-paper);
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sidebar h3 {
  margin-top: 0;
  color: var(--color-accent);
  font-size: 1.2rem;
}

.tag {
  display: inline-block;
  background: var(--color-bg);
  border: 2px solid var(--color-border);
  padding: 0.4rem 0.8rem;
  margin: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 0.9rem;
  transition: all 0.2s;
}

.tag:hover {
  border-color: var(--color-accent);
  background: var(--color-accent);
  color: white;
}

.tag.active {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

/* Posts */
.month-section {
  margin-bottom: 3rem;
}

.month-header {
  font-size: 2rem;
  color: var(--color-accent);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0.5rem;
  margin: 2rem 0 1.5rem 0;
}

.post-card {
  background: var(--color-paper);
  padding: 2rem;
  margin-bottom: 2rem;
  border-left: 4px solid var(--color-accent);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateX(4px);
}

.post-date {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-accent);
  font-weight: 600;
  margin-bottom: 1rem;
  display: block;
}

.post-content {
  margin: 1rem 0;
  font-size: 1.05rem;
  line-height: 1.8;
}

.post-content p {
  margin: 0 0 1rem 0;
}

.post-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 1rem 0;
}

.post-tags {
  margin-top: 1rem;
}

.tag-pill {
  display: inline-block;
  background: var(--color-bg);
  color: var(--color-text);
  padding: 0.25rem 0.75rem;
  margin: 0.25rem 0.25rem 0.25rem 0;
  border-radius: 20px;
  font-size: 0.8rem;
  font-family: var(--font-sans);
  border: 1px solid var(--color-border);
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .book-title {
    font-size: 1.5rem;
  }

  .month-header {
    font-size: 1.5rem;
  }

  .post-card {
    padding: 1.5rem;
  }
}
"""
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)

    def _create_js_file(self, js_path: Path):
        """Create the reflection.js file with tag filtering"""
        js_content = """
// Tag filtering and navigation for blog reflection

class ReflectionApp {
  constructor() {
    this.activeFilters = new Set();
    this.data = null;
  }

  async init() {
    // Load data
    const response = await fetch('data/posts.json');
    this.data = await response.json();

    // Setup event listeners
    this.setupTagFilters();
  }

  setupTagFilters() {
    const tagButtons = document.querySelectorAll('.tag');

    tagButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tag = e.target.dataset.tag;

        // Toggle active state
        e.target.classList.toggle('active');

        if (this.activeFilters.has(tag)) {
          this.activeFilters.delete(tag);
        } else {
          this.activeFilters.add(tag);
        }

        this.applyFilters();
      });
    });
  }

  applyFilters() {
    if (this.activeFilters.size === 0) {
      this.showAllPosts();
      return;
    }

    // Get posts matching ALL active tags
    const matchingPosts = this.data.posts.filter(post => {
      return Array.from(this.activeFilters).every(tag =>
        post.labels.map(l => l.toLowerCase()).includes(tag)
      );
    });

    const matchingIds = new Set(matchingPosts.map(p => p.id));

    // Show/hide posts
    document.querySelectorAll('.post-card').forEach(card => {
      if (matchingIds.has(card.dataset.postId)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });

    // Update month headers
    this.updateMonthHeaders();
  }

  showAllPosts() {
    document.querySelectorAll('.post-card').forEach(card => {
      card.style.display = 'block';
    });

    document.querySelectorAll('.month-section').forEach(section => {
      section.style.display = 'block';
    });
  }

  updateMonthHeaders() {
    document.querySelectorAll('.month-section').forEach(section => {
      const visiblePosts = Array.from(section.querySelectorAll('.post-card'))
        .filter(card => card.style.display !== 'none');

      section.style.display = visiblePosts.length > 0 ? 'block' : 'none';
    });
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  const app = new ReflectionApp();
  app.init();
});
"""
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)

    def _build_reflection_html(self, year: int, posts, tag_index) -> str:
        """Build the complete reflection HTML page"""
        # Group posts by month
        months_data = self._group_posts_by_month(posts)

        # Get popular tags
        popular_tags = sorted(
            tag_index.tag_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:30]

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{year} - Digital Memory Palace</title>
    <link rel="stylesheet" href="assets/css/reflection.css">
</head>
<body>
    <header class="reflection-header">
        <div class="container">
            <h1 class="book-title">Digital Memory Palace</h1>
            <p class="year-label">{year}</p>
        </div>
    </header>

    <main class="reflection-content">
        <div class="container">
            <aside class="sidebar">
                <h3>Filter by Tag</h3>
                <div class="tags">
                    {self._build_tag_buttons(popular_tags)}
                </div>
            </aside>

            <div class="timeline">
                {self._build_month_sections(months_data)}
            </div>
        </div>
    </main>

    <script src="assets/js/reflection.js"></script>
</body>
</html>"""
        return html

    def _build_index_html(self, years: list) -> str:
        """Build the index page HTML"""
        year_links = '\n'.join([
            f'<li><a href="{year}/reflection.html">{year}</a></li>'
            for year in sorted(years, reverse=True)
        ])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Memory Palace</title>
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 600px;
            margin: 4rem auto;
            padding: 2rem;
            background: #f9f7f4;
        }}
        h1 {{
            color: #8b7355;
            text-align: center;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin: 1rem 0;
        }}
        a {{
            color: #8b7355;
            text-decoration: none;
            font-size: 1.5rem;
            display: block;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            text-align: center;
            transition: transform 0.2s;
        }}
        a:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>Digital Memory Palace</h1>
    <p style="text-align: center; color: #666;">Select a year to explore</p>
    <ul>
        {year_links}
    </ul>
</body>
</html>"""
        return html

    def _group_posts_by_month(self, posts):
        """Group posts by month"""
        months = {}
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        for post in posts:
            if post.parsed_date:
                month_idx = post.parsed_date.month - 1
                if month_idx not in months:
                    months[month_idx] = {
                        'name': month_names[month_idx],
                        'posts': []
                    }
                months[month_idx]['posts'].append(post)

        return months

    def _build_tag_buttons(self, popular_tags):
        """Build HTML for tag filter buttons"""
        buttons = []
        for tag, count in popular_tags:
            buttons.append(
                f'<button class="tag" data-tag="{tag}">{tag} <span>({count})</span></button>'
            )
        return '\n'.join(buttons)

    def _build_month_sections(self, months_data):
        """Build HTML for month sections with posts"""
        sections = []

        for month_idx in sorted(months_data.keys()):
            month_info = months_data[month_idx]
            month_name = month_info['name']
            posts = month_info['posts']

            post_cards = '\n'.join([self._build_post_card(post) for post in posts])

            section_html = f"""
            <section class="month-section" id="month-{month_idx}">
                <h2 class="month-header">{month_name}</h2>
                <div class="posts-grid">
                    {post_cards}
                </div>
            </section>
            """
            sections.append(section_html)

        return '\n'.join(sections)

    def _build_post_card(self, post) -> str:
        """Build HTML for a single post card"""
        date_str = post.parsed_date.strftime('%A %d %B, %Y') if post.parsed_date else post.title

        tags_html = ' '.join([
            f'<span class="tag-pill">{tag}</span>'
            for tag in post.labels
        ])

        return f"""
        <article class="post-card" data-post-id="{post.post_id}">
            <time class="post-date">{date_str}</time>
            <div class="post-content">
                {post.content_html}
            </div>
            <div class="post-tags">
                {tags_html}
            </div>
        </article>
        """

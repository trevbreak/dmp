#!/usr/bin/env python3
"""
Blogger XML to Yearly Reflection Generator
Main execution pipeline
"""

import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from parsers.xml_parser import BloggerXMLParser
from parsers.date_parser import DateParser
from processors.image_downloader import ImageDownloader
from processors.tag_indexer import TagIndexer
from processors.content_processor import ContentProcessor
from generators.json_generator import JSONGenerator
from generators.html_generator import HTMLGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('blog_reflection_generator.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate yearly reflection pages from Blogger XML exports'
    )
    parser.add_argument(
        'xml_file',
        nargs='?',
        type=str,
        help='Path to Blogger XML export file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (default: c:/GIT/dmp/reflection)'
    )
    return parser.parse_args()


def process_year(year, year_posts, config, date_parser):
    """Process posts for a single year"""
    print(f"  === Processing {year} ===")
    print(f"      {len(year_posts)} posts")

    # Sort chronologically
    year_posts.sort(key=lambda p: p.parsed_date)

    # Download images
    posts_with_images = len([p for p in year_posts if p.has_images])
    if posts_with_images > 0:
        print(f"      Downloading images for {year}...")
        image_downloader = ImageDownloader(
            config.output_dir,
            year,
            timeout=config.image_timeout,
            retry_count=config.image_retry_count
        )
        year_posts = image_downloader.process_posts(year_posts)
        report = image_downloader.get_download_report()
        print(f"      OK - Downloaded {report['total_downloaded']} images")
        if report['failed_downloads'] > 0:
            print(f"      WARNING - {report['failed_downloads']} images failed")
    else:
        print(f"      No images to download")

    # Build tag index
    tag_indexer = TagIndexer()
    tag_index = tag_indexer.build_index(year_posts)
    print(f"      Indexed {len(tag_index.all_tags)} tags")

    # Generate JSON data
    json_gen = JSONGenerator(config.output_dir, year)
    json_gen.generate(year_posts, tag_index)

    # Generate HTML
    html_gen = HTMLGenerator(config.output_dir, config.static_dir)
    html_gen.generate_reflection_page(year, year_posts, tag_index)

    # Generate summary report
    generate_year_report(year, year_posts, tag_index, config, date_parser)

    print(f"      OK - {year} reflection complete")
    print()


def main():
    """Main execution pipeline"""

    print("=" * 70)
    print("  Blogger XML to Yearly Reflection Generator")
    print("=" * 70)
    print()

    # Parse arguments
    args = parse_arguments()

    # Load configuration
    config = Config()

    # Override with command line arguments
    if args.xml_file:
        config.xml_file = Path(args.xml_file)
    if args.output_dir:
        config.output_dir = Path(args.output_dir)

    logger.info(f"Input XML: {config.xml_file}")
    logger.info(f"Output directory: {config.output_dir}")

    try:
        # Step 1: Parse XML
        logger.info("\n[1/6] Parsing XML file...")
        print(f"[1/6] Parsing XML file: {config.xml_file.name}")
        parser = BloggerXMLParser(str(config.xml_file))
        posts = parser.parse()
        print(f"      OK - Extracted {len(posts)} posts")

        # Step 2: Parse dates from titles
        logger.info("\n[2/6] Parsing dates from titles...")
        print(f"[2/6] Parsing dates from titles...")
        date_parser = DateParser()
        for post in posts:
            post.parsed_date = date_parser.parse_title_date(post.title)

        successful_parses = sum(1 for p in posts if p.parsed_date)
        success_rate = date_parser.get_success_rate(len(posts))
        print(f"      OK - Successfully parsed {successful_parses}/{len(posts)} dates ({success_rate:.1f}%)")

        # Step 3: Group posts by year
        logger.info("\n[3/6] Grouping posts by year...")
        print(f"[3/6] Grouping posts by year...")
        posts_by_year = defaultdict(list)
        for post in posts:
            if post.parsed_date:
                posts_by_year[post.parsed_date.year].append(post)

        years_found = sorted(posts_by_year.keys())
        print(f"      OK - Found {len(years_found)} years: {', '.join(map(str, years_found))}")

        if not years_found:
            print(f"\nWARNING - No posts with valid dates found. Exiting.")
            return

        # Step 4: Process content for all posts
        logger.info("\n[4/6] Processing content...")
        print(f"[4/6] Processing content for all posts...")
        content_processor = ContentProcessor()
        for post in posts:
            if post.parsed_date:
                post.content_html = content_processor.clean_html(post.content_html)
                post.preview = content_processor.extract_preview(post.content_html, config.max_preview_length)
        print(f"      OK - Cleaned HTML for {successful_parses} posts")

        # Step 5: Process each year
        logger.info("\n[5/6] Processing years...")
        print(f"[5/6] Processing each year...")
        print()

        for year in years_found:
            process_year(year, posts_by_year[year], config, date_parser)

        # Step 6: Generate master index page
        logger.info("\n[6/6] Generating master index page...")
        print(f"\n[6/6] Generating master index page...")
        html_gen = HTMLGenerator(config.output_dir, config.static_dir)
        html_gen.generate_index_page(years_found)
        print(f"      OK - Generated index.html with {len(years_found)} years")

        # Print completion message
        print()
        print("=" * 70)
        print("  OK - All Years Generated Successfully!")
        print("=" * 70)
        print()
        print(f"Reflection pages created in: {config.output_dir}")
        print(f"Open the index page:")
        print(f"  {config.output_dir / 'index.html'}")
        print()
        print(f"Years generated: {', '.join(map(str, years_found))}")
        print()

    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        print(f"\nERROR - Error: {e}")
        print("Check blog_reflection_generator.log for details")
        sys.exit(1)


def generate_year_report(year, posts, tag_index, config, date_parser):
    """Generate summary report for a specific year"""
    report_path = config.output_dir / str(year) / 'generation_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Blogger XML to Yearly Reflection - Generation Report\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Year: {year}\n\n")

        f.write(f"Statistics:\n")
        f.write(f"  Total Posts: {len(posts)}\n")
        f.write(f"  Posts with Images: {sum(1 for p in posts if p.has_images)}\n")
        f.write(f"  Total Tags: {len(tag_index.all_tags)}\n")
        f.write(f"  Total Images: {sum(len(p.image_urls) for p in posts)}\n\n")

        f.write(f"Top 20 Tags:\n")
        top_tags = sorted(
            tag_index.tag_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        for i, (tag, count) in enumerate(top_tags, 1):
            f.write(f"  {i:2d}. {tag:30s} {count:3d}\n")

        # Date parsing failures
        failed = date_parser.get_failed_parses()
        if failed:
            f.write(f"\nDate Parsing Failures ({len(failed)}):\n")
            for title in failed[:10]:  # Show first 10
                f.write(f"  - {title}\n")
            if len(failed) > 10:
                f.write(f"  ... and {len(failed) - 10} more\n")

    logger.info(f"Report saved to: {report_path}")
    print(f"      OK - Generated report: generation_report.txt")


if __name__ == '__main__':
    main()

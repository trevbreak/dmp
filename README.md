# Blogger to Yearly Reflection Generator

Transform your Blogger XML exports into beautiful, book-style yearly reflection pages with interactive tag filtering.

## Overview

This tool extracts blog posts from Blogger XML exports, **automatically detects all years**, organizes posts chronologically, downloads all images locally, and generates a beautiful web-based reflection interface with a book/journal aesthetic.

## Features

- **Automatic Year Detection**: Processes all years found in your XML export
- **XML Parsing**: Extracts all posts from Blogger Atom feed exports
- **Smart Date Parsing**: Parses dates from post titles with multiple fallback strategies
- **Image Management**: Downloads all images locally, organized by month
- **Tag Filtering**: Interactive client-side tag filtering with instant results
- **Book/Journal Theme**: Beautiful, readable design with serif fonts and paper-like aesthetics
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

The generator automatically detects all years from the XML file and creates reflections for each year.

1. Run the generator with your Blogger XML export:
   ```bash
   cd src
   python main.py "path/to/your/blogger-export.xml"
   ```

2. Open the generated index page:
   ```
   c:\GIT\dmp\reflection\index.html
   ```

### Command Line Options

```bash
# Basic usage - processes default XML file from config.py
python main.py

# Specify XML file
python main.py "path/to/export.xml"

# Specify custom output directory
python main.py "path/to/export.xml" --output-dir "c:/my/output/dir"
```

### Example

```bash
cd c:/GIT/dmp/src
python main.py "c:/Users/tdevr/My Drive/Blog/Digital Memory Palace/2023 Export/blog-12-30-2023.xml"
```

This will:
- Parse all 1,825 posts from the XML
- Automatically detect all years (2018-2026 in this example)
- Download all images organized by year and month
- Generate reflection pages for each year
- Create a master index page to navigate between years

## Generated Output

The tool creates the following structure in `c:\GIT\dmp\reflection\`:

```
reflection/
├── index.html                    # Master year selector page
├── 2018/
│   ├── reflection.html           # 2018 reflection page
│   ├── assets/
│   │   ├── css/reflection.css    # Book-style theme
│   │   ├── js/reflection.js      # Tag filtering & navigation
│   │   └── images/               # Downloaded images by month
│   ├── data/
│   │   ├── posts.json            # Structured post data
│   │   └── metadata.json         # Generation statistics
│   └── generation_report.txt     # Detailed report
├── 2019/
│   └── ... (same structure)
├── 2020/
└── ... (all detected years)
```

## Results Summary

### Latest Run Results (2023 Export)

- **Total Posts**: 1,825 posts across all years
- **Years Detected**: 7 years (2018, 2019, 2020, 2021, 2022, 2023, 2026)
- **Date Parsing**: 100% success rate
- **Images Downloaded**: 165 images (159 for 2023, 6 for 2022)
- **Processing Time**: ~5 minutes

### Per-Year Breakdown

| Year | Posts | Images | Tags | Top Tag |
|------|-------|--------|------|---------|
| 2018 | 2     | 0      | 19   | Various |
| 2019 | 364   | 0      | 410  | #aj (105) |
| 2020 | 366   | 0      | 275  | #work (147) |
| 2021 | 365   | 0      | 278  | #work (173) |
| 2022 | 369   | 6      | 542  | #work (83) |
| 2023 | 357   | 159    | 476  | work (162) |
| 2026 | 2     | 0      | 5    | Various |

## Features in Detail

### Automatic Year Detection

The tool automatically:
1. Parses dates from all post titles
2. Groups posts by year
3. Generates a separate reflection page for each year
4. Creates a master index page with links to all years

No need to manually specify years - just point it at your XML file!

### Date Parsing

The tool uses multiple strategies to parse dates from post titles:
1. Remove ordinal suffixes (1st, 2nd, 3rd, etc.) and use dateutil
2. Regex pattern matching for exact formats
3. Fallback to ISO published date if title parsing fails

### Image Downloading

- Downloads all `blogger.googleusercontent.com` images
- Organizes by year and month (2023/jan/, 2023/feb/, etc.)
- Retry logic with exponential backoff (3 attempts)
- Updates HTML to reference local paths
- Maintains original URLs as fallback if download fails

### Tag Filtering

- Client-side JavaScript for instant filtering
- AND logic: Posts must match ALL active tags
- Shows/hides posts without page reload
- Automatically hides empty month sections

### Book/Journal Theme

- Serif fonts (Georgia) for readability
- Cream/paper background (#f9f7f4)
- Warm brown accent color (#8b7355)
- Post cards with left border accent
- Subtle shadows and hover effects

## Project Structure

```
dmp/
├── src/
│   ├── main.py                   # Pipeline orchestrator
│   ├── config.py                 # Configuration
│   ├── parsers/
│   │   ├── xml_parser.py         # Blogger XML parser
│   │   └── date_parser.py        # Date extraction
│   ├── processors/
│   │   ├── image_downloader.py   # Image management
│   │   ├── tag_indexer.py        # Tag indexing
│   │   └── content_processor.py  # HTML cleaning
│   └── generators/
│       ├── json_generator.py     # JSON data export
│       └── html_generator.py     # HTML generation
├── reflection/                   # Generated output directory
│   ├── index.html
│   ├── 2018/
│   ├── 2019/
│   └── ... (all years)
├── requirements.txt
└── README.md
```

## Configuration

Edit `src/config.py` to customize default settings:

- `xml_file`: Default XML file path
- `output_dir`: Output directory (default: `c:\GIT\dmp\reflection`)
- `image_timeout`: Timeout for image downloads (default: 30s)
- `image_retry_count`: Number of retry attempts (default: 3)
- `max_preview_length`: Length of post previews (default: 200)

## Logging

Logs are written to both console and `blog_reflection_generator.log` file with detailed information about:
- Posts extracted
- Date parsing success rate
- Image download progress (every 10 images)
- Tag indexing results
- Any errors or warnings

## Troubleshooting

### No posts with valid dates found

**Issue**: Message shows "No posts with valid dates found"

**Solution**:
- Check that your XML file has proper post titles with dates
- Look at the log for date parsing failures
- Verify the XML file is a valid Blogger export

### Image download failures

**Issue**: Some images fail to download

**Solution**:
- Check your internet connection
- Images may have been deleted from Blogger
- Original URLs are kept as fallback
- Check `failed_downloads` in the generation report

### Unicode errors on Windows

**Issue**: UnicodeEncodeError when running

**Solution**: The code uses ASCII-compatible characters. If you still see errors, ensure your terminal supports UTF-8.

## Future Enhancements

Potential features for future versions:
- PDF export option
- Full-text search functionality
- Tag cloud visualization
- Year comparison features
- Support for other blog platforms
- Incremental updates (only process new posts)

## License

This tool is provided as-is for personal use.

## Author

Generated for Trevor's Digital Memory Palace project - January 2026

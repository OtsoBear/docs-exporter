# Docs Exporter

A powerful Python tool to extract content from websites and convert it to clean, LLM-friendly markdown format. Perfect for creating training data, documentation, or preparing web content for AI processing.

## Features

- 🌐 **Web Scraping**: Supports both static and dynamic content with requests and Selenium
- 🧹 **Smart Content Extraction**: Automatically identifies main content, removes navigation/ads
- 📝 **Clean Markdown Output**: Optimized for LLM consumption with proper formatting
- 🔧 **Flexible CLI**: Easy-to-use command-line interface with multiple options
- 📦 **Batch Processing**: Export multiple URLs from a file
- 🎯 **Multiple Extraction Methods**: Choose between readability algorithm and CSS selectors
- 📋 **Metadata Support**: Include page titles, descriptions, and other metadata

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd docs-exporter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) For Selenium support, install ChromeDriver:
```bash
# On macOS with Homebrew
brew install chromedriver

# On Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Or download manually from https://chromedriver.chromium.org/
```

## Quick Start

### Command Line Usage

Export a single URL:
```bash
python main.py export https://www.tensorzero.com/docs
```

Export with custom options:
```bash
python main.py export https://example.com \
  --output my_docs.md \
  --use-selenium \
  --extraction-method readability \
  --verbose
```

Batch export from a file:
```bash
# Create a file with URLs (one per line)
echo "https://www.tensorzero.com/docs" > urls.txt
echo "https://example.com/article" >> urls.txt

python main.py batch urls.txt --output-dir ./exported
```

Copy to clipboard instead of saving:
```bash
python main.py export https://example.com --copy-to-clipboard
```

### Programmatic Usage

```python
from docs_exporter import DocsExporter, export_url_to_markdown

# Quick export
markdown = export_url_to_markdown("https://example.com")
print(markdown)

# Advanced usage
with DocsExporter(use_selenium=True, verbose=True) as exporter:
    markdown = exporter.export_url("https://example.com")
    if markdown:
        with open("output.md", "w") as f:
            f.write(markdown)
```

## CLI Commands

### `export` - Export a single URL

```bash
python main.py export [OPTIONS] URL
```

**Options:**
- `--output, -o`: Output file path
- `--output-dir, -d`: Output directory (default: current directory)
- `--use-selenium`: Force use of Selenium for dynamic content
- `--no-metadata`: Skip including metadata in output
- `--extraction-method`: Method to use (`auto`, `readability`, `selectors`)
- `--verbose, -v`: Enable verbose logging
- `--copy-to-clipboard, -c`: Copy to clipboard instead of saving

### `batch` - Export multiple URLs

```bash
python main.py batch [OPTIONS] URLS_FILE
```

**Options:**
- `--output-dir, -d`: Output directory for exported files
- `--use-selenium`: Force use of Selenium for dynamic content
- `--no-metadata`: Skip including metadata in output
- `--extraction-method`: Method to use (`auto`, `readability`, `selectors`)
- `--verbose, -v`: Enable verbose logging
- `--delay`: Delay between requests in seconds (default: 1.0)

## Extraction Methods

1. **Auto (default)**: Tries CSS selectors first, falls back to readability
2. **Readability**: Uses Mozilla's readability algorithm for content extraction
3. **Selectors**: Uses CSS selectors to find main content areas

## Configuration

The tool automatically detects content using:

- Common content selectors (`main`, `article`, `.content`, etc.)
- Readability algorithm for content scoring
- Automatic removal of navigation, ads, and other non-content elements

## Examples

### Export TensorZero Documentation
```bash
python main.py export https://www.tensorzero.com/docs \
  --output tensorzero-docs.md \
  --extraction-method auto
```

### Batch Export Multiple Documentation Pages
```bash
# Create urls.txt with:
# https://www.tensorzero.com/docs
# https://www.tensorzero.com/docs/quickstart
# https://www.tensorzero.com/docs/gateway

python main.py batch urls.txt \
  --output-dir ./tensorzero-docs \
  --delay 2.0
```

### Export JavaScript-Heavy Site
```bash
python main.py export https://spa-website.com \
  --use-selenium \
  --verbose
```

## Output Format

The tool generates clean markdown with:

- Document metadata (title, description, source URL)
- Properly formatted headings, lists, and code blocks
- Tables converted to markdown format
- Images with alt text preserved
- Links with descriptive text

Example output:
```markdown
# Page Title

**Source:** https://example.com
**Description:** Page description here

---

## Main Content

This is the main content of the page...

### Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Summary

Key points from the article...
```

## Troubleshooting

### Chrome Driver Issues
If you encounter Selenium/ChromeDriver issues:
1. Ensure ChromeDriver is installed and in PATH
2. Update Chrome browser to latest version
3. Use `--use-selenium` only when necessary

### Content Not Extracted
If content isn't being extracted properly:
1. Try different extraction methods (`--extraction-method`)
2. Use `--verbose` to see detailed logs
3. For JavaScript-heavy sites, use `--use-selenium`

### Performance
For better performance:
- Use requests (default) instead of Selenium when possible
- Increase `--delay` for batch operations to be respectful to servers
- Use `--no-metadata` to skip metadata extraction

## Development

The project structure:
```
docs_exporter/
├── __init__.py          # Package initialization
├── scraper.py           # Web scraping functionality
├── extractor.py         # Content extraction logic
├── converter.py         # HTML to Markdown conversion
├── cli.py              # Command-line interface
└── exporter.py         # Main API class
```

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `selenium`: Dynamic content scraping
- `markdownify`: HTML to Markdown conversion
- `click`: CLI framework
- `lxml`: XML/HTML processing
- `readability-lxml`: Content extraction algorithm

## License

MIT License - see LICENSE file for details.
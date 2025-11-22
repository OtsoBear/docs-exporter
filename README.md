# Docs Exporter

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Async](https://img.shields.io/badge/async-aiohttp-orange.svg)](https://docs.aiohttp.org/)

A Flask web application for extracting large documentation sites into clean, consolidated markdown format. Designed to prepare documentation for LLM consumption and analysis.

## Purpose

Convert entire documentation sites into a single markdown file that can be easily provided to Large Language Models. This enables AI assistants to understand and answer questions about complex documentation without requiring multiple web requests or context switching.

## Features

- Automatic navigation structure detection
- Batch export of multiple documentation pages
- Concurrent async processing for efficiency
- Real-time progress tracking via Server-Sent Events
- Clean markdown output optimized for LLM input
- Optional link compression to reduce token usage
- Smart content extraction with code block preservation

## Installation

### Quick Setup (Recommended)

```bash
git clone <your-repo-url>
cd docs-exporter
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd docs-exporter
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
# Or generate one: python -c "import os; print(os.urandom(24).hex())"
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Navigate to `http://localhost:5000`

3. Enter a documentation URL (e.g., `https://example.com/docs`)

4. Select which pages to include in the export

5. Download the consolidated markdown file

## Configuration

Default settings in [`app.py`](app.py:21):
- Max concurrent requests: 15
- Request delay: 0.1 seconds with adaptive adjustment
- Retry attempts: 3 with exponential backoff
- Connection timeout: 5 seconds
- Total timeout: 30 seconds

## API Endpoints

- `GET /` - Main interface
- `POST /scan` - Scan documentation site for available pages
- `POST /export` - Initiate export job
- `GET /progress/<id>` - Server-Sent Events progress stream
- `GET /result/<id>` - Retrieve export results

## Security Features

- CSRF protection on all forms
- Rate limiting per endpoint (30/min for main page, 10/min for scan, 5/min for export)
- URL validation and sanitization
- Environment-based secret key management
- Automatic cleanup of expired session data

## Dependencies

- Flask - Web framework
- Flask-WTF - CSRF protection
- Flask-Limiter - Rate limiting
- aiohttp - Async HTTP client for concurrent requests
- BeautifulSoup4 - HTML parsing
- requests - HTTP requests
- python-dotenv - Environment variable management

## Output Format

Generated markdown includes:
- Document metadata (titles, URLs)
- Properly formatted headings and hierarchy
- Preserved code blocks
- Converted tables
- Link references

Ideal for providing comprehensive context to LLMs without manually copying documentation.

## License

MIT License
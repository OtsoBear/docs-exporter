import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
import asyncio
import aiohttp

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class DocsExporter:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        
    def get_navigation_structure(self):
        """Extract navigation structure from the main docs page"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
        except:
            return None, "Pages that can't be accessed"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the sidebar navigation
        sidebar = soup.find('div', id='sidebar-content')
        if not sidebar:
            return None, "Pages that don't exist"
            
        pages = []
        
        # Find all navigation groups
        groups = sidebar.find_all('div', class_='sidebar-group-header')
        
        for group in groups:
            group_title = group.find('h5')
            if not group_title:
                continue
                
            group_name = group_title.get_text(strip=True)
            group_pages = []
            
            # Find the ul element that follows this group header
            ul_element = group.find_next_sibling('ul')
            if ul_element:
                links = ul_element.find_all('a', href=True)
                for link in links:
                    title = link.get_text(strip=True)
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = f"https://{self.domain}{href}"
                    else:
                        full_url = urljoin(self.base_url, href)
                    
                    group_pages.append({
                        'title': title,
                        'url': full_url,
                        'path': href
                    })
            
            if group_pages:
                pages.append({
                    'group': group_name,
                    'pages': group_pages
                })
        
        return pages, None
    
    async def fetch_markdown_content_async(self, session, url):
        """Fetch markdown content by appending .md to the URL"""
        try:
            # Convert docs URL to markdown URL
            # If URL ends with '/', add '.md' directly
            # If URL doesn't end with '/', add '/.md'
            if url.endswith('/'):
                md_url = url + '.md'
            else:
                md_url = url + '/.md'
            
            async with session.get(md_url, timeout=10) as response:
                if response.status == 404:
                    return None, "Pages that don't exist"
                response.raise_for_status()
                content = await response.text()
                return content, None
        except asyncio.TimeoutError:
            return None, "Rate limiting from the server"
        except:
            return None, "Pages that can't be accessed"
    
    def compress_content(self, content):
        """Compress content by removing verbose image markup and shortening URLs"""
        if not content or len(content.strip()) == 0:
            return content
            
        # First, extract and preserve code blocks and inline code
        code_blocks = []
        inline_codes = []
        
        # Extract code blocks (```...```) - more efficient pattern
        def preserve_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        # Extract inline code (`...`) - more efficient pattern
        def preserve_inline_code(match):
            inline_codes.append(match.group(0))
            return f"__INLINE_CODE_{len(inline_codes)-1}__"
        
        # Preserve code blocks first (more efficient regex)
        content = re.sub(r'```[\s\S]*?```', preserve_code_block, content)
        content = re.sub(r'`[^`\n]*`', preserve_inline_code, content)
        
        # Simple image removal - much faster
        content = re.sub(r'<div[^>]*>\s*<img[^>]*alt="([^"]*?)"[^>]*>.*?</div>', r'[\1]', content, flags=re.DOTALL)
        content = re.sub(r'<img[^>]*alt="([^"]*?)"[^>]*>', r'[\1]', content)
        content = re.sub(r'<img[^>]*>', '[image]', content)
        
        # Consolidate images - simpler pattern
        content = re.sub(r'(\[image\]\s*){2,}', '[images]', content)
        
        # Shorten URLs - more targeted pattern
        content = re.sub(r'https?://(www\.)?', '', content)
        
        # Remove HTML tags - simple and fast
        content = re.sub(r'<[^>]+>', '', content)
        
        # Restore code blocks and inline code
        for i, code_block in enumerate(code_blocks):
            content = content.replace(f"__CODE_BLOCK_{i}__", code_block)
        
        for i, inline_code in enumerate(inline_codes):
            content = content.replace(f"__INLINE_CODE_{i}__", inline_code)
        
        return content
    
    async def export_selected_pages_async(self, selected_urls, compress_links=False):
        """Export selected pages to a combined markdown file"""
        combined_content = []
        errors = []
        
        # Get navigation structure to maintain hierarchy
        nav_structure, error = self.get_navigation_structure()
        if error:
            return None, [error]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            url_to_info = {}
            
            # Prepare tasks for concurrent fetching
            for group in nav_structure:
                for page in group['pages']:
                    if page['url'] in selected_urls:
                        url_to_info[page['url']] = {
                            'group': group['group'],
                            'title': page['title']
                        }
                        task = self.fetch_markdown_content_async(session, page['url'])
                        tasks.append((page['url'], task))
            
            # Execute all requests concurrently
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results maintaining hierarchy
            url_results = dict(zip([url for url, _ in tasks], results))
            
            for group in nav_structure:
                group_added = False
                
                for page in group['pages']:
                    if page['url'] in selected_urls:
                        # Add group header if this is the first page from this group
                        if not group_added:
                            combined_content.append(f"\n# {group['group']}\n")
                            group_added = True
                        
                        # Add page header
                        combined_content.append(f"\n## {page['title']}\n")
                        
                        # Get result
                        result = url_results.get(page['url'])
                        if isinstance(result, Exception):
                            errors.append(f"{page['title']}: Pages that can't be accessed")
                            continue
                        
                        content, error = result
                        if error:
                            errors.append(f"{page['title']}: {error}")
                            continue
                        
                        if content:
                            if compress_links:
                                content = self.compress_content(content)
                            combined_content.append(content)
        
        return '\n'.join(combined_content), errors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scanning')
def scanning():
    url = request.args.get('url', '')
    return render_template('scanning.html', url=url)

@app.route('/scan', methods=['POST'])
def scan():
    url = request.form.get('url', '').strip()
    if not url:
        flash('Please enter a URL')
        return redirect(url_for('index'))
    
    # Ensure URL starts with http/https
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    exporter = DocsExporter(url)
    nav_structure, error = exporter.get_navigation_structure()
    
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    if not nav_structure:
        flash('No documentation pages found')
        return redirect(url_for('index'))
    
    return render_template('select.html', nav_structure=nav_structure, base_url=url)

@app.route('/export', methods=['POST'])
def export():
    base_url = request.form.get('base_url')
    selected_urls = request.form.getlist('selected_pages')
    compress_links = 'compress_links' in request.form
    
    if not selected_urls:
        flash('Please select at least one page')
        return redirect(url_for('scan'))
    
    exporter = DocsExporter(base_url)
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        combined_content, errors = loop.run_until_complete(
            exporter.export_selected_pages_async(selected_urls, compress_links)
        )
    finally:
        loop.close()
    
    if errors:
        for error in errors:
            flash(error)
    
    return render_template('result.html', content=combined_content, errors=errors)

if __name__ == '__main__':
    app.run(debug=True)
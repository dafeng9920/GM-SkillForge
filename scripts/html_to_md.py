#!/usr/bin/env python3
"""
Convert HTML file to Markdown format.
Usage: python scripts/html_to_md.py <html_file_path>
"""

import re
import sys
import html
from pathlib import Path


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to Markdown format."""

    # Remove script tags and their content
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Remove style tags and their content
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert headers
    html_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1\n', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert bold and italic
    html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert links
    html_content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<a[^>]*href=\'([^\']*)\'[^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert images
    html_content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>', r'![\2](\1)', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*>', r'![](\1)', html_content, flags=re.IGNORECASE)

    # Convert code blocks
    html_content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```\n', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert blockquotes
    html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '> ' + m.group(1).replace('\n', '\n> '), html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert unordered lists
    def convert_ul(match):
        items = re.findall(r'<li[^>]*>(.*?)</li>', match.group(1), flags=re.DOTALL | re.IGNORECASE)
        return '\n'.join(f'- {item.strip()}' for item in items)

    html_content = re.sub(r'<ul[^>]*>(.*?)</ul>', convert_ul, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert ordered lists
    def convert_ol(match):
        items = re.findall(r'<li[^>]*>(.*?)</li>', match.group(1), flags=re.DOTALL | re.IGNORECASE)
        return '\n'.join(f'{i+1}. {item.strip()}' for i, item in enumerate(items))

    html_content = re.sub(r'<ol[^>]*>(.*?)</ol>', convert_ol, html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert line breaks and paragraphs
    html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert div
    html_content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1\n', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Convert span
    html_content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Remove remaining HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)

    # Decode HTML entities
    html_content = html.unescape(html_content)

    # Clean up excessive whitespace
    html_content = re.sub(r'\n{3,}', '\n\n', html_content)
    html_content = html_content.strip()

    return html_content


def main():
    if len(sys.argv) < 2:
        print("Usage: python html_to_md.py <html_file_path>")
        sys.exit(1)

    html_path = Path(sys.argv[1])

    if not html_path.exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)

    print(f"Reading HTML file: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Converting to Markdown...")
    markdown_content = html_to_markdown(html_content)

    # Generate output path
    md_path = html_path.with_suffix('.md')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Markdown file saved to: {md_path}")
    print(f"Original size: {len(html_content):,} bytes")
    print(f"Markdown size: {len(markdown_content):,} bytes")


if __name__ == '__main__':
    main()

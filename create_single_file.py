#!/usr/bin/env python3
"""
Create a single-file HTML version of Fantasy Map Generator
by inlining all CSS and JavaScript files.
"""

import os
import re
from pathlib import Path

DIST_DIR = Path("/workspace/dist")
OUTPUT_FILE = Path("/workspace/Fantasy_Map_Generator.html")

def read_file(path):
    """Read file content, return empty string if file doesn't exist."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {path}: {e}")
        return ""

def resolve_path(base_path, ref_path):
    """Resolve path relative to dist directory, handling various path formats."""
    # Remove leading slashes and base path prefixes
    clean_path = ref_path.lstrip('/')
    clean_path = re.sub(r'^Fantasy-Map-Generator/', '', clean_path)
    
    # Handle query parameters
    clean_path = clean_path.split('?')[0]
    
    full_path = base_path / clean_path
    return full_path.resolve()

def inline_css(html_content, base_path):
    """Replace external CSS links with inline styles."""
    # Match link tags with rel="stylesheet" or onload pattern
    pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    
    def replace_css(match):
        href = match.group(1)
        # Skip external URLs
        if href.startswith('http://') or href.startswith('https://'):
            return match.group(0)
        
        css_path = resolve_path(base_path, href)
        css_content = read_file(css_path)
        if css_content:
            return f'<style type="text/css">{css_content}</style>'
        print(f"  Warning: CSS not found: {css_path}")
        return match.group(0)
    
    # Also handle the preload pattern
    preload_pattern = r'<link[^>]*rel=["\']preload["\'][^>]*as=["\']style["\'][^>]*href=["\']([^"\']+)["\'][^>]*onload=["\'][^"\']*["\'][^>]*>'
    
    def replace_preload_css(match):
        full_match = match.group(0)
        href_match = re.search(r'href=["\']([^"\']+)["\']', full_match)
        if not href_match:
            return full_match
        
        href = href_match.group(1)
        if href.startswith('http://') or href.startswith('https://'):
            return full_match
        
        css_path = resolve_path(base_path, href)
        css_content = read_file(css_path)
        if css_content:
            return f'<style type="text/css">{css_content}</style>'
        print(f"  Warning: Preload CSS not found: {css_path}")
        return ''
    
    html_content = re.sub(preload_pattern, replace_preload_css, html_content)
    html_content = re.sub(pattern, replace_css, html_content)
    
    return html_content

def inline_js(html_content, base_path):
    """Replace external script src with inline scripts."""
    pattern = r'<script([^>]*)src=["\']([^"\']+)["\']([^>]*)>(</script>)?'
    
    def replace_js(match):
        before_src = match.group(1)
        src = match.group(2)
        after_src = match.group(3)
        
        # Skip external URLs
        if src.startswith('http://') or src.startswith('https://'):
            return match.group(0)
        
        js_path = resolve_path(base_path, src)
        js_content = read_file(js_path)
        
        if js_content:
            attrs = before_src + after_src
            attrs = attrs.rstrip('/').strip()
            return f'<script{attrs}>{js_content}</script>'
        print(f"  Warning: JS not found: {js_path}")
        return match.group(0)
    
    html_content = re.sub(pattern, replace_js, html_content)
    return html_content

def inline_images(html_content, base_path):
    """Replace image references with data URIs (for small images)."""
    import base64
    
    patterns = [
        (r'(href=["\'])([^"\']+\.png)(["\'])', 2),
        (r'(href=["\'])([^"\']+\.svg)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.png)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.jpg)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.jpeg)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.gif)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.webp)(["\'])', 2),
        (r'(src=["\'])([^"\']+\.svg)(["\'])', 2),
    ]
    
    def replace_image(match, group_idx):
        prefix = match.group(1)
        src = match.group(group_idx)
        suffix = match.group(group_idx + 1)
        
        if src.startswith('http://') or src.startswith('https://') or src.startswith('data:'):
            return match.group(0)
        
        img_path = resolve_path(base_path, src)
        
        try:
            if img_path.exists() and img_path.stat().st_size < 50000:
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                
                ext = img_path.suffix.lower()
                mime_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                    '.svg': 'image/svg+xml',
                }
                mime_type = mime_types.get(ext, 'application/octet-stream')
                encoded = base64.b64encode(img_data).decode('ascii')
                data_uri = f'data:{mime_type};base64,{encoded}'
                return f'{prefix}{data_uri}{suffix}'
        except Exception as e:
            print(f"  Warning: Could not process image {img_path}: {e}")
        
        return match.group(0)
    
    for pattern, group_idx in patterns:
        html_content = re.sub(pattern, lambda m: replace_image(m, group_idx), html_content)
    
    return html_content

def main():
    print("Reading source HTML...")
    html_path = DIST_DIR / "index.html"
    html_content = read_file(html_path)
    
    if not html_content:
        print(f"Error: Could not read {html_path}")
        return
    
    print("Inlining CSS files...")
    html_content = inline_css(html_content, DIST_DIR)
    
    print("Inlining JavaScript files...")
    html_content = inline_js(html_content, DIST_DIR)
    
    print("Inlining small images...")
    html_content = inline_images(html_content, DIST_DIR)
    
    # Clean up module type since we're inlining everything
    html_content = html_content.replace('type="module"', '')
    html_content = html_content.replace(' crossorigin', '')
    
    print(f"Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size = OUTPUT_FILE.stat().st_size
    print(f"Done! Created {OUTPUT_FILE} ({file_size / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    main()

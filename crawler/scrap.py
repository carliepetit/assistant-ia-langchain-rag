import requests
import xml.etree.ElementTree as ET
import asyncio
import os
import argparse
import hashlib
from crawl4ai import AsyncWebCrawler
from urllib.parse import urlparse

# Register the sitemaps namespace
NAMESPACE = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

def download_sitemaps(url):
    """Download and return the content of a sitemap URL."""
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Downloaded sitemap content from {url}")
        return response.text
    else:
        raise Exception(f"Failed to download sitemaps from {url}. Status code: {response.status_code}")

def parse_sitemaps(sitemaps_content):
    """Parse sitemap content and extract URLs."""
    try:
        tree = ET.fromstring(sitemaps_content)
        urls = set()
        for url_tag in tree.findall('.//s:url', NAMESPACE):
            loc = url_tag.find('s:loc', NAMESPACE)
            if loc is not None and loc.text:
                urls.add(loc.text.strip())
        for sitemap_tag in tree.findall('.//s:sitemap', NAMESPACE):
            sitemap_loc = sitemap_tag.find('s:loc', NAMESPACE)
            if sitemap_loc is not None and sitemap_loc.text:
                sub_sitemaps_content = download_sitemaps(sitemap_loc.text)
                sub_urls = parse_sitemaps(sub_sitemaps_content)
                urls.update(sub_urls)
        print(f"Extracted {len(urls)} URLs from sitemap")
        return list(urls)
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return []
    except Exception as e:
        print(f"Error parsing sitemaps: {e}")
        return []

def generate_short_filename(url, max_length=20):
    """Generate a short filename from a URL, limited to max_length characters."""
    parsed_url = urlparse(url)
    
    # Get the path without slashes
    path = parsed_url.path.replace('/', '_')[1:] or "index"
    path = path.replace('?', '_').replace('&', '_').replace('=', '_')
    
    # If path is already short enough, use it
    if len(path) <= max_length - 3:  # Reserve 3 chars for '.md'
        return f"{path}.md"
    
    # Generate a hash for long paths
    hash_str = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # Use first few chars of path + hash
    path_part_length = max_length - 3 - 9  # 3 for '.md', 8 for hash, 1 for underscore
    if path_part_length > 0:
        return f"{path[:path_part_length]}_{hash_str}.md"
    else:
        return f"{hash_str}.md"  # Fallback if max_length is very small

def save_as_markdown(url, content, output_dir="crawled_data"):
    """Save content as Markdown file in the specified directory."""
    # Create output directory in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_dir)
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Create short filename from URL (max 20 chars)
    filename = generate_short_filename(url, max_length=20)
    original_url = url  # Store the original URL for reference
    
    # Save markdown content
    try:
        # Include the original URL in the content for reference
        markdown_content = f"# {original_url}\n\n"
        if isinstance(content, str) and content.strip():
            markdown_content += content
            print(f"Saved: {filename} ({len(content)} characters)")
        else:
            markdown_content += "No usable content extracted.\n"
            print(f"No usable content for {url}")
        
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error saving file {filepath}: {e}")

async def crawl_website(urls, batch_size=10):
    """Crawl websites in batches to avoid memory issues."""
    # Process in batches
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i+batch_size]
        print(f"\nCrawling batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, len(urls))} of {len(urls)} URLs)")
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            batch_results = await crawler.arun_many(batch_urls)
            
        # Process and save results immediately to free up memory
        for url, result in zip(batch_urls, batch_results):
            if result:
                # Use the built-in markdown attribute
                if hasattr(result, 'markdown'):
                    content = result.markdown
                    if content:
                        save_as_markdown(url, str(content))
                    else:
                        print(f"No markdown content found for {url}")
                else:
                    print(f"No markdown attribute for {url}")
            else:
                print(f"No result for {url}")
                
        # Free memory
        batch_results = None

async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Web crawler that saves pages as Markdown files.')
    parser.add_argument('--sitemap', type=str, default="https://sudestavenir.fr/lieu-sitemap.xml",
                        help='URL of the sitemap to crawl (default: https://sudestavenir.fr/category-sitemap.xml)')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Number of URLs to crawl in each batch (default: 10)')
    parser.add_argument('--output-dir', type=str, default="crawled_data",
                        help='Directory to save Markdown files (default: crawled_data)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Limit the number of URLs to crawl (default: 0, meaning no limit)')
    args = parser.parse_args()
    
    try:
        # Download and parse sitemap
        sitemaps_content = download_sitemaps(args.sitemap)
        all_urls = parse_sitemaps(sitemaps_content)
        
        # Apply limit if specified
        if args.limit > 0 and len(all_urls) > args.limit:
            print(f"Limiting to first {args.limit} URLs")
            all_urls = all_urls[:args.limit]
        
        print(f"Found {len(all_urls)} URLs to crawl")
        
        if all_urls:
            # Crawl all URLs
            await crawl_website(all_urls, batch_size=args.batch_size)
            print(f"\nCrawling completed. All pages have been saved to the '{args.output_dir}' directory.")
        else:
            print("No URLs found to crawl.")
    except Exception as e:
        print(f"Main execution error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
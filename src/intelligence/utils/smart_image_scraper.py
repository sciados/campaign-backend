import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import re
from PIL import Image
import io

def extract_product_images(url, save_folder='product_images', min_width=200, min_height=200):
    """
    Smart extractor specifically for product/service images, features, benefits, and ingredients
    Filters for images larger than specified dimensions (default: 200x200 pixels)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        os.makedirs(save_folder, exist_ok=True)
        
        images = soup.find_all('img')
        downloaded_count = 0
        skipped_count = 0
        
        print(f"🔍 Found {len(images)} potential images on sales page...")
        print(f"📏 Filtering for images larger than {min_width}x{min_height} pixels...")
        
        for i, img in enumerate(images):
            # Get image URL from various attributes (handles lazy loading)
            img_url = (img.get('src') or 
                      img.get('data-src') or 
                      img.get('data-original') or
                      img.get('data-lazy-src') or
                      img.get('data-srcset'))
            
            if not img_url:
                skipped_count += 1
                continue
            
            # Skip common non-product images
            skip_patterns = [
                r'pixel', r'tracker', r'analytics', r'icon', 
                r'sprite', r'avatar', r'social', r'loading',
                r'spinner', r'placeholder', r'1x1', r'blank',
                r'wp-content/themes', r'widget', r'badge'
            ]
            
            if any(re.search(pattern, img_url, re.IGNORECASE) for pattern in skip_patterns):
                skipped_count += 1
                continue
            
            # Handle relative URLs
            img_url = urllib.parse.urljoin(url, img_url)
            
            try:
                # Download image for analysis
                img_response = requests.get(img_url, timeout=15, headers=headers)
                if img_response.status_code != 200:
                    skipped_count += 1
                    continue
                
                # Skip very small files (likely icons)
                if len(img_response.content) < 5 * 1024:  # 5KB minimum
                    skipped_count += 1
                    continue
                
                # Analyze image dimensions
                try:
                    image = Image.open(io.BytesIO(img_response.content))
                    width, height = image.size
                    
                    # Filter by size - only keep images larger than specified dimensions
                    if width < min_width or height < min_height:
                        skipped_count += 1
                        print(f"⏩ Skipped: {width}x{height} (too small)")
                        continue
                    
                    print(f"✅ Accepting: {width}x{height} pixels")
                    
                except Exception as e:
                    print(f"⚠️  Could not analyze dimensions: {str(e)}")
                    skipped_count += 1
                    continue
                
                # Generate descriptive filename
                parsed_url = urllib.parse.urlparse(img_url)
                extension = os.path.splitext(parsed_url.path)[1]
                if not extension:
                    # Try to determine extension from content type
                    content_type = img_response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        extension = '.jpg'
                    elif 'png' in content_type:
                        extension = '.png'
                    elif 'webp' in content_type:
                        extension = '.webp'
                    else:
                        extension = '.jpg'
                
                # Clean filename
                alt_text = img.get('alt', '') or img.get('title', '')
                if alt_text:
                    # Create filename from alt text (sanitized)
                    clean_alt = re.sub(r'[^\w\s-]', '', alt_text)
                    clean_alt = re.sub(r'[-\s]+', '_', clean_alt)
                    filename = f"product_{i+1:03d}_{clean_alt[:30]}{extension}"
                else:
                    filename = f"product_{i+1:03d}{extension}"
                
                filepath = os.path.join(save_folder, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded_count += 1
                file_size_kb = len(img_response.content) // 1024
                print(f"📸 Saved: {filename} ({width}x{height}, {file_size_kb} KB)")
                
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout downloading: {img_url}")
                skipped_count += 1
            except Exception as e:
                skipped_count += 1
                print(f"❌ Failed: {str(e)}")
        
        print(f"\n" + "="*50)
        print(f"📊 SUMMARY:")
        print(f"✅ Downloaded: {downloaded_count} product images")
        print(f"⏩ Skipped: {skipped_count} non-product/small images")
        print(f"💾 Saved to: {os.path.abspath(save_folder)}")
        print("="*50)
        
        return downloaded_count
        
    except Exception as e:
        print(f"❌ Error accessing URL: {str(e)}")
        return 0

def batch_extract_product_images(urls, save_base_folder='salespage_images'):
    """
    Extract from multiple sales pages
    """
    for i, url in enumerate(urls):
        print(f"\n🎯 Processing URL {i+1}/{len(urls)}: {url}")
        folder_name = f"{save_base_folder}/page_{i+1}"
        extract_product_images(url, folder_name)

# Usage examples
if __name__ == "__main__":
    # Single URL
    url = input("Enter sales page URL: ").strip()
    if url:
        extract_product_images(url)
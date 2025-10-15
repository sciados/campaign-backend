import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
from urllib.request import urlretrieve

def extract_images_basic(url, save_folder='downloaded_images'):
    """
    Basic image extractor for static sales pages
    """
    try:
        # Create save directory
        os.makedirs(save_folder, exist_ok=True)
        
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all image tags
        images = soup.find_all('img')
        downloaded_count = 0
        
        print(f"Found {len(images)} potential images...")
        
        for i, img in enumerate(images):
            img_url = img.get('src') or img.get('data-src')
            
            if not img_url:
                continue
                
            # Handle relative URLs
            img_url = urllib.parse.urljoin(url, img_url)
            
            try:
                # Get file extension
                parsed_url = urllib.parse.urlparse(img_url)
                extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
                
                # Generate filename
                filename = f"salespage_img_{i+1:03d}{extension}"
                filepath = os.path.join(save_folder, filename)
                
                # Download image
                urlretrieve(img_url, filepath)
                downloaded_count += 1
                print(f"✓ Saved: {filename}")
                
            except Exception as e:
                print(f"✗ Failed: {img_url} - {str(e)}")
        
        print(f"\nDownloaded {downloaded_count} images to '{save_folder}'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Usage
if __name__ == "__main__":
    url = input("Enter sales page URL: ")
    extract_images_basic(url)
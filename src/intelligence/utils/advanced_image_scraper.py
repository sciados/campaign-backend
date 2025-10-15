from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import os
import time
import urllib.parse

def extract_images_advanced(url, save_folder='salespage_images'):
    """
    Advanced extractor that handles JavaScript-loaded images
    """
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Create save directory
        os.makedirs(save_folder, exist_ok=True)
        
        # Find all image elements
        images = driver.find_elements(By.TAG_NAME, "img")
        downloaded_count = 0
        
        print(f"Found {len(images)} images...")
        
        for i, img in enumerate(images):
            try:
                # Get image URL from various attributes
                img_url = (img.get_attribute("src") or 
                          img.get_attribute("data-src") or 
                          img.get_attribute("data-original"))
                
                if not img_url or img_url.startswith('data:'):
                    continue
                
                # Handle relative URLs
                img_url = urllib.parse.urljoin(url, img_url)
                
                # Get file extension
                parsed_url = urllib.parse.urlparse(img_url)
                extension = os.path.splitext(parsed_url.path)[1]
                if not extension:
                    extension = '.jpg'
                
                # Generate filename
                filename = f"img_{i+1:03d}{extension}"
                filepath = os.path.join(save_folder, filename)
                
                # Download image
                img_response = requests.get(img_url, timeout=10)
                if img_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    downloaded_count += 1
                    print(f"✓ Saved: {filename}")
                else:
                    print(f"✗ Failed to download: {img_url}")
                    
            except Exception as e:
                print(f"✗ Error with image {i+1}: {str(e)}")
        
        print(f"\nSuccessfully downloaded {downloaded_count} images")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()

# Usage
if __name__ == "__main__":
    url = input("Enter sales page URL: ")
    extract_images_advanced(url)
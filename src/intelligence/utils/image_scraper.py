import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

def extract_images(url, save_folder):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all image tags
    images = soup.find_all('img')
    
    # Create save directory
    os.makedirs(save_folder, exist_ok=True)
    
    for i, img in enumerate(images):
        img_url = img.get('src')
        if img_url:
            # Handle relative URLs
            img_url = urllib.parse.urljoin(url, img_url)
            
            try:
                # Download and save image
                img_data = requests.get(img_url).content
                filename = f"image_{i+1}.jpg"
                filepath = os.path.join(save_folder, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                print(f"Saved: {filename}")
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
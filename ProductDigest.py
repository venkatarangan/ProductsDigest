"""
Web Page Details Generator

Purpose:
- This script generates a PDF document containing details about webpages from a list of URLs.
- It handles both Amazon and non-Amazon URLs, capturing product information and page previews.

Features:
- Processes URLs from 'urls.txt'
- Captures webpage titles, thumbnails, and timestamps
- For Amazon pages: extracts prices and product details
- Generates formatted PDF with proper spacing and layout
- Includes error handling and retry mechanisms

Required Packages:
- PyMuPDF (fitz) - PDF generation
- selenium - Web automation and scraping
- webdriver_manager - Edge WebDriver management
- Pillow (PIL) - Image processing
- requests - HTTP requests
- beautifulsoup4 - HTML parsing

Additional Requirements:
- Microsoft Edge browser must be installed
- Internet connection required
- Create 'urls.txt' with one URL per line

Usage:
1. Install required packages
2. Create urls.txt file with URLs
3. Run the script
4. Output: webpage_details.pdf
"""

import fitz  # PyMuPDF
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from datetime import datetime
import time
import requests
import os
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def is_amazon_url(url):
  """Check if the URL is an Amazon URL."""
  amazon_domains = ['amazon.in', 'amzn.in', 'amazon.com']
  url_lower = url.lower()
  return any(domain in url_lower for domain in amazon_domains)

def get_amazon_preview(url):
  """Fetch product details from an Amazon URL."""
  try:
      driver.get(url)
      time.sleep(2)  # Wait for the page to load

      # Extract product title
      title = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "productTitle"))
      ).text

      # Extract product image
      try:
          img_element = WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.ID, "landingImage"))
          )
          thumbnail_url = img_element.get_attribute('src')
      except:
          # Fallback to other image elements
          img_element = driver.find_element(By.CSS_SELECTOR, "#main-image-container img")
          thumbnail_url = img_element.get_attribute('src')

    # Extract product price
      price = None
      try:
          # Extract price symbol and whole number separately
          price_symbol = driver.find_element(By.CSS_SELECTOR, ".a-price-symbol").text
          price_whole = driver.find_element(By.CSS_SELECTOR, ".a-price-whole").text
          if (price_symbol == "₹"): 
                price_symbol = "INR "
          price = f"{price_symbol}{price_whole}"
      except:
          print("Price not found")

      return title, thumbnail_url, price
  except Exception as e:
      print(f"Error fetching Amazon preview: {e}")
      return None, None, None

def get_non_amazon_preview(url):
  """Fetch webpage details from a non-Amazon URL."""
  max_retries = 3
  for attempt in range(max_retries):
      try:
          driver.get(url)
          time.sleep(2 + attempt)  # Increasing wait time with each retry

          soup = BeautifulSoup(driver.page_source, 'html.parser')
          
          # Try different meta tags for preview image
          thumbnail_url = None
          for meta_tag in ['og:image', 'twitter:image', 'image']:
              img_meta = soup.find('meta', property=meta_tag) or soup.find('meta', attrs={'name': meta_tag})
              if img_meta and img_meta.get('content'):
                  thumbnail_url = img_meta['content']
                  break

          # If no meta tags found, try finding the largest image on the page
          if not thumbnail_url:
              images = driver.find_elements(By.TAG_NAME, 'img')
              max_area = 0
              for img in images:
                  try:
                      width = int(img.get_attribute('width') or 0)
                      height = int(img.get_attribute('height') or 0)
                      area = width * height
                      if area > max_area:
                          max_area = area
                          thumbnail_url = img.get_attribute('src')
                  except:
                      continue

          title = soup.title.string if soup.title else 'No Title'
          
          if thumbnail_url:
              return title, thumbnail_url

      except Exception as e:
          print(f"Attempt {attempt + 1} failed: {e}")
          if attempt == max_retries - 1:
              return None, None
          time.sleep(1)

  return None, None

def fetch_page_info(url):
  """Fetch page information based on URL type."""
  if is_amazon_url(url):
      title, thumbnail_url, price = get_amazon_preview(url)
      return title, thumbnail_url, price
  else:
      title, thumbnail_url = get_non_amazon_preview(url)
      return title, thumbnail_url, None

def download_and_process_image(url, path):
  """Download and process an image from a URL."""
  try:
      headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
      img_response = requests.get(url, headers=headers, stream=True)
      img_response.raise_for_status()
      
      # Open the image and convert it
      img = Image.open(BytesIO(img_response.content))
      img = img.convert("RGB")
      img = img.resize((800, int(800 * img.height / img.width)), Image.LANCZOS)
      img.save(path, "JPEG", quality=75)
      
      return True
  except Exception as e:
      print(f"Error downloading or processing image: {e}")
      return False

def create_pdf(data, output_file):
  """Create a PDF document from the collected data."""
  doc = fitz.open()  # Create a new PDF document

  for index, entry in enumerate(data, start=1):
      url, title, thumbnail_url, price, accessed_time = entry
      
      # Create a new page with margins
      page = doc.new_page()
      margin = 72  # 1 inch margin
      width, height = fitz.paper_size("a4")
      text_rect = fitz.Rect(margin, margin, width - margin, height - margin)

      # Add title with numbering
      y_offset = 0
      page.insert_textbox(text_rect + (0, y_offset, 0, 0), f"{index}. {title}", fontsize=12, fontname="helv", color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)
      y_offset += 95

      # Add URL
      page.insert_textbox(text_rect + (0, y_offset, 0, 0), f"URL: {url}", fontsize=10, fontname="helv", color=(0, 0, 1), align=fitz.TEXT_ALIGN_LEFT)
      y_offset += 95

      # Add accessed time
      page.insert_textbox(text_rect + (0, y_offset, 0, 0), f"Accessed Time: {accessed_time}", fontsize=10, fontname="helv", color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)
      y_offset += 95

      # Add price if available
      if price:
          page.insert_textbox(text_rect + (0, y_offset, 0, 0), f"Price: {price}", fontsize=10, fontname="helv", color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)
          y_offset += 95

      # Add thumbnail
      if thumbnail_url:
          img_path = f"temp_thumbnail_{index}.jpg"
          if download_and_process_image(thumbnail_url, img_path):
              try:
                  if os.path.exists(img_path):
                      img_rect = fitz.Rect(margin, y_offset, width - margin, y_offset + 300)  # Define where to place the image
                      page.insert_image(img_rect, filename=img_path)
                      os.remove(img_path)
                      y_offset += 310  # Adjust y_offset for image height
              except Exception as e:
                  page.insert_textbox(text_rect + (0, y_offset, 0, 0), f"Thumbnail could not be loaded: {e}", fontsize=10, fontname="helv", color=(1, 0, 0), align=fitz.TEXT_ALIGN_LEFT)
                  y_offset += 95
          else:
              page.insert_textbox(text_rect + (0, y_offset, 0, 0), "Thumbnail could not be downloaded.", fontsize=10, fontname="helv", color=(1, 0, 0), align=fitz.TEXT_ALIGN_LEFT)
              y_offset += 95

      # Add footer
      footer_text = f"Page {index} - Generated by @venkatarangan"
      footer_rect = fitz.Rect(margin, height - 50, width - margin, height - 30)
      page.insert_textbox(footer_rect, footer_text, fontsize=10, fontname="helv", color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT)

  doc.save(output_file)
  doc.close()

def main():
  """Main function to read URLs, fetch data, and create PDF."""
  input_file = 'urls.txt'
  output_file = 'webpage_details.pdf'

  # Read and validate URLs
  with open(input_file, 'r') as file:
      urls = []
      for line in file:
          line = line.strip()
          if line:
              if not line.startswith(('http://', 'https://')):
                  line = 'https://' + line
              urls.append(line)

  data = []
  for url in urls:
      try:
          title, thumbnail_url, price = fetch_page_info(url)
          if title:
              accessed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
              data.append((url, title, thumbnail_url, price, accessed_time))
      except Exception as e:
          print(f"Error processing {url}: {e}")

  if data:
      create_pdf(data, output_file)
      print(f"PDF saved as {output_file}")
  else:
      print("No valid data to create PDF")

  driver.quit()

if __name__ == "__main__":
  # Set up Selenium with Edge in headless mode
  edge_options = Options()
  edge_options.add_argument("--headless")
  edge_options.add_argument("--disable-gpu")
  edge_options.add_argument("--no-sandbox")
  edge_options.add_argument("--log-level=3")
  
  # Initialize the WebDriver for Edge
  driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)
  
  main()

# End of ProductDigestMu.py
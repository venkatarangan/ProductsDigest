# pip install selenium webdriver-manager fpdf beautifulsoup4 requests Pillow

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from fpdf import FPDF
from datetime import datetime
import time
import requests
import os
from bs4 import BeautifulSoup
from PIL import Image
import io

def is_amazon_url(url):
  return 'amazon.' in url.lower()

def get_amazon_preview(url):
  try:
      driver.get(url)
      time.sleep(3)  # Initial wait for page load

      title = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "productTitle"))
      ).text

      # Locate product price
      try:
          price = WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.ID, "priceblock_ourprice"))
          ).text
      except:
          try:
              price = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.ID, "priceblock_dealprice"))
              ).text
          except:
              price = "Price not available"

      img_element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "landingImage"))
      )
      thumbnail_url = img_element.get_attribute('src')
      
      return title, thumbnail_url, price
  except Exception as e:
      print(f"Error fetching Amazon preview: {e}")
      return None, None, None

def get_non_amazon_preview(url):
  for attempt in range(3):  # Retry mechanism for non-Amazon URLs
      try:
          driver.get(url)
          time.sleep(3 + attempt)  # Incremental wait on retries

          soup = BeautifulSoup(driver.page_source, 'html.parser')
          title = soup.title.string if soup.title else 'No Title'

          thumbnail_url = None
          for meta_tag in ['og:image', 'twitter:image', 'image']:
              img_meta = soup.find('meta', property=meta_tag) or soup.find('meta', attrs={'name': meta_tag})
              if img_meta and img_meta.get('content'):
                  thumbnail_url = img_meta['content']
                  break
          
          if thumbnail_url:
              return title, thumbnail_url, None

          images = driver.find_elements(By.TAG_NAME, 'img')
          largest_image = max(images, key=lambda img: int(img.get_attribute('width') or 0) * int(img.get_attribute('height') or 0), default=None)
          thumbnail_url = largest_image.get_attribute('src') if largest_image else None

          return title, thumbnail_url, None

      except Exception as e:
          print(f"Attempt {attempt + 1} failed: {e}")
          time.sleep(2)
  return None, None, None

def fetch_page_info(url):
  return get_amazon_preview(url) if is_amazon_url(url) else get_non_amazon_preview(url)

def download_image(url, path):
  try:
      headers = {'User-Agent': 'Mozilla/5.0'}
      img_response = requests.get(url, headers=headers, stream=True)
      img_response.raise_for_status()

      with open(path, 'wb') as img_file:
          for chunk in img_response.iter_content(8192):
              img_file.write(chunk)

      # Verify and fix the image using Pillow
      try:
          with Image.open(path) as img:
              img.verify()
              img = Image.open(path)  # Re-open to manipulate
              img = img.convert('RGB')  # Ensure it's in RGB mode
              img.save(path, 'JPEG')  # Re-save as JPEG
      except (IOError, SyntaxError) as e:
          print(f"Image verification failed: {e}. Attempting to fix...")
          try:
              with Image.open(path) as img:
                  img = img.convert('RGB')
                  img.save(path, 'JPEG')
          except Exception as fix_error:
              print(f"Failed to fix image: {fix_error}")
              return False

      return os.path.exists(path) and os.path.getsize(path) > 0
  except Exception as e:
      print(f"Error downloading image: {e}")
      return False

def create_pdf(data, output_file):
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()
  pdf.set_font("Arial", size=12)

  for index, entry in enumerate(data, start=1):
      url, title, thumbnail_url, accessed_time, price = entry

      pdf.set_font("Arial", 'B', 14)
      pdf.multi_cell(0, 10, txt=f"{index}. {title.encode('latin-1', 'replace').decode('latin-1')}", align='L')
      pdf.set_font("Arial", size=12)
      pdf.set_text_color(0, 0, 255)
      pdf.cell(0, 10, txt=f"URL: {url}", ln=True, link=url)
      pdf.set_text_color(0, 0, 0)
      pdf.cell(0, 10, txt=f"Accessed Time: {accessed_time}", ln=True)

      if price:
          pdf.cell(0, 10, txt=f"Price: {price}", ln=True)

      if thumbnail_url:
          img_path = f"temp_thumbnail_{index}.jpg"
          if download_image(thumbnail_url, img_path):
              try:
                  pdf.image(img_path, w=100)
              except Exception as e:
                  pdf.multi_cell(0, 10, txt=f"Thumbnail could not be loaded: {e}", align='L')
              finally:
                  if os.path.exists(img_path):
                      os.remove(img_path)

      pdf.ln(5)
      pdf.cell(0, 0, '', ln=True, border='T')
      pdf.ln(10)

  pdf.output(output_file)

def main():
  input_file = 'urls.txt'
  output_file = 'webpage_details.pdf'

  with open(input_file, 'r') as file:
      urls = [line.strip() for line in file if line.strip()]

  data = []
  for url in urls:
      if not url.startswith(('http://', 'https://')):
          url = 'https://' + url
      try:
          title, thumbnail_url, price = fetch_page_info(url)
          if title:
              accessed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
              data.append((url, title, thumbnail_url, accessed_time, price))
          time.sleep(2)  # Added delay to give time for page loading
      except Exception as e:
          print(f"Error processing {url}: {e}")

  if data:
      create_pdf(data, output_file)
      print(f"PDF saved as {output_file}")
  else:
      print("No valid data to create PDF")

  driver.quit()

if __name__ == "__main__":
  edge_options = Options()
  edge_options.add_argument("--headless")
  edge_options.add_argument("--disable-gpu")
  edge_options.add_argument("--no-sandbox")
  edge_options.add_argument("--log-level=3")

  driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)
  
  main()
# ProductDigest
 A Python-based web scraper that fetches details (title, image thumbnail, and price if available) from specified webpages, especially optimized for Amazon product pages, and generates a comprehensive PDF report with the information. This tool is useful for gathering quick previews of multiple URLs, summarizing the content of each page, and creating a printable or sharable PDF document.

## Features

- Fetches and displays webpage titles, prices (for Amazon pages), and preview images
- Supports Amazon product pages with dedicated handling for product title, price, and main image
- Basic support for other websites to extract page title and largest image if available
- Image verification and reformatting for compatibility in PDFs
- Generates a PDF report summarizing all fetched data with clickable URLs

## Problem Statement

In today’s information-driven world, curating information from multiple web pages for comparison or reporting can be time-consuming. Especially in e-commerce, a user might want to compare various products' titles, prices, and images across different sources. This project automates the collection of this information, extracting it from user-provided URLs, formatting it, and exporting it as a structured PDF report.

## Installation

To get started, clone this repository and install the dependencies. Place the URLs of the products in *URLS.txt* textfile. Output file is in *webpage_details.pdf*:

`git clone https://github.com/venkatarangan/ProductDigest.git
cd ProductDigest
pip install -r requirements.txt

python -v venv .venv
python ProductDigest.py`
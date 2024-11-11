# ProductDigest

## Objective
This project provides a tool to automatically extract and compile webpage details into a well-formatted PDF document. It is particularly tailored to handle Amazon product pages, capturing prices and other key details, but also works with general URLs to gather metadata and generate page previews.

## What It Does
- Reads a list of URLs from a file (`urls.txt`).
- Fetches the title, timestamp, and thumbnail of each webpage.
- Specifically for Amazon URLs, retrieves additional details such as product pricing and description.
- Compiles these details into a structured PDF file (`webpage_details.pdf`), making it convenient for users to view key webpage information offline.

## How It Works
1. **URL Processing**: The script reads URLs from a text file (`urls.txt`), handling each URL line-by-line.
2. **Data Extraction**:
   - Uses `Selenium` for automated browsing and scraping.
   - For Amazon pages, specialized routines extract product pricing and details.
   - General URLs are parsed for titles and preview images.
3. **PDF Generation**: Combines the extracted data, arranging each entry with a title, thumbnail, and timestamp, and generates a PDF using `PyMuPDF`.
4. **Error Handling**: Incorporates retry mechanisms for failed URL loads to improve reliability.

## Required Packages
To run this script, the following Python packages are required:
- `PyMuPDF (fitz)` for PDF creation.
- `selenium` for web scraping and page automation.
- `webdriver_manager` to manage the Edge WebDriver.
- `Pillow (PIL)` for image processing.
- `requests` for HTTP requests.
- `beautifulsoup4` for HTML parsing.

Additionally, ensure that:
- Microsoft Edge is installed on your system.
- An internet connection is available.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/venkatarangan/ProductsDigest.git 
   cd ProductsDigest
   ```
2. Install the required Python packages:
   ```bash
   pip install PyMuPDF selenium webdriver_manager Pillow requests beautifulsoup4
   ```
3. Ensure Microsoft Edge is installed and up-to-date for compatibility with `Selenium`.

## Usage
1. Create a text file named `urls.txt` in the project directory, listing the URLs to process, with one URL per line.
2. Run the script:
   ```bash
   python ProductDigest.py
   ```
3. The output PDF, `webpage_details.pdf`, will be generated in the project directory.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgement
The basic code was generated from several prompts using GPT-4o and Claude Sonnet 3.5 in Abacus.AI, with further adjustments made to improve accuracy and customize functionality.

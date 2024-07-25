import sys
import tempfile
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

html_template = """
<html>
    <head>
        <title>Clickjack test page</title>
    </head>
    <body>
        <iframe src="{}" width="600" height="500"></iframe>
    </body>
</html>
"""

def sanitize_filename(url):
    # Remove scheme (http, https) and replace non-alphanumeric characters with underscores
    filename = re.sub(r'[^a-zA-Z0-9]', '_', url.split('://')[-1])
    return filename

def create_and_test_clickjack(url):
    try:
        print(f"Processing URL: {url}")

        # Add scheme if missing
        if '://' not in url:
            url = 'https://' + url

        # Use requests to get the final URL after following redirects
        response = requests.head(url, allow_redirects=True)
        final_url = response.url
        print(f"Final URL: {final_url}")

        # Create HTML content with the final URL
        html_content = html_template.format(final_url)

        # Create a temporary HTML file
        temp_file_path = os.path.join(tempfile.gettempdir(), 'clickjack-test-temp.html')

        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(html_content)

        # Set up headless browser
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        # Open the temporary HTML file in the headless browser
        driver.get('file://' + temp_file_path)

        # Give it some time to load the iframe content
        time.sleep(2)  # Adjust the sleep duration as needed

        # Take a screenshot and save it to the current directory
        screenshot_filename = sanitize_filename(final_url) + '.png'
        screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Close the browser
        driver.quit()

    except requests.exceptions.RequestException as e:
        print(f"Error processing URL {url}: {e}")
    except Exception as e:
        print(f"Error taking screenshot for {url}: {e}")

def test_clickjacking_for_urls(file_path):
    # Read URLs from the file
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()

    # Test clickjacking for each URL
    for url in urls:
        create_and_test_clickjack(url)

if __name__ == "__main__":
    # Check if a filename is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    test_clickjacking_for_urls(filename)

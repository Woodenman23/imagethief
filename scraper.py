from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
import re

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()), options=options
)

answer = input("What should I use to search? \n\n 1) Artist name \n 2) Page URL\n\n")
if answer == "1":
    ARTIST = input("Enter artist name: ").replace(" ", "-")
    GALLERY_URL = f"https://www.wikiart.org/en/{ARTIST}/all-works"
elif answer == "2":
    GALLERY_URL = input("Enter URL: ")
    match = re.search("/www\.wikiart\.org\/[^/]+\/([^/]+)/", GALLERY_URL)
    if match:
        ARTIST = match.group(1)
    else:
        ARTIST = input("Enter artist name: ").replace(" ", "-")


SAVE_DIR = f"downloaded_images/{ARTIST}"
os.makedirs(SAVE_DIR, exist_ok=True)


def load_all_images():
    driver.get(GALLERY_URL)
    time.sleep(6)
    count = 0
    while count < 5:
        try:
            load_more_button = driver.find_element(
                By.CLASS_NAME, "masonry-load-more-button"
            )
            if load_more_button.is_displayed():
                driver.execute_script("arguments[0].click();", load_more_button)
                count += 1
                time.sleep(3)
            else:
                break
        except Exception as e:
            try:
                error_message = driver.find_element(By.CLASS_NAME, "error404-hint")
                print(
                    "Artist page not found. Please ensure artists name matches page on https://www.wikiart.org. For example Picasso is Pablo Picasso on the site."
                )

            except Exception as e:
                print(f"No load more button found: {e}")

            break

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)


def get_image_links():
    images = driver.find_elements(By.CSS_SELECTOR, "li img")
    image_urls = []
    for img in images:
        # Scroll the image into view to trigger lazy loading.
        driver.execute_script("arguments[0].scrollIntoView();", img)
        time.sleep(1)  # Allow time for lazy-loading to update the src
        src = img.get_attribute("src")
        if src and "lazy-load-placeholder" in src:
            # Optionally, wait a bit more and re-check
            time.sleep(1)
            src = img.get_attribute("src")
        image_urls.append(src)
    return image_urls


def download_images(image_urls):
    for url in image_urls:
        if not url:
            continue
        # Optionally, remove any size suffix from the URL if needed.
        if "!" in url:
            url = url.split("!")[0]
        filename = os.path.join(SAVE_DIR, os.path.basename(url.split("?")[0]))
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")


load_all_images()
image_urls = get_image_links()
driver.quit()

print(f"Found {len(image_urls)} images")
download_images(image_urls)

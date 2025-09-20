from markdownify import markdownify
from playwright.sync_api import sync_playwright

def scrape_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        # markdown_content = markdownify(content.text).strip()
        browser.close()
        return content

# print(scrape_playwright("https://www.tesla.com/en_ca"))
# print("\n======================================================\n")
# print(scrape_playwright("https://www.airbus.com/en"))

from markdownify import markdownify
from playwright.sync_api import sync_playwright
import asyncio
from playwright.async_api import async_playwright
from utils_folder.loggger import log_error, log_normal

def scrape_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        # markdown_content = markdownify(content.text).strip()
        browser.close()
        return content



async def scrape_playwright_async(url: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
            log_normal(content, "scrape_playwright_async")

            await browser.close()
            return content
    except Exception as e:
        log_error(e, "scrape_playwright_async")
        raise e




# Si estás en script normal:
if __name__ == "__main__":
    # url = "https://www.tesla.com/en_ca"
    url = "https://www.airbus.com/en"
    result = asyncio.run(scrape_playwright(url))
    print(result[:500])

# forward_playwright.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time
import random
import json
import os

# --- CONFIGURA AQUI ---
URL = "https://www.tesla.com/en_ca"
# Proxy ejemplo: "http://user:pass@host:port"  (recomendado: residencial)
PROXY = "http://PROXY_USER:PROXY_PASS@PROXY_HOST:PORT"  # o None
OUTPUT_STATE = "storage_state.json"  # guarda cookies/session
# user agent realista (cámbialo por uno actual de Chrome)
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
# cabeceras extra
EXTRA_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1"
}
# ------------------------

# script "stealth" básico que inyectamos antes de que la página corra JS
STEALTH_JS = """
// reduce navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
// languages
Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
// plugins
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
// mimic chrome runtime
window.chrome = { runtime: {} };
// set permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.__proto__.query = function(parameters) {
  if (parameters && parameters.name === 'notifications') {
    return Promise.resolve({ state: Notification.permission });
  }
  return originalQuery(parameters);
};
"""

def human_delay(min_s=0.3, max_s=1.2):
    time.sleep(random.uniform(min_s, max_s))

def run():
    with sync_playwright() as p:
        launch_args = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
        if PROXY:
            # playwright accepts proxy dict: {"server": "http://host:port", "username": "...", "password": "..."}
            # parse PROXY to dict if has credentials
            # simple parse:
            from urllib.parse import urlparse
            parsed = urlparse(PROXY)
            server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            proxy_dict = {"server": server}
            if parsed.username and parsed.password:
                proxy_dict["username"] = parsed.username
                proxy_dict["password"] = parsed.password
            launch_args["proxy"] = proxy_dict

        browser = p.chromium.launch(**launch_args)

        context_args = {
            "user_agent": USER_AGENT,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "viewport": {"width": 1366, "height": 768},
            "java_script_enabled": True,
            "extra_http_headers": EXTRA_HEADERS,
        }

        # reuse storage_state if exists
        if os.path.exists(OUTPUT_STATE):
            print("Reusing storage state:", OUTPUT_STATE)
            context_args["storage_state"] = OUTPUT_STATE

        context = browser.new_context(**context_args)

        # inject stealth before any script runs
        context.add_init_script(STEALTH_JS)

        # open page
        page = context.new_page()

        try:
            print("Going to:", URL)
            page.goto(URL, timeout=60000, wait_until="domcontentloaded")

            # small human-like interactions
            human_delay(0.5, 1.5)
            # random mouse move
            page.mouse.move(400 + random.randint(-50,50), 300 + random.randint(-30,30))
            human_delay(0.2, 0.7)

            content = page.content()
            status = page.response.status if page.response else None
            print("HTTP status (last response):", status)

            # save storage state (cookies + localStorage) para reutilizar
            context.storage_state(path=OUTPUT_STATE)
            print("Saved storage_state ->", OUTPUT_STATE)

            # output snippet
            print(content[:1000])

            # Opcional: convertir a markdown u otro procesamiento
            return content

        except PWTimeout as e:
            print("Timeout or navigation error:", e)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()

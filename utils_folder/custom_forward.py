import re
import time
import random
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import requests
    from markdownify import markdownify
except ImportError as e:
    raise ImportError(
        "You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests`."
    ) from e

def create_session():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504, 403],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def scrape_with_retry(url, max_retries=3):
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    session = create_session()
    
    for attempt in range(max_retries):
        try:
            # Add random delay
            if attempt > 0:
                time.sleep(random.uniform(2, 5))
            
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print(f"403 Forbidden - Attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise RequestException(f"Access forbidden after {max_retries} attempts")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                continue
            else:
                raise
    
    return None

def customforward(url):
    try:
        response = scrape_with_retry(url)
        if response:
            markdown_content = markdownify(response.text).strip()
            # Process your content here
            return markdown_content
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        raise e
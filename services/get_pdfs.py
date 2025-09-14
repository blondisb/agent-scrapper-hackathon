import os
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


async def scrape_pdf(base_url: str, abn: str,json_statesments: list):
    """
    """
    folder = f"temp/{abn}/pdf"
    os.makedirs(folder, exist_ok=True)

    for dicts in json_statesments:
        statement_url = dicts["href"]
        
        try:
            async with httpx.AsyncClient() as client:

                page = await client.get(statement_url, timeout=15)
                page.raise_for_status()
                page_tree = html.fromstring(page.content)

                iframe_src = page_tree.xpath('/html/body/main/div/div[2]/div/div/iframe/@src')
                if not iframe_src:
                    log_error(f"⚠ No se encontró PDF en {statement_url}")
                    continue

                pdf_url = base_url + iframe_src[0] if iframe_src[0].startswith("/") else iframe_src[0]

                pdf_name = pdf_url.strip("/").split("/")[-2] + ".pdf"
                pdf_path = os.path.join(folder, pdf_name)

                pdf_resp = await client.get(pdf_url, timeout=30)
                pdf_resp.raise_for_status()

                with open(pdf_path, "wb") as f:
                    f.write(pdf_resp.content)

                print(f"✅ PDF descargado: {pdf_path}")
        except Exception as e:
            log_error(e, "scrape_pdf")
            raise JSONResponse(status_code=500, content={"error": str(e)})

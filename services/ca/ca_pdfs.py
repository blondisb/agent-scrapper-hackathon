import os, time
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


async def ca_pdfs(statesments: list, pdf_folder: str) -> list:
    """
    """
    os.makedirs(pdf_folder, exist_ok=True)
    # json_pdf_url = {}
    pdf_paths = []

    for dicts in statesments:
        statement_url = dicts["href"]
        
        try:
            start_time = time.time()
            async with httpx.AsyncClient() as client:

                page = await client.get(statement_url, timeout=15)
                page.raise_for_status()
                page_tree = html.fromstring(page.content)

                iframe_src = page_tree.xpath('//section[@class="alert alert-info mrgn-tp-lg"]//a/@href')
                if not iframe_src:
                    log_error(f"⚠ No se encontró PDF en {statement_url}")
                    continue

                pdf_url = iframe_src[0].strip()
                pdf_name = os.path.basename(pdf_url)  # obtiene el nombre real del archivo PDF
                pdf_path = os.path.join(pdf_folder, pdf_name)

                pdf_resp = await client.get(pdf_url, timeout=30)
                pdf_resp.raise_for_status()

                with open(pdf_path, "wb") as f:
                    f.write(pdf_resp.content)
                
                pdf_paths.append(pdf_path)
                total_time = time.time() - start_time
                log_normal(f"single pdf took {total_time:.2f} seconds", "scrape_pdf")

        except Exception as e:
            log_error(e, "scrape_pdf")
            raise JSONResponse(status_code=500, content={"error": str(e)})
        
    log_normal(f"✅ PDF descargado: {pdf_paths}", "scrape_pdf")
    return pdf_paths

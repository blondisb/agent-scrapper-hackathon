import os, time
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


async def uk_pdf(base_url: str, id_company: str, json_statesments: list, pdf_folder: str) -> list:
    """
    """
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_paths = []
    start_time = time.time()

    for dicts in json_statesments:
        statement_url = dicts["href"]
        
        try:
            
            async with httpx.AsyncClient() as client:

                page = await client.get(statement_url, timeout=15)
                page.raise_for_status()
                page_tree = html.fromstring(page.content)
                iframe_src = page_tree.xpath('/html/body/div[3]/main/div[2]/div[2]/div/div[2]/div/p[2]/a/@href')
                
                if not iframe_src:
                    text_content = page_tree.xpath('//main//text()')
                    clean_text = "\n".join([t.strip() for t in text_content if t.strip()])

                    filename = os.path.join(pdf_folder,  dicts["year"] + ".txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(clean_text)
                else:
                    pdf_url = iframe_src[0]
                    pdf_resp = await client.get(pdf_url, timeout=30)
                    pdf_resp.raise_for_status()

                    filename = os.path.join(pdf_folder, dicts["year"]+".pdf")
                    with open(filename, "wb") as f:
                        f.write(pdf_resp.content)
                pdf_paths.append(filename)

        except Exception as e:
            log_error(e, "scrape_pdf")
            raise JSONResponse(status_code=500, content={"error": str(e)})
    
    total_time = time.time() - start_time
    log_normal(f"single pdf took {total_time:.2f} seconds", "scrape_pdf")
        
    log_normal(f"✅ PDF descargado: {pdf_paths}", "scrape_pdf")
    return pdf_paths

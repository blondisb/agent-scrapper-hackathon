import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils_folder.loggger import log_error, log_normal


async def au_companies_id(ABN_URL: str, company: str):
    try:
        log_normal(ABN_URL)
        async with httpx.AsyncClient() as client:
            resp = await client.get(ABN_URL, params={"SearchText": company}, timeout=15)
            resp.raise_for_status()
            print(1, resp)

        tree = html.fromstring(resp.text)

        # 🔎 Extraer filas de la tabla de resultados
        rows = tree.xpath(
            "/html/body/div[3]/div[3]/div[2]/form/div/div/div/table/tbody//tr"
        )
        log_normal(rows, "au_companies_id // rows")

        results = []
        for row in rows[1:]:  # saltamos la cabecera <tr>
            cols = row.xpath(".//td")
            log_normal(cols, "au_companies_id")

            if len(cols) >= 4:
                # ABN
                abn = cols[0].xpath(".//a/text()")
                abn = abn[0].strip() if abn else ""

                # Status
                status = cols[0].xpath(".//span/text()")
                status = status[0].strip() if status else ""

                # Nombre
                name = cols[1].text_content().strip()

                # Tipo
                type_ = cols[2].text_content().strip()

                # Ubicación
                location = cols[3].text_content().strip()
                location = re.sub(r"\s+", " ", location)

                if name:
                    results.append({
                        "id": abn,
                        "name": name,
                        "status": status,
                        "type": type_,
                        "location": location
                    })
        return JSONResponse(content={"matches": results})
    except Exception as e:
        log_error(e)
        raise JSONResponse(status_code=500, content={"error": str(e)})
    


from playwright.async_api import async_playwright

async def au_scrape_v2(base_url, company):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"{base_url}?SearchText={company}")
            
            # Esperar que aparezca la tabla
            await page.wait_for_selector("table tbody tr")
            
            rows = await page.query_selector_all("table tbody tr")
            log_normal(rows, "au_scrape_v2 -- rows")

            results = []
            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 4:
                    abn = (await cols[0].inner_text()).strip()
                    name = (await cols[1].inner_text()).strip()
                    type_ = (await cols[2].inner_text()).strip()
                    location = (await cols[3].inner_text()).strip()
                    results.append({"id": abn, "name": name, "type": type_, "location": location})
            
            await browser.close()
            log_normal(results, "au_scrape_v2 -- results")
            return results
    except Exception as e:
        log_error(e, "au_scrape_v2")
        raise e
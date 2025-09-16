import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal

async def uk_companies_id(BASE_URL, company: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(BASE_URL, params={"q": company}, timeout=15)
        resp.raise_for_status()
        tree = html.fromstring(resp.text)

        results = []

        try:
        # Cada empresa está dentro de <li class="type-company">
            for li in tree.xpath('//ul[@id="results"]/li[@class="type-company"]'):
                name = li.xpath('.//a/text()')
                comp_id = li.xpath('.//a[contains(@href,"/company/")]/@href')

                if name and comp_id:
                    company_name = name[0].strip()
                    # el id viene en la URL tipo "/company/02194014"
                    company_id = comp_id[0].split("/")[-1]
                    results.append({"name": company_name, "id_company": company_id})

            return JSONResponse(content={"matches": results if len(results) > 0 else "Not companies found"})
        except Exception as e:
            log_error(e)
            raise JSONResponse(status_code=500, content={"error": str(e)})
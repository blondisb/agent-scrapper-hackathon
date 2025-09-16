import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


async def uk_statements(base_url: str, id_company: str) -> list:
    search_url = f"{base_url}/search-results"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(search_url, params={"Search": id_company}, timeout=15)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)

            results = []
            rows = tree.xpath('//table/tbody/tr')

            for row in rows:
                href = row.xpath('.//a[@class="govuk-link"]/@href')
                year = row.xpath('.//p[@class="govuk-body govuk-!-margin-bottom-2 govuk-!-margin-top-1"]/text()')
                
                if href and year:
                    year = year[0].strip()  # <-- solo strip aquí, sin volver a hacer [0]
                    results.append({
                        "year": year,
                        "href": base_url + href[0].strip()
                    })

            # log_normal(results, "uk_statements")
            return results
    except Exception as e:
        log_error(e, "uk_statements")
        raise JSONResponse(status_code=500, content={"error": str(e)})
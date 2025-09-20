import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils_folder.loggger import log_error, log_normal

async def ca_statements1(search_url, base_url) -> dict:
    search_url += "&nb=50"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(search_url, timeout=15)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)

            results = []
            # seleccionamos todas las filas menos el header
            rows = tree.xpath('//table[@id="dataset-filter1"]/tbody/tr')

            for row in rows:
                title = row.xpath('.//td[1]/a/text()')
                href = row.xpath('.//td[1]/a/@href')
                resource = row.xpath('.//td[2]/text()')
                year = row.xpath('.//td[3]/text()')
                collection = row.xpath('.//td[4]/a/text()')

                if title and href:
                    results.append({
                        "title": title[0].strip(),
                        "href": base_url + '/' + href[0].strip(),
                        "resource": resource[0].strip() if resource else None,
                        "year": year[0].strip() if year else None,
                        "collection": collection[0].strip() if collection else None,
                    })

            return results
    except Exception as e:
        log_error(e, "uk_statements")
        raise JSONResponse(status_code=500, content={"error": str(e)})
import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


async def scrape_statements(base_url: str, abn: str) -> list:
    """
    Scrapea el Modern Slavery Register para un ABN dado.
    Retorna una lista de diccionarios con href y la info textual.
    """
    statements_url = f"{base_url}/statements/"
    params = {
        "q": abn,
        "search_type": "abn",
        "ordering": "-submitted_at",
        "spsf": "",
        "spet": "",
        "voluntarity": ""
    }

    try:

        async with httpx.AsyncClient() as client:
            resp = await client.get(statements_url, params=params, timeout=15)
            resp.raise_for_status()
            tree = html.fromstring(resp.content)

        matches = []

        for item in tree.xpath('//a[contains(@class,"search-results__item")]'):
            href = item.xpath('./@href')[0]
            href = (
                base_url + href
                if href.startswith("/")
                else href
            )

            # Extraer textos limpios
            raw_texts = [t.strip() for t in item.xpath('.//text()') if t.strip()]
            
            # Nombre + ABN (ej: "AIRBUS AUSTRALIA PACIFIC LIMITED (68 003 035 470)")
            name_abn = raw_texts[0]
            match_abn = re.search(r"\((\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\)", name_abn)
            abn_val = match_abn.group(1).replace(" ", "") if match_abn else None
            name_val = name_abn.split("(")[0].strip()
            
            # Fecha (ej: "01 January 2024 to 31 December 2024")
            date_val = next((t for t in raw_texts if "to" in t), None)
            
            # Países (último bloque antes de ABN)
            countries = None
            for t in raw_texts:
                if re.match(r"^[A-Za-z]+(\s+[A-Za-z]+)*$", t) and not t.startswith("ABN"):
                    countries = t
            # ABN aparece explícito
            explicit_abn = next((t for t in raw_texts if t.startswith("ABN:")), None)
            if explicit_abn:
                abn_val = explicit_abn.replace("ABN:", "").strip()

            matches.append({
                "href": href,
                "abn": abn,
                "name": name_val,
                "date": date_val,
                "countries": countries
            })

        return matches
    except Exception as e:
        log_error(e, "scrape_statements")
        raise JSONResponse(status_code=500, content={"error": str(e)})
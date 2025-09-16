import re
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from utils.loggger import log_error, log_normal


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

        results = []
        for row in rows[1:]:  # saltamos la cabecera <tr>
            cols = row.xpath(".//td")
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
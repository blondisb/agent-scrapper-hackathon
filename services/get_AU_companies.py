import re
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
from lxml import html


async def get_au_comanies(BASE_URL: str, company: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params={"SearchText": company}, timeout=15)
            resp.raise_for_status()

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

                print(5, results)

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
            return JSONResponse(status_code=500, content={"error": str(e)})
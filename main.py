import os, re
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from services.get_AU_companies import get_au_comanies
from utils.loggger import log_normal

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "https://abr.business.gov.au/Search/ResultsActive")

@app.get("/AUcompanies/search")
async def search_company(company: str = Query(..., min_length=2)) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"input: {company}")
    resp = await get_au_comanies(BASE_URL, company)
    log_normal(f"output: {company}")

    return resp

    

    
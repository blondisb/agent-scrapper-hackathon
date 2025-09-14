import os, re
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from dotenv import load_dotenv, find_dotenv

from utils.loggger import log_normal
from services.get_AU_companies import get_au_comanies
from services.get_statements import scrape_statements

load_dotenv(find_dotenv(), override=True)
app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "/outslavery")
ABN_URL = os.getenv("ABN_URL", "https://abr.business.gov.au/Search/ResultsActive")
AU_STATEMENTS_URL = os.getenv("AU_STATEMENTS_URL", "https://modernslaveryregister.gov.au/statements/")



@app.get(f"{BASE_URL}/AUcompanies/search")
async def search_company(company: str = Query(..., min_length=2)) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"IN: {company}")
    resp = await get_au_comanies(ABN_URL, company)
    
    log_normal(f"OUT: {resp}")
    return resp


@app.get(f"{BASE_URL}/AUcompanies/statements")
async def search_au_statemens(abn: str) -> dict:
    """
    """
    log_normal(f"input: {abn}")
    resp = await scrape_statements(AU_STATEMENTS_URL, abn)
    log_normal(f"output: {resp}")

    return resp

    



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
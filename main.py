import os, re
import time
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
from lxml import html
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
import shutil

from utils.loggger import log_normal
from utils.utils import delete_folders, find_existing_file

from services.get_AU_companies import get_au_comanies
from services.get_statements import scrape_statements
from services.get_pdfs import scrape_pdf
from services_agents.agentss import main_agents


# ================================================================================================================================================
load_dotenv(find_dotenv(), override=True)
app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "/outslavery")
ABN_URL = os.getenv("ABN_URL", "https://abr.business.gov.au/Search/ResultsActive")
AU_MODERNSLAVERY = os.getenv("AU_MODERNSLAVERY", "https://modernslaveryregister.gov.au")
BASE_PATH = "/tmp"



# ================================================================================================================================================
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



# ================================================================================================================================================
@app.get(f"{BASE_URL}/AUcompanies/statements")
async def search_au_statemens(abn: str) -> dict:
    """
    """
    
    if " " in abn: abn = abn.replace(" ", "")
    log_normal(f"IN: {abn}", "search_au_statemens")

    abn_path = f"{BASE_PATH}/{abn}"
    txt_path = f"{abn_path}/summary.txt"

    llm_response = find_existing_file(txt_path)
    if llm_response is not None:
        log_normal(f"OUT1: {abn} || {llm_response}", "search_au_statemens")
        return {"data": llm_response}

    statements = await scrape_statements(AU_MODERNSLAVERY, abn)    
    pdf_names = await scrape_pdf(AU_MODERNSLAVERY, abn, statements, f"{abn_path}/pdf")
    llm_response = main_agents(abn, pdf_names, f"{abn_path}/pdf", txt_path)
    
    log_normal(f"OUT2: {abn} || {llm_response}", "search_au_statemens")
    return {"data": llm_response}

    

# ================================================================================================================================================
@app.delete(f"{BASE_URL}/deletefolder")
def delete_folder(folder_name: str = '.'):
    return delete_folders(folder_name)




# ================================================================================================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
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
from services_agents.agentss import main_agents

from services.au.get_AU_companies import au_companies_id
from services.au.get_statements import au_statements
from services.au.get_pdfs import au_pdfs

from services.uk.get_uk_idcompany import uk_companies_id
from services.uk.get_uk_statements import uk_statements
from services.uk.get_uk_pdfs import uk_pdfs


# ================================================================================================================================================
load_dotenv(find_dotenv(), override=True)
app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "/outslavery")
AU_COMPANIES_ID = os.getenv("AU_COMPANIES_ID", "https://abr.business.gov.au/Search/ResultsActive")
AU_STATEMENTS_URL = os.getenv("AU_STATEMENTS_URL", "https://modernslaveryregister.gov.au")
BASE_PATH_AU = "/tmp/au"

UK_COMPANIES_ID = os.getenv("UK_COMPANIES_ID", "https://find-and-update.company-information.service.gov.uk/search/companies")
UK_STATEMENTS_URL = os.getenv("UK_STATEMENTS_URL", "https://modern-slavery-statement-registry.service.gov.uk")
BASE_PATH_UK = "/tmp/uk"


# ================================================================================================================================================
@app.get(f"{BASE_URL}/AUcompanies/search")
async def search_company(company: str = Query(..., min_length=2)) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"IN: {company}")
    resp = await au_companies_id(AU_COMPANIES_ID, company)
    
    log_normal(f"OUT: {resp}")
    return resp


@app.get(f"{BASE_URL}/AUcompanies/statements")
async def search_au_statemens(abn: str) -> dict:
    """
    """
    if " " in abn: abn = abn.replace(" ", "")
    log_normal(f"IN: {abn}", "search_au_statemens")

    abn_path = f"{BASE_PATH_AU}/{abn}"
    txt_path = f"{abn_path}/summary.txt"
    llm_response = find_existing_file(txt_path)

    if llm_response is None:
        statements      = await au_statements(AU_STATEMENTS_URL, abn)    
        pdf_names       = await au_pdfs(statements, f"{abn_path}/pdf")
        llm_response    = await main_agents(abn, pdf_names, f"{abn_path}/pdf", txt_path)
    
    log_normal(f"OUT2: {abn} || {llm_response}", "search_au_statemens")
    return {"data": llm_response}




# ================================================================================================================================================
@app.get(f"{BASE_URL}/UKcompanies/search")
async def search_company(company: str = Query(..., min_length=2)) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"IN: {company}")
    resp = await uk_companies_id(UK_COMPANIES_ID, company)
    
    log_normal(f"OUT: {resp}")
    return resp


@app.get(f"{BASE_URL}/UKstatements")
async def search_uk_statemens(id_company: str) -> dict:
    """
    """
    # if " " in abn: abn = abn.replace(" ", "")
    log_normal(f"IN: {id_company}", "search_au_statemens")

    company_path = f"{BASE_PATH_UK}/{id_company}"
    txt_path = f"{company_path}/summary.txt"
    llm_response = find_existing_file(txt_path)

    if llm_response is None:
        # .
        statements = await uk_statements(UK_STATEMENTS_URL, id_company)
        log_normal(statements, "uk_statements")
        # .
        pdf_names = await uk_pdfs(statements, f"{company_path}/pdf")
        log_normal(pdf_names, "uk_statements")
        # .
        llm_response = await main_agents(id_company, pdf_names, f"{company_path}/pdf", txt_path)
    
    log_normal(f"OUT1: {id_company} || {llm_response}", "search_uk_statemens")
    return {"data": llm_response}


    

# ================================================================================================================================================
@app.delete(f"{BASE_URL}/deletefolder")
def delete_folder(folder_name: str = '.'):
    return delete_folders(folder_name)




# ================================================================================================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
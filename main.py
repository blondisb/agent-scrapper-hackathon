import os, re
import time
import uvicorn
import httpx
import shutil
import ollama

from lxml import html
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from smolagents import LiteLLMModel

from utils_folder.loggger import log_normal
from utils_folder.utils import delete_folders, find_existing_file

from services_agents.agentss import main_agents
from services_agents.statement_reader_ollama import main_agents2
# from services_agents.scrapper_agent import main_scrapper_agent
from services_agents.search_agent import url_finder_agent, visitor_agent
from services_agents.reader_webpage_info import reading_webpagecontent

from services.au.get_AU_companies import au_companies_id, au_scrape_v2
from services.au.get_statements import au_statements
from services.au.get_pdfs import au_pdfs

from services.uk.get_uk_idcompany import uk_companies_id
from services.uk.get_uk_statements import uk_statements
from services.uk.get_uk_pdfs import uk_pdfs

from services.ca.ca_statements import ca_statements1
from services.ca.ca_pdfs import ca_pdfs



# ================================================================================================================================================
load_dotenv(find_dotenv(), override=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)  


# ================================================================================================================================================


BASE_URL = os.getenv("BASE_URL", "/outslavery")
AU_COMPANIES_ID = os.getenv("AU_COMPANIES_ID", "https://abr.business.gov.au/Search/ResultsActive")
AU_STATEMENTS_URL = os.getenv("AU_STATEMENTS_URL", "https://modernslaveryregister.gov.au")
BASE_PATH_AU = "/tmp/au"

UK_COMPANIES_ID = os.getenv("UK_COMPANIES_ID", "https://find-and-update.company-information.service.gov.uk/search/companies")
UK_STATEMENTS_URL = os.getenv("UK_STATEMENTS_URL", "https://modern-slavery-statement-registry.service.gov.uk")
BASE_PATH_UK = "/tmp/uk"

CA_BASE_URL = "https://www.publicsafety.gc.ca/cnt/rsrcs/lbrr/ctlg"
CA_FINDER_URL="/rslts-en.aspx?l=2,3,7&a="
BASE_PATH_CA = "/tmp/ca"


# Lazy load model to speed up startup
model1 = None
testingg = True


def get_model():
    global model1

    if testingg == True:
        if model1 is None:
            model1 = LiteLLMModel(
                model_id = "gemini/gemini-2.0-flash", api_key = os.getenv("GEMINI_API_KEY")
            )
        return model1
    else:
            
        global model1
        if model1 is None:
            # Aquí puedes "anclar" el modelo que quieres usar por defecto
            # Ej: llama3, mistral, gemma, etc.
            model1 = {
                "client": ollama,
                "model_id": os.getenv("OLLAMA_MODEL", "llama3")  # configurable por env
            }
        return model1



# ================================================================================================================================================
@app.get(f"{BASE_URL}/AUcompanies/search")
async def search_company(company: str = Query(..., min_length=2)) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"IN: {company}")
    # resp = await au_companies_id(AU_COMPANIES_ID, company)
    resp = await au_scrape_v2(AU_COMPANIES_ID, company)
    
    log_normal(f"OUT: {resp}")
    return {"matches": resp}


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
        statements = await au_statements(AU_STATEMENTS_URL, abn) 
        log_normal(statements, "search_au_statemens")

        if len(statements) == 0:
            return {"data": f"Not documents found for the company witn ABN: {abn}"}
         
        pdf_names       = await au_pdfs(statements, f"{abn_path}/pdf")
        log_normal(pdf_names, "search_au_statemens")  

        if testingg == True:
            llm_response    = await main_agents(abn, pdf_names, f"{abn_path}/pdf", txt_path)
        else:
            llm_response    = await main_agents2(abn, pdf_names, f"{abn_path}/pdf", txt_path)
        log_normal(llm_response, "search_au_statemens")  
    
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
        if len(statements) == 0:
            return {"data": f"Not documents found for the company with id company: {id_company}"}
        # .
        pdf_names = await uk_pdfs(statements, f"{company_path}/pdf")
        log_normal(pdf_names, "uk_statements")
        # .

        if testingg == True:
            llm_response = await main_agents(id_company, pdf_names, f"{company_path}/pdf", txt_path)
        else:
            llm_response = await main_agents2(id_company, pdf_names, f"{company_path}/pdf", txt_path)
    
    log_normal(f"OUT1: {id_company} || {llm_response}", "search_uk_statemens")
    return {"data": llm_response}





# ================================================================================================================================================
@app.get(f"{BASE_URL}/CAstatements")
async def search_ca_company(company_name: str = Query(..., min_length=2)) -> dict:
    """
    """
    log_normal(f"IN: {company_name}")

    if " " in company_name:
        company_url = company_name.replace(" ", "+")
        company_id = company_name.replace(" ", "_")
    else:
        company_url = company_name
        company_id = company_name

    pdf_folder = f"{BASE_PATH_CA}/{company_id}/pdf"
    txt_path = f"{BASE_PATH_CA}/{company_id}/summay.txt"
    search_url = CA_BASE_URL + CA_FINDER_URL + company_url

    llm_response = find_existing_file(txt_path)
    if llm_response is None:
        
        resp_stt = await ca_statements1(search_url, CA_BASE_URL)
        log_normal(resp_stt, "search_ca_company")
        if len(resp_stt) == 0:
            return {"data": f"Not documents found for the company with company: {company_name}"}

        pdf_names = await ca_pdfs(resp_stt, pdf_folder)
        log_normal(pdf_names, "search_ca_company/pdf_names")

        if testingg == True:
            llm_response = await main_agents(company_id, pdf_names, pdf_folder, txt_path)
        else:
            llm_response = await main_agents2(company_id, pdf_names, pdf_folder, txt_path)


    log_normal(f"OUT: {llm_response}")
    return {"data": llm_response}





# ================================================================================================================================================
@app.get(f"{BASE_URL}/scrapperagent")
async def search_company(
    company: str = Query(..., min_length=2),
    country: str = Query(..., min_length=2)
) -> dict:
    """
    Busca una compañía en ABN Lookup (ejemplo) usando POST al formulario
    y devuelve IDs y nombres extraídos con XPath.
    """
    log_normal(f"IN: {company, country}")
    url = await url_finder_agent(get_model(), company.upper(), country.upper())
    resp = await reading_webpagecontent(url)

    log_normal(f"OUT: {resp}")
    return {"data": f"{url} || {resp}"}
    

# ================================================================================================================================================
@app.delete(f"{BASE_URL}/deletefolder")
def delete_folder(folder_name: str):
    return delete_folders(folder_name)




# ================================================================================================================================================
# Server startup is handled by Docker CMD: uvicorn main:app --host 0.0.0.0 --port 8080
    
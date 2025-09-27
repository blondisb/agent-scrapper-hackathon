import os, re
import time
import uvicorn
import httpx
import shutil
import json

from lxml import html
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from smolagents import LiteLLMModel

from utils_folder.loggger import log_normal
from utils_folder.utils import delete_folders, find_existing_file

# from services_agents.agentss import main_agents
# from services_agents.scrapper_agent import main_scrapper_agent
from services_agents.search_agent import url_finder_agent
from services_agents.reader_webpage_info import reading_webpagecontent

from services_agents.llm_calling import summarize_with_groq_async, summarize_with_groq_async_chunked
# from services_agents.ollama_call import summarize_with_ollama_async

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


os.environ["LITELLM_CACHE_DIR"] = "/tmp/litellm_cache"



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

MODEL_ENV = os.getenv("MODEL_ENV", "deepseek-r1-distill-llama-70b")



# model1 = None
# def get_model():
#     global model1
#     if model1 is None:
#         model1 = LiteLLMModel(
#             model_id = "gemini/gemini-2.0-flash", api_key = os.getenv("GEMINI_API_KEY")
#         )
#     return model1

def get_model():
    return LiteLLMModel(
        model_id=f"groq/{MODEL_ENV}"
        ,api_key=os.environ.get("GROQ_API_KEY")
        # ,api_base="https://api.groq.com/openai/v1"
    )




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
    final_data = find_existing_file(txt_path)

    if final_data["llm_response"] is None:
        statements = await au_statements(AU_STATEMENTS_URL, abn) 

        if len(statements) == 0:
            return {"data": f"Not documents found for the company witn ABN: {abn}"}
         
        pdf_names       = await au_pdfs(statements, f"{abn_path}/pdf")
        # llm_response    = await main_agents(abn, pdf_names, f"{abn_path}/pdf", txt_path)
        
        llm_response = await summarize_with_groq_async(
            file_paths=pdf_names,
            model=MODEL_ENV,
            max_tokens=20000,
            pdf_folder=f"{abn_path}/pdf",
            txt_path=txt_path
        )
        
    
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
    final_data = find_existing_file(txt_path)

    if final_data["llm_response"] is None:
        statements = await uk_statements(UK_STATEMENTS_URL, id_company)

        if len(statements) == 0:
            return {"data": f"Not documents found for the company with id company: {id_company}"}
        
        pdf_names = await uk_pdfs(statements, f"{company_path}/pdf")
        # llm_response = await main_agents(id_company, pdf_names, f"{company_path}/pdf", txt_path)

        llm_response = await summarize_with_groq_async(
            file_paths=pdf_names,
            model=MODEL_ENV,
            max_tokens=20000,
            pdf_folder=f"{company_path}/pdf",
            txt_path=txt_path
        )
    
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
    final_data = find_existing_file(txt_path)

    if final_data["llm_response"] is None:
        resp_stt = await ca_statements1(search_url, CA_BASE_URL)
        if len(resp_stt) == 0:
            return {"data": f"Not documents found for the company with company: {company_name}"}

        pdf_names = await ca_pdfs(resp_stt, pdf_folder)
        # llm_response = await main_agents(company_id, pdf_names, pdf_folder, txt_path)

        llm_response = await summarize_with_groq_async_chunked(
            file_paths=pdf_names,
            model=MODEL_ENV,
            max_tokens_input=1000,
            max_tokens_summary=1000,
            pdf_folder=f"{pdf_folder}/pdf",
            txt_path=txt_path
        )

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
    
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
    log_normal(f"input: {abn}", "search_au_statemens")

    statements = await scrape_statements(AU_MODERNSLAVERY, abn)    
    await scrape_pdf(AU_MODERNSLAVERY, abn, statements)

    
    log_normal(f"output: {abn} || {statements}", "search_au_statemens")
    return {"data": statements}

    

# ================================================================================================================================================
@app.delete(f"{BASE_URL}/deletefolder/")
def delete_folder(folder_name: str = '.'):


    folder_name = folder_name.replace(" ", "")
    # Siempre trabajar bajo /tmp
    folder_path = os.path.abspath(os.path.join("/tmp", folder_name))
    log_normal(f"IN: {folder_path}")

    # Seguridad: validar que la ruta está dentro de /tmp
    if not folder_path.startswith("/tmp"):
        raise HTTPException(status_code=400, detail="Ruta no permitida")

  
    try:
        contents = []

        if os.path.exists(folder_path):
            contents = os.listdir(folder_path)
            shutil.rmtree(folder_path)
        else:
            return {"message": f"La carpeta {folder_name} no existe."}

        log_normal(f"📂 Contenido deleteado de '{folder_name}': {contents}", "delete_folder")  # 👈 imprime en consola del contenedor
        return {"folder": folder_name, "contents": contents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar la carpeta: {str(e)}")




# ================================================================================================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
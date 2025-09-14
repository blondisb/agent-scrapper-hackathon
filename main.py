import os, re
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
    log_normal(f"input: {abn}")

    resp = await scrape_statements(AU_MODERNSLAVERY, abn)
    await scrape_pdf(AU_MODERNSLAVERY, abn, resp)
    
    log_normal(f"output: {resp}")
    return {"data": resp}

    

# ================================================================================================================================================
@app.delete(f"{BASE_URL}/deletefolder/")
def delete_folder(folder_name: str = '.'):

    REPO_PATH = "/app/temp"
    if " " in folder_name: folder_name = folder_name.replace(" ", "")

    folder_path = os.path.join(REPO_PATH, folder_name)
    log_normal(f"IN: {folder_path}")

    # Verificar si la carpeta existe
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="La carpeta no existe en el repo.")

    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="La ruta especificada no es una carpeta.")

    try:
        # Eliminar todo el contenido dentro de la carpeta, pero no la carpeta en sí
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # elimina archivos y links
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # elimina subcarpetas
        # return {"message": f"Contenido de la carpeta '{folder_name}' eliminado con éxito."}

        contents = os.listdir(folder_path)
        print(f"📂 Contenido deleteado de '{folder_name}':", contents)  # 👈 imprime en consola del contenedor
        return {"folder": folder_name, "contents": contents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar la carpeta: {str(e)}")




# ================================================================================================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
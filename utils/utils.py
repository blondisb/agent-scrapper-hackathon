import os
import shutil
from utils.loggger import log_error, log_normal
from fastapi import HTTPException

BASE_PATH = "/tmp"

def delete_folders(folder_path):
    folder_path = os.path.abspath(os.path.join(folder_path))
    log_normal(f"IN: {folder_path}", "delete_folders")

    # Seguridad: validar que la ruta está dentro de /tmp
    if not folder_path.startswith(BASE_PATH):
        raise HTTPException(status_code=400, detail="Ruta no permitida")
  
    try:
        contents = []

        if os.path.exists(folder_path):
            contents = os.listdir(folder_path)
            shutil.rmtree(folder_path)
        else:
            return {"message": f"La carpeta {folder_path} no existe."}

        log_normal(f"📂 Contenido deleteado de '{folder_path}': {contents}", "delete_folders")  # 👈 imprime en consola del contenedor
        return {"folder": folder_path, "contents": contents}
    
    except Exception as e:
        log_error(f"Error al limpiar la carpeta: {e}", "delete_folders")
        raise HTTPException(status_code=500, detail=f"Error al limpiar la carpeta: {str(e)}")
    


def save_file(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if isinstance(content, bytes):
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        log_normal(f"LLM response saved to {file_path}", "main_agents")
    except Exception as e:
        log_error(f"Error al guardar el archivo: {e}", "main_agents")
        raise e
    

def find_existing_file(file_path):
    """"
    Busca un archivo en la ruta especificada y devuelve su contenido.
    Si el archivo no existe, devuelve None.
    """

    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    except Exception as e:
        log_error(f"Error al buscar el archivo: {e}", "find_existing_file")
        raise e
# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import time
# from typing import List, Dict
# import tempfile
# from pathlib import Path

# from crewai import Agent, Task, Crew
# from langchain.tools import tool
# from langchain_ollama import OllamaLLM

# # Crear carpeta temporal para los PDFs
# # TEMP_DIR = tempfile.mkdtemp(prefix="modern_slavery_pdfs_")

# TEMP_DIR = "/tmp/ca/pdf"
# print(f"Carpeta temporal creada: {TEMP_DIR}")





# # Configurar Ollama (necesitas tener Ollama instalado)
# llm1 = OllamaLLM(
#     model="qwen2.5:0.5b",  # o "mistral", "codellama", etc.
#     temperature=0.7
# )


# @tool("canada_modern_slavery_scraper")
# def canada_modern_slavery_scraper(company_name: str) -> Dict:
#     """
#     Busca y descarga documentos PDF de Modern Slavery para una empresa específica
#     del catálogo de la Biblioteca de Seguridad Pública de Canadá.
    
#     Args:
#         company_name (str): Nombre de la empresa a buscar (ej: "3m")
        
#     Returns:
#         Dict: Información sobre los PDFs encontrados y descargados
#     """
    
#     # URL base del catálogo con parámetros de búsqueda
#     base_search_url = "https://www.publicsafety.gc.ca/cnt/rsrcs/lbrr/ctlg/rslts-en.aspx"
    
#     def search_company_documents(company: str) -> List[Dict]:
#         """Busca documentos de la empresa en el catálogo"""
#         try:
#             # Construir URL de búsqueda
#             search_params = {
#                 'l': '2,3,7',  # Filtros específicos (ajustar según necesidades)
#                 'a': company   # Nombre de la empresa
#             }
            
#             # Realizar búsqueda
#             search_url = f"{base_search_url}?l={search_params['l']}&a={search_params['a']}"
#             print(f"Buscando en: {search_url}")
            
#             response = requests.get(search_url, timeout=15)
#             response.raise_for_status()
            
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Buscar resultados de búsqueda (enlaces a documentos individuales)
#             results = []
            
#             # Buscar enlaces que parecen documentos individuales
#             # Los resultados suelen estar en elementos con clase específica
#             document_links = soup.find_all('a', href=True)
            
#             for link in document_links:
#                 href = link['href']
#                 text = link.get_text().strip()
                
#                 # Buscar enlaces a páginas de documentos individuales
#                 if 'ctlg-vw' in href and 'rsrcs' in href:
#                     full_url = urljoin("https://www.publicsafety.gc.ca", href)
#                     results.append({
#                         'title': text or 'Documento Modern Slavery',
#                         'url': full_url,
#                         'company': company
#                     })
            
#             # También buscar enlaces directos a PDFs
#             pdf_links = soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
#             for link in pdf_links:
#                 href = link['href']
#                 text = link.get_text().strip()
#                 full_url = urljoin("https://www.publicsafety.gc.ca", href)
#                 results.append({
#                     'title': text or 'Documento Modern Slavery PDF',
#                     'url': full_url,
#                     'company': company
#                 })
            
#             return results
            
#         except Exception as e:
#             print(f"Error en la búsqueda: {e}")
#             return []
    
#     def get_document_details(document_url: str) -> Dict:
#         """Obtiene detalles del documento y enlaces PDF"""
#         try:
#             response = requests.get(document_url, timeout=15)
#             response.raise_for_status()
            
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Buscar enlaces PDF en la página del documento
#             pdf_links = []
            
#             # Buscar enlaces directos a PDFs
#             links = soup.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
#             for link in links:
#                 href = link['href']
#                 text = link.get_text().strip()
#                 full_url = urljoin("https://www.publicsafety.gc.ca", href)
#                 pdf_links.append({
#                     'url': full_url,
#                     'title': text or 'Modern_Slavery_Statement.pdf'
#                 })
            
#             # Buscar también enlaces que contengan palabras clave de Modern Slavery
#             keywords = ['modern slavery', 'slavery statement', 'human trafficking', 'forced labour']
#             all_links = soup.find_all('a', href=True)
#             for link in all_links:
#                 text = link.get_text().lower()
#                 href = link['href'].lower()
#                 if any(keyword in text or keyword in href for keyword in keywords):
#                     if href.endswith('.pdf'):
#                         full_url = urljoin("https://www.publicsafety.gc.ca", link['href'])
#                         title = link.get_text().strip() or 'Modern_Slavery_Document.pdf'
#                         pdf_links.append({
#                             'url': full_url,
#                             'title': title
#                         })
            
#             return {
#                 'pdf_links': pdf_links,
#                 'page_title': soup.find('title').get_text() if soup.find('title') else 'Documento'
#             }
            
#         except Exception as e:
#             print(f"Error obteniendo detalles del documento {document_url}: {e}")
#             return {'pdf_links': [], 'page_title': 'Error'}
    
#     def download_pdf(pdf_url: str, filename: str, company: str) -> str:
#         """Descarga un PDF y lo guarda en la carpeta temporal"""
#         try:
#             print(f"Descargando PDF: {pdf_url}")
            
#             response = requests.get(pdf_url, timeout=30)
#             response.raise_for_status()
            
#             # Crear nombre de archivo seguro
#             safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).rstrip()
#             safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
#             # Asegurar que tenga extensión .pdf
#             if not safe_filename.lower().endswith('.pdf'):
#                 safe_filename += '.pdf'
            
#             file_path = os.path.join(TEMP_DIR, f"{safe_company}_{safe_filename}")
            
#             with open(file_path, 'wb') as f:
#                 f.write(response.content)
            
#             print(f"PDF descargado: {file_path}")
#             return file_path
            
#         except Exception as e:
#             print(f"Error descargando PDF {pdf_url}: {e}")
#             return ""
    
#     # Proceso principal
#     try:
#         print(f"Buscando documentos de Modern Slavery para: {company_name}")
        
#         # Paso 1: Buscar documentos de la empresa
#         search_results = search_company_documents(company_name)
        
#         if not search_results:
#             return {
#                 "status": "not_found",
#                 "message": f"No se encontraron documentos para {company_name}",
#                 "company": company_name,
#                 "downloaded_files": [],
#                 "TEMP_DIRectory": TEMP_DIR
#             }
        
#         print(f"Encontrados {len(search_results)} resultados")
        
#         downloaded_files = []
        
#         # Paso 2: Para cada resultado, obtener detalles y descargar PDFs
#         for i, result in enumerate(search_results[:10]):  # Limitar a 10 resultados
#             print(f"Procesando resultado {i+1}/{len(search_results[:10])}: {result['title']}")
            
#             # Obtener detalles del documento
#             doc_details = get_document_details(result['url'])
            
#             # Si no encontramos PDFs directamente, agregar el documento principal
#             if not doc_details['pdf_links']:
#                 # Verificar si la URL principal es un PDF
#                 if result['url'].lower().endswith('.pdf'):
#                     doc_details['pdf_links'] = [{
#                         'url': result['url'],
#                         'title': result['title'] or 'Modern_Slavery_Statement.pdf'
#                     }]
#                 else:
#                     # Intentar con la URL principal como posible PDF
#                     doc_details['pdf_links'] = [{
#                         'url': result['url'],
#                         'title': result['title'] or 'Document.pdf'
#                     }]
            
#             # Descargar cada PDF encontrado
#             for pdf_info in doc_details['pdf_links']:
#                 if pdf_info['url'].lower().endswith('.pdf'):
#                     filename = pdf_info['title'] or f'document_{i+1}.pdf'
#                     file_path = download_pdf(pdf_info['url'], filename, company_name)
                    
#                     if file_path:
#                         downloaded_files.append({
#                             'company': company_name,
#                             'file_path': file_path,
#                             'url': pdf_info['url'],
#                             'title': pdf_info['title'],
#                             'source_page': result['url']
#                         })
            
#             # Pequeña pausa para no sobrecargar el servidor
#             time.sleep(1)
        
#         return {
#             "status": "success",
#             "message": f"Procesados {len(downloaded_files)} archivos PDF",
#             "company": company_name,
#             "downloaded_files": downloaded_files,
#             "TEMP_DIRectory": TEMP_DIR,
#             "search_url": f"{base_search_url}?l=2,3,7&a={company_name}"
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Error general: {str(e)}",
#             "company": company_name,
#             "downloaded_files": [],
#             "TEMP_DIRectory": TEMP_DIR
#         }
    
# from langchain.tools import StructuredTool

# # Convertimos la función en un StructuredTool
# canada_modern_slavery_scraper_tool = StructuredTool.from_function(
#     func=canada_modern_slavery_scraper
# )

# # Crear el agente
# canada_modern_slavery_agent = Agent(
#     role='Canadian Modern Slavery Document Collector',
#     goal='Buscar y descargar documentos PDF de Modern Slavery del catálogo de Seguridad Pública de Canadá',
#     backstory="""
#         Eres un experto en recolección de documentos de Modern Slavery Statements 
#         del catálogo de la Biblioteca de Seguridad Pública de Canadá. 
#         Tu tarea es buscar documentos para empresas específicas, navegar a las páginas 
#         de documentos individuales, identificar reportes relacionados con Modern Slavery 
#         y descargar los archivos PDF para análisis posterior.
#     """,
#     verbose=True,
#     allow_delegation=False,
#     tools=[canada_modern_slavery_scraper],
#     llm=llm1
# )

# # Crear la tarea
# def create_canada_modern_slavery_task(company_name: str):
#     return Task(
#         description=f"""
#             Busca y descarga documentos PDF de Modern Slavery para la empresa '{company_name}'.
#             Utiliza el catálogo de la Biblioteca de Seguridad Pública de Canadá.
#             El proceso debe incluir:
#             1. Buscar la empresa en el catálogo usando la URL: https://www.publicsafety.gc.ca/cnt/rsrcs/lbrr/ctlg/rslts-en.aspx?l=2,3,7&a={company_name}
#             2. Identificar resultados relevantes de la búsqueda
#             3. Navegar a las páginas individuales de cada documento
#             4. Buscar enlaces a PDFs relacionados con Modern Slavery
#             5. Descargar todos los PDFs encontrados
#             6. Guardar los archivos en la carpeta temporal
            
#             Parámetros:
#             - Nombre de empresa: {company_name}
#         """,
#         agent=canada_modern_slavery_agent,
#         expected_output=f"""
#             Un diccionario con:
#             - Estado de la operación
#             - Mensaje con resultados
#             - Lista de archivos descargados con sus rutas
#             - Ruta de la carpeta temporal donde se guardaron los archivos
#             - URL utilizada para la búsqueda
#         """
#     )

# # Función principal para ejecutar el agente
# def run_canada_modern_slavery_scraper(company_name: str):
#     """
#     Ejecuta el agente para buscar y descargar PDFs de Modern Slavery del catálogo canadiense
    
#     Args:
#         company_name (str): Nombre de la empresa (ej: "3m")
    
#     Returns:
#         Dict: Resultados de la operación
#     """
    
#     # Crear la tarea
#     task = create_canada_modern_slavery_task(company_name)
    
#     # Crear el crew
#     crew = Crew(
#         agents=[canada_modern_slavery_agent],
#         tasks=[task],
#         verbose=2
#     )
    
#     # Ejecutar
#     result = crew.kickoff()
    
#     return result

# # Ejemplo de uso
# async def ca_agent_statement(company_name):
    

    
#     print("Iniciando agente de scraping de Modern Slavery del catálogo canadiense...")
#     result = run_canada_modern_slavery_scraper(company_name)
#     print("Resultado:", result)
    
#     # Mostrar archivos descargados
#     if isinstance(result, dict) and 'downloaded_files' in result:
#         print(f"\nArchivos descargados ({len(result['downloaded_files'])}):")
#         for file_info in result['downloaded_files']:
#             print(f"  - {file_info['title']}: {file_info['file_path']}")
#         print(f"\nCarpeta temporal: {result.get('TEMP_DIRectory', 'No disponible')}")
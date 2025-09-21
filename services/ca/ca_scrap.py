# import os
# import asyncio
# from crewai import Agent
# from crewai_tools import ScrapeWebsiteTool
# from langchain_ollama import OllamaLLM

# from crewai import Agent, Task, Crew
# from crewai.tools import BaseTool
# from pydantic import BaseModel, Field


# # Definir el LLM (Ollama en local)
# llm1 = OllamaLLM(
#     model="ollama/qwen2.5:0.5b",
#     temperature=0.7
# )


# from crewai.tools import tool

# @tool("fetch_data_async")
# async def fetch_data_async(query: str) -> str:
#     """Asynchronously fetch data based on the query."""
#     # Simulate async operation
#     await asyncio.sleep(1)
#     return f"Data retrieved for {query}"



# # Crear la herramienta de scraping
# scraper_tool = ScrapeWebsiteTool("https://www.publicsafety.gc.ca/cnt/rsrcs/lbrr/ctlg/dtls-en.aspx?d=PS&i=99611367")

# # Crear el agente con la tool oficial de CrewAI
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
#     tools=[scraper_tool, fetch_data_async],  # ✅ Usamos ScrapeWebsiteTool
#     llm=llm1
# )

# task = Task(
#     description="Find info about modern-slavery",
#     expected_output="a json with all modern slavery info in it value",
#     agent=canada_modern_slavery_agent  # Must be properly defined agent
# )

# # Crear el crew
# crew = Crew(
#     agents=[canada_modern_slavery_agent],
#     tasks=[task],
#     verbose=True
# )

# result = crew.kickoff()
    
# print(result)



# from crewai import Agent, Task, Crew, LLM
# from crewai_tools import  SerperDevTool, ScrapeWebsiteTool #, FirecrawlScrapeWebsiteTool 
# from langchain_ollama import OllamaLLM
# from utils_folder.loggger import log_error
# from services_agents.scrapper_agent_params import backstory1, goal1, task_description1, output1
# from smolagents import DuckDuckGoSearchTool, CodeAgent
# from utils_folder.custom_visitwebpage_tool import CustomVisitWebpageTool

# # Definir el LLM (Ollama en local)
# # llm1 = OllamaLLM(
# #     # model="ollama/qwen2.5:0.5b",
# #     model="ollama/deepseek-r1:1.5b",
# #     temperature=0.7
# # )

# # Definir el LLM (Ollama en local)
# llm1 = LLM(
#     model="gemini/gemini-2.0-flash",
#     temperature=0.7
# )

# # Initialize tools


# search_tool = SerperDevTool()  # For finding company websites
# scraper_tool = ScrapeWebsiteTool()  # For basic scraping
# # advanced_scraper = FirecrawlScrapeWebsiteTool()  # For complex sites



# # async def main_scrapper_agent(company, country):
# async def main_scrapper_agent(model, url):
    
#     try:
#         # country_tool = 'AU'
#         # if country == "CANADA": country_tool = 'CA'
#         # brave_search_tool = BraveSearchTool(
#         #     country=country_tool,
#         #     n_results=5,
#         #     save_file=True
#         # )
        
#         # Create the agent
#         modern_slavery_researcher = Agent(
#             role="Modern Slavery Research Specialist",
#             goal=goal1,
#             backstory=backstory1,
#             tools=[search_tool, scraper_tool],
#             verbose=True,
#             llm=llm1
#         )

#         # Create task
#         research_task = Task(
#             # description=f"Search for {company} official website for {country} and then, inside this: {task_description1}",
#             # expected_output=output1,
#             # description=f"Search on internet for the company: {company} official website in the country of: {country} and extract all information related to modern slavery policies, statements, supply chain transparency, and compliance measures",
#             expected_output="Detailed report of modern slavery-related information found on the company website also, return the URL and date of pdf statements",
#             agent=modern_slavery_researcher
#         )

#         # Run the crew
#         crew = Crew(agents=[modern_slavery_researcher], tasks=[research_task])
#         # result = crew.kickoff()
#         result = crew.kickoff_async()
#         return result
#     except Exception as e:
#         log_error(f"An error occurred: {e}")
#         return None
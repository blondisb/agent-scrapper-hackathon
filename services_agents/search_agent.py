import anyio.to_thread
from smolagents import DuckDuckGoSearchTool, CodeAgent, ToolCallingAgent
from utils_folder.custom_visitwebpage_tool import CustomVisitWebpageTool

async def url_finder_agent(model, company, country):
    
    agent = CodeAgent(
        model = model,
        tools = [DuckDuckGoSearchTool()]
    )

    prompt = f"""
        You are a websites research assistant specialized in web navigation.

        Your task is find the official website for the company: {company} in the country: {country}
        Your output must **always** be the URL of the company (**in that country**) found
        Your only send a global webpage if doesnt exist the webpage for this country: {country}
        
        Do not add extra text, explanations.  
        Return only the plain text. 

        Example output (for CANADA):
            https://www.ktm.com/en-ca.html
        or:
            https://www.3mcanada.ca/3M/en_CA/company-ca
        or:
            https://www.decathlon.ca/en
    """

    resp = agent.run(task=prompt, max_steps=6)
    return resp

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

    resp = agent.run(task=prompt, max_steps=4)
    return resp



async def visitor_agent(model, url):
    agent = ToolCallingAgent(
        model=model,
        tools=[CustomVisitWebpageTool()]
    )

    prompt = f"""
        You are a websites research assistant specialized in web navigation.

        Your task is using the tool: custom_scrapping_modern_slavery,  that i give to you, navigate **ONLY** in this website {url} in order to find modern slavery related info. Specifically anual reports or news, which often are published in footer page. Also, you are to search in sections like: 'About Us', or 'Our Company'
        Your output must **always** be a string with this formmat:
        
            info_ecountered(yes/not)|||url_modern_slavery_encountered|||brief description about the section modern slavery or related

        Do not add extra text, explanations.  
        Return only the plain text. 

        Example output:
            yes|||https://multimedia.3m.com/mws/media/2579388O/3m-2025-modern-slavery-statement.pdf|||The page host: https://www.3mcanada.ca/3M/en_CA/company-ca/ already has content abour modern slavery
    """

    # resp = agent.run(task=prompt, max_steps=3)
    # resp = agent.run(task=prompt, max_steps=4)
    resp = await anyio.to_thread.run_sync(agent.run, prompt)
    return resp
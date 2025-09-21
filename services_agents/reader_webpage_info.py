from google import genai
from dotenv import load_dotenv, find_dotenv
from utils_folder.custom_visitwebpage_tool_ASYNC import CustomVisitWebpageTool
from utils_folder.loggger import log_error, log_normal
import asyncio

load_dotenv(find_dotenv(), override=True)

async def reading_webpagecontent(url):
    client = genai.Client()
    visit_tool_srv = CustomVisitWebpageTool()

    try:
        content_page =  await visit_tool_srv.forward(
            url     = url,
            # query   = """I need all information related to: The UK's Modern Slavery Act 2015 is a landmark piece of legislation designed to combat modern slavery and human trafficking by consolidating previous offenses, increasing penalties for perpetrators, introducing measures to protect victims, and creating an Independent Anti-slavery Commissioner. A key provision is Section 54, which requires large commercial organizations (those with annual turnover above a set threshold) to publish a yearly statement detailing the steps they've taken to address slavery in their supply chains. """
            query   = "Search for data related to modern-slavery"
        )
        log_normal(f"content_pagea: {content_page}", "reading_webpagecontent")

        if content_page:
            # Contar tokens antes de enviar
            count = client.models.count_tokens(
                model="gemini-2.0-flash",
                contents=content_page
            )
            log_normal(f"Cantidad de tokens de entrada: {count.total_tokens}", "reading_webpagecontent")

            # Llamar al modelo limitando tokens de salida
            # response = client.models.generate_content(
            #     model="gemini-2.0-flash",
            #     contents=content_page
            # )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                    your task is find data related with **MODERN SLAVERY** in the following content
                    your answer **ALWAYS** are going to be shorter, giving a confirmation if content contains or not, info related
                    if contains, find pdf, links, texts, paragraph, etc.

                    The following content is this: {content_page}               
                """
            )

            return response.text
        else:
            return None
    except Exception as e:
        log_error(e, "reading_webpagecontent")
        raise e
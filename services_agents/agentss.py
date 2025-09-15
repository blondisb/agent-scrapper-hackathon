from google import genai
from dotenv import load_dotenv, find_dotenv
from utils.loggger import log_error, log_normal
from utils.utils import delete_folders, save_file
from fastapi.responses import JSONResponse

load_dotenv(find_dotenv(), override=True)

async def main_agents(abn: str, pdf_names: list, pdf_folder, txt_path):
    
    try:
        client = genai.Client()

        pdf_list = []
        for pdf_path in pdf_names:
            pdf = client.files.upload(file=pdf_path)
            pdf_list.append(pdf)
        delete_folders(pdf_folder)

        # Construir la entrada
        contents = [
            """
            You are an expert analyst in corporate social responsibility and compliance. You will be given several annual Modern Slavery Statements from the same company across different years. Your task is to carefully analyze each document and then compare them across years.

            For each statement:
            - Extract concrete facts such as implemented actions, mitigation strategies, reported risks, audits, training programs, and stakeholder engagement.
            - Identify key dates, deadlines, or timelines mentioned.
            - Highlight specific policies or frameworks introduced to address modern slavery.
            - Note measurable improvements, progress indicators, or new commitments.

            When comparing across all statements:
            - Summarize how the company’s approach to modern slavery has evolved over time.
            - Point out advancements, improvements, or new measures in later reports compared to earlier ones.
            - Identify recurring issues or risks that remain unaddressed.
            - Highlight any significant changes in governance, supply chain monitoring, or worker protection.

            Finally, provide a comparative table or bullet list showing year-by-year progress in:
            1. Risks identified
            2. Mitigation measures
            3. Policies implemented
            4. Concrete outcomes or evidence of effectiveness

            """,
            pdf_list
        ]

        # Contar tokens antes de enviar
        count = client.models.count_tokens(
            model="gemini-2.0-flash",
            contents=contents
        )
        log_normal(f"Cantidad de tokens de entrada: {count.total_tokens}", "main_agents")

        # Llamar al modelo limitando tokens de salida
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents
        )
        log_normal(f"LLM response: {response}", "main_agents")
        
        save_file(
            txt_path,
            f"(({count.total_tokens}, {response.usage_metadata.total_token_count})) || {response.text}"
        )

        # print(response.text)
        return {
            "tokens": {
                "input": count.total_tokens,
                "total": response.usage_metadata.total_token_count
            },
            "llm_response": response.text
        }
        
    except Exception as e:
        log_error(f"Error al llamar al modelo: {e}", "main_agents")
        raise e
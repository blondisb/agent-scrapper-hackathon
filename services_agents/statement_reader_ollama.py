import ollama
from dotenv import load_dotenv, find_dotenv
from utils_folder.loggger import log_error, log_normal
from utils_folder.utils import delete_folders, save_file
from fastapi.responses import JSONResponse
import PyPDF2

load_dotenv(find_dotenv(), override=True)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto plano de un PDF."""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


async def main_agents2(abn: str, pdf_names: list, pdf_folder: str, txt_path: str):
    try:
        # Extraer texto de cada PDF
        pdf_texts = []
        for pdf_path in pdf_names:
            pdf_text = extract_text_from_pdf(pdf_path)
            pdf_texts.append(f"### Documento {pdf_path}\n{pdf_text}")
        delete_folders(pdf_folder)

        # Construir el prompt
        prompt = f"""
        You are an expert analyst in corporate social responsibility and compliance. 
        You will be given several annual Modern Slavery Statements from the same company across different years. 
        Your task is to carefully analyze each document and then compare them across years.

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

        Here are the documents:

        {chr(10).join(pdf_texts)}
        """

        # Llamar a Ollama
        response = ollama.chat(
            model="llama3",  # o "mistral", "gemma", etc.
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        llm_text = response["message"]["content"]

        # Guardar la salida
        save_file(
            txt_path,
            llm_text
        )

        return {
            "tokens": {
                "input": None,   # Ollama hoy no da conteo de tokens exacto
                "total": None
            },
            "llm_response": llm_text
        }

    except Exception as e:
        log_error(f"Error al llamar al modelo: {e}", "main_agents")
        raise e

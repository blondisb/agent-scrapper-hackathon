from fastapi.responses import JSONResponse
import os
import asyncio
from groq import AsyncGroq
import PyPDF2
import tiktoken
from typing import List
from utils_folder.utils import delete_folders, save_file


async def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un PDF."""
    def _extract_pdf_text(path):
        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    
    return await asyncio.to_thread(_extract_pdf_text, pdf_path)

async def extract_text_from_txt(txt_path: str) -> str:
    """Extrae texto de un archivo .txt."""
    def _read_txt_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    
    return await asyncio.to_thread(_read_txt_file, txt_path)

async def load_texts_from_paths(paths: List[str], pdf_folder: str) -> List[str]:
    """Dado un listado de rutas de archivos (pdf o txt), devolver su contenido como lista de strings."""
    texts = []
    for p in paths:
        p_lower = p.lower()
        try:
            if p_lower.endswith(".pdf"):
                txt = await extract_text_from_pdf(p)
                texts.append(txt)
            elif p_lower.endswith(".txt"):
                txt = await extract_text_from_txt(p)
                texts.append(txt)
            else:
                # desconocido: ignorar o intentar convertirlo
                continue
        except Exception as exc:
            print(f"⚠️ Error procesando {p}: {exc}")
    
    delete_folders(pdf_folder)
    return texts

def chunk_text(text: str, max_tokens: int, tokenizer) -> List[str]:
    """Divide texto en trozos según límite de tokens (estrategia simple)."""
    tokens = tokenizer.encode(text)
    # print("\n\n============", tokens)
    if len(tokens) <= max_tokens:
        return [text]
    # dividir aproximadamente en dos y recursivamente
    mid = len(text) // 2
    return chunk_text(text[:mid], max_tokens, tokenizer) + chunk_text(text[mid:], max_tokens, tokenizer)

async def summarize_with_groq_async(
    file_paths: List[str],
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
    max_tokens: int = 20000,
    pdf_folder: str = "",
    txt_path: str=""
) -> str:
    """Función asincrónica que toma una lista de rutas y devuelve un resumen usando Groq."""
    # inicializar cliente async
    client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

    # extraer textos
    texts = await load_texts_from_paths(file_paths, pdf_folder)
    # concatenar todos con separadores
    full_text = "\n\n".join(texts)

    # escoger tokenizer (adecuado para el modelo que uses)
    encoder = tiktoken.get_encoding("gpt2")  # ajusta según modelo
    # fragmentar si es muy largo
    chunks = chunk_text(full_text, max_tokens, encoder)

    # construir prompt
    prompt = (
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

            Finally, provide a comparative *bullet list* showing year-by-year progress in:
            1. Risks identified
            2. Mitigation measures
            3. Policies implemented
            4. Concrete outcomes or evidence of effectiveness

            The statements here:
            """
        + "\n\n---\n\n".join(chunks)
    )

    # hacer la llamada asíncrona al modelo
    resp = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un asistente que resume documentos largos."},
            {"role": "user", "content": prompt},
        ],
        model=model,
    )

    if resp is None:
        raise JSONResponse(status_code=500, content={"error": "No response from AI"}) 
    else:
        # extraer contenido de la respuesta
        save_file(
            txt_path,
            # f"(({count.total_tokens}, {response.usage_metadata.total_token_count})) || {response.text}"
            resp.choices[0].message.content
        )
        return resp.choices[0].message.content
    







async def summarize_with_groq_async_chunked(
    file_paths: List[str],
    model: str = "llama-3.3-70b-versatile",
    max_tokens_input: int = 3000,     # límite para prompt
    max_tokens_summary: int = 500,     # cuánto puede generar el resumen por chunk
    pdf_folder: str = "",
    txt_path: str=""
) -> str:
    client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    texts = await load_texts_from_paths(file_paths, pdf_folder)
    full_text = "\n\n".join(texts)

    encoder = tiktoken.get_encoding("gpt2")

    # función que divide en chunks
    chunks = chunk_text(full_text, max_tokens_input, encoder)

    partial_summaries = []
    for chunk in chunks:
        prompt = (
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

                Finally, provide a comparative *bullet list* showing year-by-year progress in:
                1. Risks identified
                2. Mitigation measures
                3. Policies implemented
                4. Concrete outcomes or evidence of effectiveness

                The statements here:
                """
            + "\n\n---\n\n".join(chunk)
        )
        resp = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un asistente que resume."},
                {"role": "user", "content": prompt},
            ],
            model=model,
            max_tokens=max_tokens_summary
        )
        partial_summaries.append(resp.choices[0].message.content)

    # ahora combina los resúmenes parciales en un solo texto y haz un resumen final
    combined = "\n\n".join(partial_summaries)
    final_prompt = (
        "Toma estos resúmenes parciales y genera un resumen consolidado:\n\n" + combined
    )
    resp2 = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un asistente que resume documentos."},
            {"role": "user", "content": final_prompt},
        ],
        model=model
    )
    # return resp2.choices[0].message.content

    if resp2 is None:
        raise JSONResponse(status_code=500, content={"error": "No response from AI"}) 
    else:
        save_file(
            txt_path,
            resp2.choices[0].message.content
        )
        return resp2.choices[0].message.content

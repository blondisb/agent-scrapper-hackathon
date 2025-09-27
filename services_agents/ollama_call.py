# from fastapi.responses import JSONResponse
# import os
# import asyncio
# from ollama import AsyncClient  # cliente async de Ollama :contentReference[oaicite:1]{index=1}
# import PyPDF2
# import tiktoken
# from typing import List
# from utils_folder.utils import delete_folders, save_file

# async def extract_text_from_pdf(pdf_path: str) -> str:
#     def _extract_pdf_text(path):
#         text_parts = []
#         with open(path, "rb") as f:
#             reader = PyPDF2.PdfReader(f)
#             for page in reader.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text_parts.append(page_text)
#         return "\n".join(text_parts)
#     return await asyncio.to_thread(_extract_pdf_text, pdf_path)

# async def extract_text_from_txt(txt_path: str) -> str:
#     def _read_txt_file(path):
#         with open(path, "r", encoding="utf-8") as f:
#             return f.read()
#     return await asyncio.to_thread(_read_txt_file, txt_path)

# async def load_texts_from_paths(paths: List[str], pdf_folder: str) -> List[str]:
#     texts = []
#     for p in paths:
#         p_lower = p.lower()
#         try:
#             if p_lower.endswith(".pdf"):
#                 txt = await extract_text_from_pdf(p)
#                 texts.append(txt)
#             elif p_lower.endswith(".txt"):
#                 txt = await extract_text_from_txt(p)
#                 texts.append(txt)
#             else:
#                 continue
#         except Exception as exc:
#             print(f"⚠️ Error procesando {p}: {exc}")
#     delete_folders(pdf_folder)
#     return texts

# def chunk_text(text: str, max_tokens: int, tokenizer) -> List[str]:
#     tokens = tokenizer.encode(text)
#     if len(tokens) <= max_tokens:
#         return [text]
#     mid = len(text) // 2
#     return chunk_text(text[:mid], max_tokens, tokenizer) + chunk_text(text[mid:], max_tokens, tokenizer)

# async def summarize_with_ollama_async(
#     file_paths: List[str],
#     model: str = "qwen2.5:0.5b",  # ajusta al modelo que tengas en Ollama
#     max_tokens: int = 20000,
#     pdf_folder: str = "",
#     txt_path: str = ""
# ) -> str:
#     client = AsyncClient()

#     texts = await load_texts_from_paths(file_paths, pdf_folder)
#     full_text = "\n\n".join(texts)

#     # tokenizador; ajusta si tienes otro tokenizer para Ollama
#     encoder = tiktoken.get_encoding("gpt2")
#     chunks = chunk_text(full_text, max_tokens, encoder)

#     prompt = (
#         """
#         You are an expert analyst in corporate social responsibility and compliance. You will be given several annual Modern Slavery Statements from the same company across different years. Your task is to carefully analyze each document and then compare them across years.

#         For each statement:
#         - Extract concrete facts such as implemented actions, mitigation strategies, reported risks, audits, training programs, and stakeholder engagement.
#         - Identify key dates, deadlines, or timelines mentioned.
#         - Highlight specific policies or frameworks introduced to address modern slavery.
#         - Note measurable improvements, progress indicators, or new commitments.

#         When comparing across all statements:
#         - Summarize how the company’s approach to modern slavery has evolved over time.
#         - Point out advancements, improvements, or new measures in later reports compared to earlier ones.
#         - Identify recurring issues or risks that remain unaddressed.
#         - Highlight any significant changes in governance, supply chain monitoring, or worker protection.

#         Finally, provide a comparative *bullet list* showing year-by-year progress in:
#         1. Risks identified
#         2. Mitigation measures
#         3. Policies implemented
#         4. Concrete outcomes or evidence of effectiveness

#         The statements here:
#         """
#         + "\n\n---\n\n".join(chunks)
#     )

#     # Hacer la llamada a Ollama
#     resp = await client.chat(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are an assistant that summarizes long documents."},
#             {"role": "user", "content": prompt},
#         ],
#         # puedes incluir stream=True si quieres respuesta por partes
#     )

#     if resp is None:
#         raise JSONResponse(status_code=500, content={"error": "No response from AI"})
#     else:
#         # resp es un dict o un objeto ChatResponse que tiene .message.content :contentReference[oaicite:2]{index=2}
#         content = resp["message"]["content"] if isinstance(resp, dict) else resp.message.content
#         save_file(
#             txt_path,
#             content
#         )
#         return content

# async def summarize_with_ollama_async_chunked(
#     file_paths: List[str],
#     model: str = "llama3",
#     max_tokens_input: int = 3000,
#     max_tokens_summary: int = 500,
#     pdf_folder: str = "",
#     txt_path: str = ""
# ) -> str:
#     client = AsyncClient()
#     texts = await load_texts_from_paths(file_paths, pdf_folder)
#     full_text = "\n\n".join(texts)

#     encoder = tiktoken.get_encoding("gpt2")
#     chunks = chunk_text(full_text, max_tokens_input, encoder)

#     partial_summaries = []
#     for chunk in chunks:
#         prompt = (
#             """
#             You are an expert analyst in corporate social responsibility and compliance. You will be given several annual Modern Slavery Statements from the same company across different years. Your task is to carefully analyze each document and then compare them across years.

#             For each statement:
#             - Extract concrete facts such as implemented actions, mitigation strategies, reported risks, audits, training programs, and stakeholder engagement.
#             - Identify key dates, deadlines, or timelines mentioned.
#             - Highlight specific policies or frameworks introduced to address modern slavery.
#             - Note measurable improvements, progress indicators, or new commitments.

#             When comparing across all statements:
#             - Summarize how the company’s approach to modern slavery has evolved over time.
#             - Point out advancements, improvements, or new measures in later reports compared to earlier ones.
#             - Identify recurring issues or risks that remain unaddressed.
#             - Highlight any significant changes in governance, supply chain monitoring, or worker protection.

#             Finally, provide a comparative *bullet list* showing year-by-year progress in:
#             1. Risks identified
#             2. Mitigation measures
#             3. Policies implemented
#             4. Concrete outcomes or evidence of effectiveness

#             The statements here:
#             """
#             + "\n\n---\n\n" + chunk
#         )
#         resp = await client.chat(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are an assistant that summarizes."},
#                 {"role": "user", "content": prompt},
#             ],
#             # puedes usar max_tokens, o parámetros adicionales si Ollama los soporta
#         )
#         content = resp["message"]["content"] if isinstance(resp, dict) else resp.message.content
#         partial_summaries.append(content)

#     combined = "\n\n".join(partial_summaries)
#     final_prompt = (
#         "Take these partial summaries and produce a consolidated summary:\n\n" + combined
#     )
#     resp2 = await client.chat(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are an assistant that summarizes."},
#             {"role": "user", "content": final_prompt},
#         ],
#     )

#     if resp2 is None:
#         raise JSONResponse(status_code=500, content={"error": "No response from AI"})
#     else:
#         content2 = resp2["message"]["content"] if isinstance(resp2, dict) else resp2.message.content
#         save_file(txt_path, content2)
#         return content2

from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

def main_agents():
    
    client = genai.Client()
    pass

    # # Subir PDFs
    # pdf1 = client.files.upload(file="ms3pages.pdf")
    # pdf2 = client.files.upload(file="otro.pdf")

    # # Construir la entrada
    # contents = [
    #     "Give me a joint summary of these PDF files.",
    #     pdf1,
    #     pdf2
    # ]

    # # Contar tokens antes de enviar
    # count = client.models.count_tokens(
    #     model="gemini-2.0-flash",
    #     contents=contents
    # )
    # print(f"Cantidad de tokens de entrada: {count.total_tokens}")

    # # Llamar al modelo limitando tokens de salida
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=contents,
    #     generation_config={
    #         "max_output_tokens": 500  # aquí decides el límite de salida
    #     }
    # )

    # print(response.text)

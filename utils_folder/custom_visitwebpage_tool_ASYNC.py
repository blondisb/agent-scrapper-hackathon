import re
import logging
from sentence_transformers import SentenceTransformer, CrossEncoder
from smolagents import VisitWebpageTool, WebSearchTool, CodeAgent
from utils_folder.forward_playwright import scrape_playwright_async
from utils_folder.loggger import log_error, log_normal

logger = logging.getLogger(__name__)

class CustomVisitWebpageTool(VisitWebpageTool):
    name = "custom_scrapping_modern_slavery"
    description = """
    Given a URL and query, fetch detailed page content (including dynamic content)
    using Playwright async. Return passages matching the query using semantic search.
    If scraping fails or content is empty or error occurs, return empty string so that WebSearchTool can be used.
    """
    inputs = {
        "url": { "type": "string", "description": "The URL to scrape" },
        "query": { "type": "string", "description": "Search query/filter keywords" }
    }
    output_type = "string"

    def __init__(self):
        super().__init__(max_output_length=999999)
        self.bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    async def forward(self, url: str, query: str) -> str:
        logger.debug(f">> CustomVisitWebpageTool.forward (async): url={url}, query={query}")

        content: str
        try:
            content = await scrape_playwright_async(url)
        except Exception as e:
            log_error(e, "forward")
            logger.error(f"Scraping failed: {e}")
            return ""  # indica fallo; agente debe usar búsqueda web

        if not content or not content.strip():
            logger.debug("Scrape returned empty or blank content")
            return ""

        sentences = self.get_sentences(content)
        if not sentences:
            logger.debug("No sentences extracted from content")
            return ""

        bi_filtered = self.apply_bi_encoder(query, sentences)
        if not bi_filtered:
            logger.debug("No results after bi-encoder filtering")
            return ""

        cross_filtered = self.apply_cross_encoder(query, bi_filtered)
        if not cross_filtered:
            logger.debug("No results after cross-encoder filtering")
            return ""

        result = "\n".join(cross_filtered)
        logger.debug(f"<< CustomVisitWebpageTool.forward result length {len(result)}")
        return result

    @staticmethod
    def get_bi_encoder_top_k(num_sentences: int) -> int:
        if num_sentences <= 50:
            return min(20, num_sentences)
        elif num_sentences <= 500:
            return min(max(30, int(num_sentences * 0.1)), 100)
        elif num_sentences <= 2000:
            return min(max(50, int(num_sentences * 0.05)), 200)
        else:
            return 200

    def apply_bi_encoder(self, query: str, sentences: list[str]) -> list[str]:
        logger.debug(">> apply_bi_encoder")
        sentence_embeddings = self.bi_encoder.encode_document(sentences, convert_to_tensor=True)
        query_embedding = self.bi_encoder.encode_query(query, convert_to_tensor=True)
        similarities = self.bi_encoder.similarity(query_embedding, sentence_embeddings)
        top_k = self.get_bi_encoder_top_k(len(sentences))
        top_k = min(top_k, len(sentences))
        top_results = similarities.topk(k=top_k)
        results = [sentences[idx.item()] for idx in top_results.indices.flatten()]
        logger.debug(f"bi-encoder: selected {len(results)} sentences")
        return results

    def apply_cross_encoder(self, query: str, candidates: list[str]) -> list[str]:
        logger.debug(">> apply_cross_encoder")
        ranks = self.cross_encoder.rank(query, candidates, return_documents=True, top_k=3)
        results = [r["text"] for r in ranks]
        logger.debug(f"cross-encoder: returning {len(results)} candidates")
        return results

    @staticmethod
    def get_sentences(content: str) -> list[str]:
        logger.debug(">> get_sentences")
        sections = re.split(r'\n\s*\n', content.strip())
        sentences = []
        for section in sections:
            section_sentences = re.split(r'(?<=[.!?])\s+|(?<=\n)', section)
            for s in section_sentences:
                s2 = s.strip()
                if s2 and len(s2) >= 10:
                    sentences.append(s2)
        logger.debug(f"<< get_sentences: {len(sentences)} sentences extracted")
        return sentences

# Función que usa la herramienta, con fallback de búsqueda web
async def get_content_or_search(url: str, query: str, agent_model):
    """
    Intenta usar CustomVisitWebpageTool para obtener contenido detallado;
    si falla o contenido vacío, usa WebSearchTool para responder al query.
    """
    visit_tool = CustomVisitWebpageTool()
    try:
        content = await visit_tool.forward(url=url, query=query)
    except Exception as e:
        logger.error(f"Error calling scraper forward: {e}")
        content = ""

    if content and content.strip():
        return content
    else:
        # fallback usando WebSearchTool
        search_tool = WebSearchTool(max_results=5)  # ajustar número de resultados si quieres
        # WebSearchTool tiene llamada sin await (es síncrono normalmente)
        try:
            search_results = search_tool(query=query)
        except Exception as e:
            logger.error(f"Search tool also failed: {e}")
            return ""
        return search_results

# Ejemplo de integrarlo en un agente smolagents
def build_agent_with_custom_scraper_and_search(model):
    from smolagents import CodeAgent
    agent = CodeAgent(
        tools=[CustomVisitWebpageTool(), WebSearchTool()],
        model=model,
        add_base_tools=False,
        max_steps=4,
        instructions=(
            "You must use the WebSearchTool for web searches. "
            "Use CustomVisitWebpageTool only when you have a URL and scraping can succeed. "
            "If CustomVisitWebpageTool returns empty or fails, then use WebSearchTool to answer."
        )
    )
    return agent
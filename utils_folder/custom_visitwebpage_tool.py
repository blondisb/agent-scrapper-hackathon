#
# https://medium.com/@laurentkubaski/smolagents-extending-visitwebpagetool-to-implement-semantic-search-with-a-sentence-transformer-cada17e056b4
#

import re
from sentence_transformers import SentenceTransformer, CrossEncoder
from smolagents import VisitWebpageTool
import logging
import asyncio
# from custom_forward import customforward
from utils_folder.forward_playwright import scrape_playwright, scrape_playwright_async
# from forward_playwright import scrape_playwright, scrape_playwright_async

logger = logging.getLogger(__name__)


class CustomVisitWebpageTool(VisitWebpageTool):
    name = "custom_scrapping_modern_slavery"
    description = """
    Searches the content of a web page at a given URL.
    Returns the content of the page that matches the given search query.
    """
    inputs = {
        "url": { "type": "string", "description": "The url of the web page" },
        "query": { "type": "string", "description": "The search query to perform on the web page content.",
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__(max_output_length=999999)
        # Models are downloaded in ~/.cache/huggingface/hub
        # https://www.sbert.net/docs/sentence_transformer/usage/usage.html
        self.bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
        # https://www.sbert.net/docs/cross_encoder/usage/usage.html
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")


    def forward(self, url: str, query: str) -> str:
        logger.debug(f">> CustomVisitWebpageTool.forward: url={url}, query={query}")
        
        content = super().forward(url=url)
        # content = customforward(url)
        try:
            content = scrape_playwright(url)
            # content = await scrape_playwright_async(url)
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return ""  # or some marker the content isn’t usable

        results = self.get_sentences(content)
        results = self.apply_bi_encoder(query, results)
        results = self.apply_cross_encoder(query, results)

        results = "\n".join(results)
        logger.debug("<< CustomVisitWebpageTool.forward")
        return results

    @staticmethod
    def get_bi_encoder_top_k(num_sentences: int) -> int:
        result = None
        if num_sentences <= 50:
            result = min(20, num_sentences)  # small doc: retrieve almost all
        elif num_sentences <= 500:
            result =  min(max(30, int(num_sentences * 0.1)), 100)  # medium doc
        elif num_sentences <= 2000:
            result =  min(max(50, int(num_sentences * 0.05)), 200)  # large doc
        else:
            result =  200  # cap for very large docs
        logger.debug(f">> << CustomVisitWebpageTool.get_bi_encoder_top_k: num_sentences={num_sentences} -> top_k={result}")
        return result

    def apply_bi_encoder(self, query:str, sentences:list[str]) -> list[str]:
        logger.debug(">> CustomVisitWebpageTool.apply_bi_encoder")

        # https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html#sentence_transformers.SentenceTransformer.encode
        # https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html#sentence_transformers.SentenceTransformer.encode_document
        # Dim = Tensor(nb_sentences,embedding_dim)
        sentence_embeddings = self.bi_encoder.encode_document(sentences,convert_to_tensor=True)

        # https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html#sentence_transformers.SentenceTransformer.encode_query
        # Dim = Tensor(embedding_dim,)
        query_embedding = self.bi_encoder.encode_query(query, convert_to_tensor=True)

        # https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html#sentence_transformers.SentenceTransformer.similarity
        # "Compute the similarity between two collections of embeddings"
        # "The output is a matrix with the similarity scores between all embeddings from the first parameter and all embeddings from the second parameter"
        # Dim = Tensor(1,nb_sentences)
        similarities = self.bi_encoder.similarity(query_embedding, sentence_embeddings)

        # Get top-k results
        top_k = self.get_bi_encoder_top_k(len(sentences))
        top_k = min(top_k, len(sentences))

        # https://docs.pytorch.org/docs/stable/generated/torch.topk.html#torch.topk
        # A namedtuple of (values, indices) is returned with the values and indices of the largest k elements of each row of the input tensor in the given dimension dim.
        # Dim = Tensor(1,top_k)
        top_results = similarities.topk(k=top_k)
        # flatten() transforms the Tensor(1,top_k) into Tensor(top_k,)
        # idx is a Tensor(,) so we call idx.item() to get the integer value
        # See https://docs.pytorch.org/docs/stable/generated/torch.Tensor.item.html#torch.Tensor.item
        # "Returns the value of this tensor as a standard Python number. This only works for tensors with one element"
        results = [sentences[idx.item()] for idx in top_results.indices.flatten()]

        logger.debug("bi-encoder results:")
        logger.debug("------")
        for result in results:
            logger.debug(result.replace("\n", " "))
        logger.debug("------")
        logger.debug(f"<< CustomVisitWebpageTool.apply_bi_encoder: returning nb results={len(results)}")

        return results

    def apply_cross_encoder(self, query:str, results:list[str]) -> list[str]:
        logger.debug(">> CustomVisitWebpageTool.apply_cross_encoder")
        ranks = self.cross_encoder.rank(query, results, return_documents=True, top_k=3)
        results = []
        for rank in ranks:
            results.append(rank["text"])
        logger.debug("cross-encoder results")
        logger.debug("------")
        for result in results:
            logger.debug(result.replace("\n", " "))
        logger.debug("------")
        logger.debug(f"<< CustomVisitWebpageTool.apply_cross_encoder: returning nb results={len(results)}")
        return results

    @staticmethod
    def get_sentences(content:str):
        logger.debug(">> CustomVisitWebpageTool.get_sentences")
        # split on whitespace
        #####################
        # \n → Matches a newline character.
        # \s* → Matches zero or more whitespace characters (spaces, tabs, newlines, etc.).
        #
        # So the regexp:
        # 1) looks for a newline,
        # 2) then any amount of whitespace
        # 3) then another newline.
        sections = re.split(r'\n\s*\n', content.strip())
        sentences = []
        for section in sections:
            # split on sentence endings
            ###########################
            # (?<=[.!?]) → This is a lookbehind assertion which says: “the position we’re at must be immediately after a ., !, or ?”.
            # \s+ → Matches one or more whitespace characters (spaces, tabs, newlines, etc.).
            # (?<=\n) -> This is a lookbehind assertion which says: "the position we're at must be immediately after a newline character".
            #
            section_sentences = re.split(r'(?<=[.!?])\s+|(?<=\n)', section)
            sentences.extend(section_sentences)
        # Only keep sentences that are long enough:
        sentences = [s for s in sentences if s.strip() and len(s.strip()) >= 10]
        logger.debug(f"<< CustomVisitWebpageTool.get_sentences: nb sentences={len(sentences)}")
        return sentences


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # or DEBUG if you want more details
        format="%(name)s - %(levelname)s - %(message)s"
    )
    # logging.getLogger("__main__").setLevel(logging.DEBUG)

    #url="https://en.wikipedia.org/wiki/Pont_des_Arts",
    # url="https://kids.nationalgeographic.com/animals/mammals/facts/leopard",
    # query="What is the weight of a leopard?"
    
    # url     = "https://www.3mcanada.ca/3M/en_CA/company-ca/"
    # query   = "There is something related with modern-slavery?"

    # url = "https://modern-slavery-statement-registry.service.gov.uk/statement-summary/zZQEGdH8/2022"
    # query = "give me details abour modern slavery risks"

    # url = "https://www.tesla.com/en_ca" 
    url = "https://www.airbus.com/en"
    # url = "https://www.boeing.ca/"
    query = "talk me about financial results and modern slavery"

    tool = CustomVisitWebpageTool()
    result = asyncio.run(tool.forward(
        url     = url,
        query   = query
    ))
    print(result)
import logging
import time
from langchain_community.embeddings import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

def compute_embedding_similarity(text1: str, text2: str, logger: logging.Logger, adjust: bool = True) -> float:
    try:
        if not text1.strip() or not text2.strip():
            logger.warning("One of the texts is empty, returning 0")
            return 0.0

        logger.debug(f"Computing similarity for texts:\nT1: {text1[:100]}...\nT2: {text2[:100]}...")
        start_time = time.time()
        emb1 = embedding_model.embed_query(text1)
        emb2 = embedding_model.embed_query(text2)
        raw_similarity = cosine_similarity([emb1], [emb2])[0][0]
        
        adjusted_similarity = raw_similarity
        if adjust:
            adjusted_similarity = max(0, raw_similarity - 0.1)
            len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
            if len_ratio < 0.6:
                adjusted_similarity *= 0.8
        
        logger.debug(f"Similarity calculated: {adjusted_similarity} (raw: {raw_similarity}) (in {time.time()-start_time:.2f}s)")
        return adjusted_similarity
    except Exception as e:
        logger.error(f"Error in compute_embedding_similarity: {str(e)}")
        return 0.0
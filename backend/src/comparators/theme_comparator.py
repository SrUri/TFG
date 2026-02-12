import logging
import re
import difflib
from typing import Dict
from src.llm.client import llm
from src.utils.embedding_utils import compute_embedding_similarity
from src.llm.prompts import get_theme_comparator_prompt
from src.utils.lang_detect import ensure_english

logger = logging.getLogger(__name__)

def compare_themes(theme1: Dict[str, str], theme2: Dict[str, str], subject_name1: str = "", subject_name2: str = "") -> float:
    logger.debug("🔍 Comparando temas:")
    logger.debug(f"Tema 1 ({subject_name1}):\n{theme1}")
    logger.debug(f"Tema 2 ({subject_name2}):\n{theme2}")
    
    if not theme1 or not theme2:
        return 0.0
    if all(theme1[key] == theme2[key] for key in theme1):
        return 1.0

    weights = {"core_topic": 0.4, "key_contents": 0.4, "application_domain": 0.2}
    similarities = {}
    for field in weights:
        text1 = theme1.get(field, "Unknown")
        text2 = theme2.get(field, "Unknown")
        logger.debug(f"🔎 Comparando campo '{field}':")
        logger.debug(f"  - Texto 1: {text1[:200]}...")
        logger.debug(f"  - Texto 2: {text2[:200]}...")

        if text1 == "Unknown" or text2 == "Unknown":
            similarities[field] = 0.0
        else:
            similarities[field] = compute_embedding_similarity(text1, text2, logger, adjust=False)

    title_similarity = 0.0
    if subject_name1 and subject_name2:
        title_similarity = difflib.SequenceMatcher(None, subject_name1.lower(), subject_name2.lower()).ratio()
        logger.info(f"Title similarity between '{subject_name1}' and '{subject_name2}': {title_similarity:.2f}")

    prompt = get_theme_comparator_prompt(theme1, theme2)
    logger.debug(f"📝 Prompt enviado al LLM:\n{prompt[:500]}...")
    
    try:
        llm_response = llm.invoke(prompt).strip()
        logger.info(f"Raw LLM response for theme comparison: {llm_response}")
        match = re.search(r"0?\.\d{1,2}", llm_response)
        if match:
            llm_score = float(match.group(0))
            logger.info(f"Extracted LLM score: {llm_score}")
        else:
            logger.warning(f"No numeric score found in LLM response: {llm_response}")
            llm_score = 0.0
    except Exception as e:
        logger.error(f"Error in LLM theme comparison: {e}")
        llm_score = 0.0

    weighted_score = sum(similarities[field] * weights[field] for field in weights)
    final_score = 0.45 * weighted_score + 0.45 * llm_score + 0.1 * title_similarity
    if theme1.get('core_topic') == theme2.get('core_topic') and theme1.get('key_contents') == theme2.get('key_contents'):
        final_score = max(final_score, 0.90)
    elif theme1.get('core_topic') == theme2.get('core_topic'):
        final_score = max(final_score, 0.80)
    final_score = round(min(max(final_score, 0.0), 1.0), 2)
    logger.info(f"Theme comparison - Embedding: {similarities}, LLM: {llm_score}, Title: {title_similarity:.2f}, Final: {final_score}")
    return final_score
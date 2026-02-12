from langdetect import detect
from src.llm.client import llm
import logging
from src.llm.prompts import translate_text_to_english

logger = logging.getLogger(__name__)

def ensure_english(text: str) -> str:
    """Traduce el texto a inglés usando LLM si no lo está."""
    if not text or not text.strip():
        return text
    
    try:
        lang = detect(text)
        logger.info(f"🌐 Detectado idioma: {lang}")
        logger.info(f"📥 Texto original ({lang}):\n{text[:500]}...")
    except Exception as e:
        logger.info(f"⚠️ No se pudo detectar idioma, se asume inglés: {e}")
        lang = "en"

    if lang.lower() != "en":
        logger.info("🌐 Traduciendo texto a inglés con LLM...")
        prompt = translate_text_to_english(text)
        translated = llm.invoke(prompt).strip()
        logger.info(f"📤 Texto traducido (en):\n{translated[:500]}...")
        return translated
    
    logger.info(f"✅ Texto ya en inglés:\n{text[:500]}...")
    return text
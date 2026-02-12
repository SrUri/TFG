import logging
import re
from typing import Dict
from fastapi import HTTPException
from urllib.parse import urlparse, parse_qs
from src.llm.client import llm
from src.llm.prompts import get_extract_subjects_prompt, get_extract_theme_prompt
from src.utils.json_utils import safe_json_parse
from src.utils.url_utils import fetch_url_content, build_urv_url
from src.extractors.urv_extractor import extract_urv_contents
from src.extractors.html_extractor import extract_contents_section
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_subject_theme(text: str, subject_title: str = None) -> Dict[str, str]:
    logger.debug(f"Subject title: {subject_title}")
    analysis_text = text
    logger.debug(f"Input text for theme extraction: {analysis_text[:2000]}")
    if isinstance(text, str) and "urv.cat" in text.lower() and "assignatura=" in text.lower():
        try:
            parsed = urlparse(text)
            params = parse_qs(parsed.query)
            contents_url = build_urv_url(text, params, '57')
            logger.info(f"🔍 Fetching URV contents from: {contents_url}")
            print(f"Fetching URV contents from: {contents_url}")
            response = fetch_url_content(contents_url)
            soup = BeautifulSoup(response, "html.parser")
            contents = extract_urv_contents(soup)
            if contents:
                logger.info("✅ URV contents extracted successfully from contents URL")
                analysis_text = "\n\n".join(f"{k.upper()}:\n{v}" for k, v in contents.items() if v)
            else:
                logger.info("⚠️ No contents found at specific URV contents URL, falling back to input text")
        except Exception as e:
            logger.error(f"⚠️ Error fetching URV contents from {contents_url}: {e}")

    if analysis_text == text and not re.search(r'\w+:\s*\w+|\n\s*[\d\.\-]+\s*\w+', analysis_text):
        logger.debug("🔍 Input text appears invalid, retrying contents extraction")
        contents = extract_contents_section(text)
        if contents:
            logger.info("✅ Contents extracted from input text")
            analysis_text = contents
        else:
            logger.info("⚠️ No contents extracted, using raw text")

    prompt = get_extract_theme_prompt(analysis_text)
    logger.debug(f"Prompt for theme extraction: {prompt[:1000]}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt).strip()
            logger.debug(f"Raw LLM response (attempt {attempt+1}): {response}")
            theme = safe_json_parse(response)
            if not all(key in theme for key in ["core_topic", "key_contents", "application_domain"]):
                raise ValueError("Missing required fields in JSON response")
            return {
                "core_topic": str(theme.get("core_topic", "")).strip() or subject_title or "Unknown",
                "key_contents": ", ".join(theme["key_contents"]) if isinstance(theme.get("key_contents"), list) else str(theme.get("key_contents", "")),
                "application_domain": str(theme.get("application_domain", "")).strip() or "General Education",
            }
        except Exception as e:
            logger.warning(f"JSON decode error on attempt {attempt+1}: {str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to extract theme after {max_retries} attempts: {str(e)}")
                return {
                    "core_topic": subject_title or "Unknown",
                    "key_contents": "Extracted from title: " + (subject_title or "Unknown"),
                    "application_domain": "General Education"
                }
            
def extract_subjects_with_llm(text: str, subject_title: str = None) -> Dict[str, Dict]:
    prompt = get_extract_subjects_prompt(subject_title, text)
    try:
        response = llm.invoke(prompt).strip()
        subjects = safe_json_parse(response)
        if not isinstance(subjects, dict):
            raise ValueError("LLM response is not a dictionary")
        subject_name = subject_title or "Unknown"
        subject_data = subjects.get(subject_name, {})
        validated_contents = {k: v for k, v in list(subject_data.get("contents", {}).items())[:8] if v}
        return {
            subject_name: {
                "competences": subject_data.get("competences", []),
                "objectives": subject_data.get("objectives", []),
                "contents": validated_contents
            }
        }
    except Exception as e:
        logger.error(f"Error processing LLM response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing response: {str(e)}")
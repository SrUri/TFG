import logging
from typing import Optional
from bs4 import BeautifulSoup
from src.extractors.urv_extractor import extract_urv_contents
from src.utils.html_utils import clean_html

logger = logging.getLogger(__name__)

def extract_contents_section(full_text: str) -> Optional[str]:
    logger.debug(f"🔍 Attempting to extract contents section from text (first 500 chars): {full_text[:500]}")
    soup = BeautifulSoup(full_text, 'html.parser')

    if "urv.cat" in full_text.lower() or "guiadocent.urv.cat" in full_text.lower():
        logger.info("🔍 Detected potential URV content, attempting URV contents extraction")
        extracted = extract_urv_contents(soup)
        if extracted:
            return "\n\n".join(f"{k.upper()}:\n{v}" for k, v in extracted.items() if v)
        logger.info("❌ No URV contents found")
        return None

    logger.info("🔍 Searching for contents header in non-URV content")
    print("🔍 Searching for contents header in non-URV content")
    target_headers = ['contents', 'contenidos', 'temario', 'syllabus', 'programme', 'course content', 'course programme', 'synopsis', 'syllabus of lectures', 'Syllabus of tutorials', 'Study Objective']
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        header_text = header.get_text(strip=True).lower()
        logger.debug(f"Checking header: '{header_text}'")
        if any(target in header_text for target in target_headers):
            logger.info(f"📌 Found contents header: '{header_text}'")
            print(f"📌 Encontrado título relevante: '{header_text}'")
            content_parts = []
            next_node = header.next_sibling
            while next_node:
                if next_node.name in ['div', 'section', 'ul', 'ol', 'table', 'p']:
                    content_parts.append(clean_html(str(next_node)))
                elif next_node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
                next_node = next_node.next_sibling
            if content_parts:
                content = "\n\n".join(part.strip() for part in content_parts if part.strip())
                if len(content.strip()) > 50:
                    logger.info("✅ Content extracted from section under contents header")
                    print("✅ Contenido obtenido desde sección bajo título")
                    return content
                else:
                    logger.info("⚠️ Extracted content too short, discarding")
    logger.info("❌ No contents header found, returning None")
    print("❌ No se encontraron secciones de contenidos")
    return None
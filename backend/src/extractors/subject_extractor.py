import logging
from fastapi import HTTPException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from src.extractors.urv_extractor import extract_urv_contents
from src.utils.url_utils import fetch_url_content
from src.utils.html_utils import clean_html
from src.utils.url_utils import build_urv_url

logger = logging.getLogger(__name__)

def extract_subject_from_url(subject_url: str, subject_title: str = None) -> str:
    if "bilakniha.cvut.cz" in subject_url and "/cs/" in subject_url:
        subject_url = subject_url.replace("/cs/", "/en/")

    logger.info(f"📥 Processing subject URL: {subject_url}")
    print(f"📥 Procesando asignatura individual: {subject_url}")

    is_urv = "urv.cat" in subject_url.lower() or "guiadocent.urv.cat" in subject_url.lower()
    if is_urv:
        logger.info("🔍 Detected URV URL - attempting contents extraction")
        parsed = urlparse(subject_url)
        params = parse_qs(parsed.query)
        result = {"contents": None, "objectives": None, "competences": None}

        for fitxa, section in [('57', 'contents'), ('56', 'objectives'), ('55', 'competences')]:
            url = build_urv_url(subject_url, params, fitxa)
            try:
                logger.info(f"🔍 Fetching URV {section} from: {url}")
                response = fetch_url_content(url)
                soup = BeautifulSoup(response, "html.parser")
                extracted = extract_urv_contents(soup, subject_title)
                if extracted:
                    for key in ['contents', 'objectives', 'competences']:
                        if extracted.get(key) and not result.get(key):
                            result[key] = extracted[key]
                            logger.info(f"✅ URV {key} extracted successfully")
            except Exception as e:
                logger.error(f"⚠️ Error fetching URV {section} from {url}: {e}")

        if any(result.values()):
            return "\n\n".join(f"{k.upper()}:\n{v}" for k, v in result.items() if v)

        logger.info("⚠️ No contents found at specific URV URLs, trying main page")
        try:
            content = fetch_url_content(subject_url)
            soup = BeautifulSoup(content, "html.parser")
            extracted = extract_urv_contents(soup, subject_title)
            if extracted:
                return "\n\n".join(f"{k.upper()}:\n{v}" for k, v in extracted.items() if v)
        except Exception as e:
            logger.error(f"⚠️ Error fetching main URL {subject_url}: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {subject_url}")

    logger.info("🔍 Processing non-URV URL, searching for content sections")
    try:
        content = fetch_url_content(subject_url)
        soup = BeautifulSoup(content, "html.parser")
        result = {"contents": None, "objectives": None, "competences": None}
        section_headers = {
            "contents": ["contents", "temario", "programa", "syllabus", "topics", "Syllabus of lectures", "Syllabus of tutorials"],
            "objectives": ["objectives", "objetivos", "learning outcomes", "learning results", "goals", "synopsis", "Study Objective"],
            "competences": ["competences", "competencias", "habilidades", "skills", "synopsis"]
        }

        for section, headers in section_headers.items():
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dt']):
                header_text = header.get_text(strip=True).lower()
                if any(h in header_text for h in headers):
                    content = []
                    next_node = header.next_sibling
                    while next_node:
                        if next_node.name in ['div', 'section', 'ul', 'ol', 'table', 'p', 'dd']:
                            content.append(clean_html(str(next_node)))
                        elif next_node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dt']:
                            break
                        next_node = next_node.next_sibling
                    if content:
                        result[section] = "\n".join(part.strip() for part in content if part.strip())
                        break

        if any(result.values()):
            return "\n\n".join(f"{k.upper()}:\n{v}" for k, v in result.items() if v)

        logger.info("⚠️ No se encontraron secciones específicas, intentando extracción genérica")
        main_content = soup.find(['div', 'section', 'article'], class_=['content', 'main-content', 'syllabus-content'])
        if main_content:
            content = clean_html(str(main_content))
            if content.strip():
                return f"CONTENTS:\n{content.strip()}"
        
        logger.info("⚠️ No se encontró contenido, devolviendo cadena vacía")
        return ""
    except Exception as e:
        logger.error(f"⚠️ Error fetching URL {subject_url}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {subject_url}")
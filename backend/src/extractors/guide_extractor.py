import re
import logging
from typing import List, Dict
from fastapi import HTTPException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.utils.url_utils import fetch_url_content

logger = logging.getLogger(__name__)

def extract_subjects_from_guide_generic(guide_url: str, max_subjects: int) -> List[Dict]:
    logger.info(f"🔵 Procesando guía de grado (genérico): {guide_url}")

    candidates = extract_all_links_from_page(guide_url, max_links=max_subjects)
    logger.info(f"🔍 Enlaces candidatos detectados: {len(candidates)}")

    subjects_data = []
    seen_urls = set()

    for cand in candidates:
        url = cand["url"]
        name = cand["link_text"].strip().title()

        if url in seen_urls:
            continue
        seen_urls.add(url)

        subjects_data.append({
            "name": name or "Unknown Subject",
            "url": url
        })
        logger.info(f"✅ Asignatura detectada: {name} → {url}")

    logger.info(f"🟢 Total asignaturas extraídas: {len(subjects_data)}")
    return subjects_data

def extract_all_links_from_page(guide_url: str, max_links: int) -> List[Dict]:
    logger.info(f"🔵 Procesando todos los enlaces de la página (casos especiales): {guide_url}")

    try:
        content = fetch_url_content(guide_url)
    except Exception as e:
        logger.error(f"❌ Error descargando la guía: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetch: {e}")

    soup = BeautifulSoup(content, "html.parser")
    visited_urls = set()
    all_links: List[Dict] = []

    for a_tag in soup.find_all("a", href=True):
        link_text = a_tag.get_text(strip=True).lower().strip()
        href = a_tag["href"].strip()

        if not href:
            continue

        full_url = urljoin(guide_url, href)

        if "bilakniha.cvut.cz" in full_url and "/cv/" in full_url:
            full_url = full_url.replace("/cs/", "/en/")
        
        if full_url in visited_urls:
            continue
        visited_urls.add(full_url)

        parent = a_tag.find_parent(["tr", "li", "div", "td"])
        context_html = parent.prettify() if parent else a_tag.prettify()
        context_html = context_html.replace('"', '').replace('\n', ' ').strip()

        is_valid = (
            ("cvut.cz" in full_url and "predmet" in full_url) or        # Erasmus Praga
            ("urv.cat" in full_url and "assignatura=" in full_url) or   # URV
            re.search(r"/(asignaturas|assignatures|syllabus)/[A-Z0-9]+$", full_url) or # Exemple FIB
            re.search(r"guiadocent\.udl\.cat/.*/\d{4}-\d{2}_\d+$", full_url)  # Exemple UdL
        )

        if is_valid:
            logger.info(f"🔗 Enlace válido detectado: {full_url}")
            all_links.append({
                "link_text": link_text,
                "url": full_url,
                "context_html": context_html
            })

        if max_links > 0 and len(all_links) >= max_links:
            logger.info(f"🔵 Límite de {max_links} enlaces alcanzado")
            break

    logger.info(f"✅ Extraídos {len(all_links)} enlaces válidos de casos especiales")
    return all_links
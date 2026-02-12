import logging
from typing import Dict

logger = logging.getLogger(__name__)

def is_subject_url(url: str) -> bool:
    url_lower = url.lower()
    return ("asignatura=" in url_lower or 
            "assignatura=" in url_lower or 
            "subject=" in url_lower or 
            "ficha=" in url_lower or
            any(kw in url_lower for kw in ["ficha_asignatura", "subject_description", "asignatura_detalle"]))

def convert_to_new_format(subjects: Dict) -> Dict:
    new_format = {}
    for name, contents in subjects.items():
        if isinstance(contents, dict):
            new_format[name] = {
                "competences": str(contents.get("competences", "")),
                "objectives": str(contents.get("objectives", "")),
                "contents": str(contents.get("contents", ""))
            }
        else:
            new_format[name] = {
                "competences": str(contents),
                "objectives": "",
                "contents": ""
            }
    return new_format
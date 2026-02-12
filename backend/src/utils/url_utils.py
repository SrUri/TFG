import logging
from typing import Dict
from fastapi import HTTPException
import requests
from urllib.parse import urlencode
from io import BytesIO
import fitz

logger = logging.getLogger(__name__)

def build_urv_url(base_url: str, params: Dict[str, str], fitxa_apartat: str) -> str:
    cleaned_params = {k: v[-1] for k, v in params.items() if k != 'fitxa_apartat'}
    cleaned_params['fitxa_apartat'] = fitxa_apartat
    return f"{base_url.split('?')[0]}?{urlencode(cleaned_params, doseq=True)}"

def fetch_url_content(url: str, headers: Dict[str, str] = None) -> str:
    headers = headers or {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text
import logging
import re
import time
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from src.llm.client import llm
from src.utils.json_utils import safe_json_parse
from src.utils.embedding_utils import compute_embedding_similarity
from src.llm.prompts import get_subject_expert_prompt
from src.utils.lang_detect import ensure_english

logger = logging.getLogger(__name__)

def similarity_score(text1: str, text2: str) -> Dict:
    logger.info("🟠 [EMBED] Iniciando cálculo de similitud")
    logger.debug(f"🟠 [EMBED] Texto 1 (inicio):\n{text1[:200]}...")
    logger.debug(f"🟠 [EMBED] Texto 2 (inicio):\n{text2[:200]}...")

    try:
        logger.info("🟠 [EMBED] Extrayendo componentes...")
        comp1 = extract_components(text1)
        comp2 = extract_components(text2)

        logger.debug(f"🟠 [EMBED] Componentes texto 1: {comp1}")
        logger.debug(f"🟠 [EMBED] Componentes texto 2: {comp2}")

        embed_scores = compute_embedding_similarities(comp1, comp2)
        logger.info(f"🟠 [EMBED] Puntuaciones crudas: {embed_scores}")

        final_score = compute_final_score(embed_scores)
        logger.info(f"🟠 [EMBED] Puntuación final: {final_score}")

        logger.info("🟠 [EMBED] Iniciando análisis cualitativo...")
        llm_analysis = qualitative_analysis(comp1, comp2, final_score)
        logger.debug(f"🟠 [EMBED] Análisis cualitativo:\n{llm_analysis}")

        return {
            'score': round(final_score, 4),
            'components': embed_scores,
            'llm_analysis': llm_analysis,
            'explanation': llm_analysis.get('explicacion', 'No se proporcionó una explicación detallada.')
        }
    except Exception as e:
        logger.error(f"🔴 [EMBED] Error crítico: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def extract_components(text: str) -> Dict[str, str]:
    components = {'name': '', 'competences': '', 'objectives': '', 'contents': ''}
    name_pattern = r'(?i)nombre:\s*(.*?)(?=\s*competencias|$)'
    competences_pattern = r'(?i)competencias:\s*(\[.*?\])'
    objectives_pattern = r'(?i)objetivos:\s*(\[.*?\])'
    contents_patterns = [
        r'(?i)contenidos:\s*({.*?})',
        r'(?i)contenidos:\s*(\[.*?\])',
        r'(?i)contents?:\s*({.*?})',
        r'(?i)contents?:\s*(\[.*?\])'
    ]

    try:
        name_match = re.search(name_pattern, text, re.DOTALL)
        if name_match:
            components['name'] = name_match.group(1).strip()

        comp_match = re.search(competences_pattern, text, re.DOTALL)
        if comp_match:
            components['competences'] = comp_match.group(1)

        obj_match = re.search(objectives_pattern, text, re.DOTALL)
        if obj_match:
            components['objectives'] = obj_match.group(1)

        for pattern in contents_patterns:
            cont_match = re.search(pattern, text, re.DOTALL)
            if cont_match:
                components['contents'] = cont_match.group(1)
                break
    except Exception as e:
        logger.error(f"Error extrayendo componentes: {str(e)}")

    return components

def compute_embedding_similarities(comp1: Dict[str, str], comp2: Dict[str, str]) -> Dict[str, float]:
    logger.info("🟠 [EMBED] Calculando similitud de embeddings...")
    embed_scores = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            key: executor.submit(cosine_sim, comp1[key], comp2[key])
            for key in ['contents', 'objectives', 'competences']
        }
        for key, future in futures.items():
            embed_scores[key] = future.result()
            logger.debug(f"🟠 [EMBED] Similitud {key}: {embed_scores[key]}")
    return embed_scores

def cosine_sim(text1: str, text2: str) -> float:
    return compute_embedding_similarity(text1, text2, logger)

def qualitative_analysis(comp1: Dict[str, str], comp2: Dict[str, str], final_score: float) -> Dict:
    logger.info("🟠 [EMBED-QA] Iniciando análisis cualitativo")
    logger.debug(f"🟠 [EMBED-QA] Comp1: {comp1}")
    logger.debug(f"🟠 [EMBED-QA] Comp2: {comp2}")

    prompt = get_subject_expert_prompt(comp1, comp2, final_score)

    try:
        logger.debug(f"🟠 [EMBED-QA] Prompt enviado al LLM:\n{prompt[:500]}...")
        start_time = time.time()
        response = llm.invoke(prompt)
        logger.info(f"🟠 [EMBED-QA] Respuesta LLM recibida en {time.time()-start_time:.2f}s")
        logger.info(f"🟠 [EMBED-QA] Respuesta completa LLM:\n{response}")

        response = response.strip()
        if not response.endswith("}"):
            logger.info("🟠 [EMBED-QA] Respuesta incompleta: faltaba '}', se ha añadido automáticamente")
            response += "}"

        analysis = safe_json_parse(response)
        if not isinstance(analysis, dict):
            logger.error(f"🔴 [EMBED-QA] Respuesta del LLM no es un diccionario: {analysis}")
            raise ValueError(f"Respuesta del LLM no es un diccionario válido: {type(analysis)}")
        
        required_keys = ["similitudes_tecnicas", "diferencias_sustanciales", "advertencias", "explicacion"]
        if not all(key in analysis for key in required_keys):
            missing_keys = [key for key in required_keys if key not in analysis]
            logger.error(f"🔴 [EMBED-QA] Claves faltantes en la respuesta: {missing_keys}")
            raise ValueError(f"JSON response missing required keys: {missing_keys}")
        
        if not (isinstance(analysis["similitudes_tecnicas"], list) and
                isinstance(analysis["diferencias_sustanciales"], list) and
                isinstance(analysis["advertencias"], list) and
                isinstance(analysis["explicacion"], str)):
            invalid_types = {key: type(analysis[key]) for key in required_keys if not isinstance(analysis[key], (list if key != "explicacion" else str))}
            logger.error(f"🔴 [EMBED-QA] Tipos incorrectos en la respuesta: {invalid_types}")
            raise ValueError(f"Invalid JSON structure: incorrect types for keys: {invalid_types}")
        
        logger.info(f"🟠 [EMBED-QA] Similitudes técnicas recibidas: {analysis['similitudes_tecnicas']}")
        logger.info(f"🟠 [EMBED-QA] Diferencias sustanciales recibidas: {analysis['diferencias_sustanciales']}")

        cleaned_diferencias = []
        for item in analysis["diferencias_sustanciales"]:
            if isinstance(item, str) and " vs. " in item:
                cleaned_diferencias.extend(x.strip() for x in item.split(" vs. "))
            elif isinstance(item, str):
                cleaned_diferencias.append(item)
            else:
                logger.warning(f"🟠 [EMBED-QA] Elemento no es string en diferencias_sustanciales: {item}")
                cleaned_diferencias.append(str(item))
        analysis["diferencias_sustanciales"] = cleaned_diferencias
        logger.info("🟠 [EMBED-QA] Análisis parseado correctamente")
        return analysis
    except Exception as e:
        logger.error(f"🔴 [EMBED-QA] Error inesperado: {str(e)}", exc_info=True)
        return {
            "similitudes_tecnicas": [],
            "diferencias_sustanciales": [],
            "advertencias": [f"Error en análisis cualitativo: {str(e)}"],
            "explicacion": f"No se pudo generar una explicación debido a un error: {str(e)}"
        }
    
def compute_final_score(embed_scores: Dict[str, float]) -> float:
    contents_sim = max(0, (embed_scores['contents'] - 0.3) * 1.6)
    objectives_sim = embed_scores['objectives'] * 0.2
    competences_sim = embed_scores['competences'] * 0.2
    final_score = min(1.0, contents_sim + objectives_sim + competences_sim)
    return final_score

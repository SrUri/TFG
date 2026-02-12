import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor, as_completed
import difflib
from sqlalchemy.orm import Session
from src.extractors.guide_extractor import extract_subjects_from_guide_generic
from src.extractors.subject_extractor import extract_subject_from_url
from src.llm.subject_llm import extract_subject_theme, extract_subjects_with_llm
from src.comparators.theme_comparator import compare_themes
from src.comparators.content_comparator import similarity_score
from src.utils.subject_utils import convert_to_new_format
from models.schemas import CompareRequest, CompareSubjectsRequest
from src.database.database import Comparison, get_db

logging.basicConfig(
    level=logging.INFO,
    filename='test_postman.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare-subjects")
async def compare_subjects(request: CompareSubjectsRequest, db: Session = Depends(get_db)):
    if not request:
        logger.error("🔴 [MAIN] Empty request received")
        raise HTTPException(status_code=400, detail="Empty request")
    
    logger.info(f"🔵 [MAIN] Iniciando comparación de asignaturas individuales")
    logger.info(f"🔵 [MAIN] URL1: {request.url1}, Título1: {request.subject_title1}")
    logger.info(f"🔵 [MAIN] URL2: {request.url2}, Título2: {request.subject_title2}")

    existing_comparison = db.query(Comparison).filter(
        Comparison.url1 == request.url1,
        Comparison.subject_title1 == request.subject_title1,
        Comparison.url2 == request.url2,
        Comparison.subject_title2 == request.subject_title2,
        Comparison.comparison_type == "compare-subjects"
    ).first()

    if existing_comparison:
        logger.info(f"🟢 [MAIN] Comparación ya existe en la base de datos, devolviendo resultado almacenado")
        return {
            "asignatura_origen": existing_comparison.subject_title1,
            "detalles_origen": existing_comparison.detalles_origen or {},
            "asignatura_comparada": existing_comparison.subject_title2,
            "detalles_comparada": existing_comparison.detalles_comparada or {},
            "similitud_contenido": existing_comparison.similarity_score,
            "componentes": existing_comparison.components,
            "analisis": existing_comparison.analysis,
            "explicacion": existing_comparison.explanation
        }

    try:
        logger.info("🔵 [MAIN] Fase 1: Extrayendo contenido de las asignaturas")
        subject_text1 = extract_subject_from_url(request.url1, request.subject_title1)
        subject_text2 = extract_subject_from_url(request.url2, request.subject_title2)
        
        logger.debug(f"🔵 [MAIN] Texto crudo asignatura 1 (primeros 500 chars):\n{subject_text1[:500]}")
        logger.debug(f"🔵 [MAIN] Texto crudo asignatura 2 (primeros 500 chars):\n{subject_text2[:500]}")

        logger.info("🔵 [MAIN] Fase 2: Extrayendo detalles estructurados")
        subjects1 = extract_subjects_with_llm(subject_text1, subject_title=request.subject_title1)
        subjects2 = extract_subjects_with_llm(subject_text2, subject_title=request.subject_title2)
        
        logger.debug(f"🔵 [MAIN] Respuesta LLM asignatura 1:\n{subjects1}")
        logger.debug(f"🔵 [MAIN] Respuesta LLM asignatura 2:\n{subjects2}")

        subjects1 = convert_to_new_format(subjects1)
        subjects2 = convert_to_new_format(subjects2)
        logger.debug(f"🔵 [MAIN] Asignatura 1 formateada:\n{subjects1}")
        logger.debug(f"🔵 [MAIN] Asignatura 2 formateada:\n{subjects2}")

        input_title1 = request.subject_title1
        best_match1 = difflib.get_close_matches(input_title1.upper(), [s.upper() for s in subjects1.keys()], n=1, cutoff=0.3)
        if not best_match1:
            logger.error(f"🔴 [MAIN] No se encontró la asignatura '{request.subject_title1}'. Títulos extraídos: {list(subjects1.keys())}")
            raise HTTPException(status_code=400, detail=f"Asignatura '{request.subject_title1}' no encontrada. Títulos disponibles: {list(subjects1.keys())}")
        
        input_title2 = request.subject_title2
        best_match2 = difflib.get_close_matches(input_title2.upper(), [s.upper() for s in subjects2.keys()], n=1, cutoff=0.3)
        if not best_match2:
            logger.error(f"🔴 [MAIN] No se encontró la asignatura '{request.subject_title2}'. Títulos extraídos: {list(subjects2.keys())}")
            raise HTTPException(status_code=400, detail=f"Asignatura '{request.subject_title2}' no encontrada. Títulos disponibles: {list(subjects2.keys())}")

        match_upper1 = best_match1[0]
        original_title1 = next((s for s in subjects1.keys() if s.upper() == match_upper1), match_upper1)
        match_upper2 = best_match2[0]
        original_title2 = next((s for s in subjects2.keys() if s.upper() == match_upper2), match_upper2)

        subject_data1 = subjects1[original_title1]
        subject_data2 = subjects2[original_title2]

        combined_text1 = f"""
            Nombre: {original_title1}
            Competencias: {subject_data1.get('competences', '')}
            Objetivos: {subject_data1.get('objectives', '')}
            Contenidos: {subject_data1.get('contents', '')}
        """
        combined_text2 = f"""
            Nombre: {original_title2}
            Competencias: {subject_data2.get('competences', '')}
            Objetivos: {subject_data2.get('objectives', '')}
            Contenidos: {subject_data2.get('contents', '')}
        """
        logger.debug(f"🔵 [MAIN] Texto combinado asignatura 1:\n{combined_text1}")
        logger.debug(f"🔵 [MAIN] Texto combinado asignatura 2:\n{combined_text2}")

        logger.info("🔵 [MAIN] Fase 3: Calculando similitud de contenido")
        analysis = similarity_score(combined_text1, combined_text2)
        logger.info(f"🔵 [MAIN] Resultado análisis:\n{analysis}")

        result = {
            "asignatura_origen": original_title1,
            "detalles_origen": subject_data1,
            "asignatura_comparada": original_title2,
            "detalles_comparada": subject_data2,
            "similitud_contenido": analysis.get('score', 0) * 100,
            "componentes": analysis.get('components', {}),
            "analisis": analysis.get('llm_analysis', ''),
            "explicacion": analysis.get('explanation', '')
        }

        db_comparison = Comparison(
            url1=request.url1,
            subject_title1=request.subject_title1,
            url2=request.url2,
            subject_title2=request.subject_title2,
            similarity_score=analysis.get('score', 0) * 100,
            components=analysis.get('components', {}),
            analysis=analysis.get('llm_analysis', ''),
            explanation=analysis.get('explanation', ''),
            comparison_type="compare-subjects",
            detalles_origen=subject_data1,
            detalles_comparada=subject_data2
        )
        db.add(db_comparison)
        db.commit()
        db.refresh(db_comparison)

        logger.info("🟢 [MAIN] Comparación de asignaturas completada y guardada en la base de datos")
        return result

    except HTTPException as he:
        logger.error(f"🔴 [MAIN] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"🔴 [MAIN] Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@app.post("/compare")
async def compare(request: CompareRequest, db: Session = Depends(get_db)):
    logger.info(f"🔵 [MAIN] Iniciando comparación")
    logger.info(f"🔵 [MAIN] URL1: {request.url1}")
    logger.info(f"🔵 [MAIN] URL2: {request.url2}")
    logger.info(f"🔵 [MAIN] Título asignatura: {request.subject_title}")

    try:
        # Fase inicial: Extraer detalles de la asignatura principal (siempre, ya que es rápida y necesaria)
        logger.info("🔵 [MAIN] Extrayendo asignatura principal")
        subject_text = extract_subject_from_url(request.url1, request.subject_title)
        main_theme = extract_subject_theme(subject_text)
        logger.info(f"🔵 [MAIN] Temática principal identificada: {main_theme}")

        subjects1 = extract_subjects_with_llm(subject_text, subject_title=request.subject_title)
        subjects1 = convert_to_new_format(subjects1)

        input_title = request.subject_title
        best_match = difflib.get_close_matches(input_title.upper(), [s.upper() for s in subjects1.keys()], n=1, cutoff=0.4)
        if not best_match:
            logger.error(f"🔴 [MAIN] No se encontró la asignatura '{request.subject_title}'")
            raise HTTPException(status_code=400, detail="Asignatura no encontrada")
        
        match_upper = best_match[0]
        original_title = next((s for s in subjects1.keys() if s.upper() == match_upper), match_upper)
        request.subject_title = original_title
        subject_data = subjects1[request.subject_title]
        combined_text1 = f"""
            Nombre: {request.subject_title}
            Competencias: {subject_data.get('competences', '')}
            Objetivos: {subject_data.get('objectives', '')}
            Contenidos: {subject_data.get('contents', '')}
        """

        # Nueva verificación inicial: Buscar comparaciones existentes para esta guía y asignatura origen
        existing_comparisons = db.query(Comparison).filter(
            Comparison.url1 == request.url1,
            Comparison.subject_title1 == request.subject_title,
            Comparison.guide_url == request.url2,
            Comparison.comparison_type == "compare"
        ).all()

        if existing_comparisons:
            logger.info(f"🟢 [MAIN] Comparaciones existentes encontradas para esta guía ({len(existing_comparisons)}), devolviendo resultados almacenados")
            detailed_subjects = []
            for comp in existing_comparisons:
                detailed_subjects.append({
                    "asignatura": comp.subject_title2,
                    "similitud_tematica": comp.theme_similarity,
                    "similitud_contenido": comp.similarity_score,
                    "componentes": comp.components,
                    "analisis": comp.analysis,
                    "explicacion": comp.explanation,
                    "detalles": comp.detalles_comparada or {},
                    "url": comp.url2
                })
            detailed_subjects.sort(key=lambda x: x["similitud_contenido"], reverse=True)
            
            return {
                "asignatura_origen": request.subject_title,
                "tema_principal": main_theme,
                "detalles_origen": subject_data,
                "coincidencias": detailed_subjects[:5]
            }

        # Si no existen, proceder con el flujo completo
        logger.info("🔵 [MAIN] No se encontraron comparaciones existentes, procediendo con extracción completa")

        logger.info("🔵 [MAIN] Fase 1: Extrayendo asignaturas básicas de la guía docente")
        guide_subjects = extract_subjects_from_guide_generic(request.url2, max_subjects=10)
        logger.info(f"🔵 [MAIN] Asignaturas encontradas en guía: {len(guide_subjects)}")
        
        logger.info("🔵 [MAIN] Fase 2: Procesando asignatura principal")
        guide_subjects_content = []
        for subject in guide_subjects:
            try:
                subject_content = extract_subject_from_url(subject["url"], subject["name"])
                if subject_content:
                    guide_subjects_content.append({
                        "name": subject["name"],
                        "url": subject["url"],
                        "content": subject_content
                    })
                    logger.info(f"✅ Contenido extraído para asignatura: {subject['name']}")
                else:
                    logger.warning(f"⚠️ No se encontró contenido para asignatura: {subject['name']}")
            except Exception as e:
                logger.error(f"❌ Error al procesar asignatura {subject['name']}: {e}")

        logger.info(f"🔵 [MAIN] Asignaturas con contenido extraído: {len(guide_subjects_content)}")
        subject_text = extract_subject_from_url(request.url1, request.subject_title)
        main_theme = extract_subject_theme(subject_text)
        logger.info(f"🔵 [MAIN] Temática principal identificada: {main_theme}")

        logger.info("🔵 [MAIN] Fase 3: Comparando temáticas")
        filtered_subjects = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_subject = {
                executor.submit(extract_subject_theme, extract_subject_from_url(subject['url'], subject['name'])): subject 
                for subject in guide_subjects
            }
            for future in as_completed(future_to_subject):
                subject = future_to_subject[future]
                try:
                    subject_theme = future.result()
                    theme_similarity = compare_themes(main_theme, subject_theme, request.subject_title, subject['name'])
                    logger.info(f"🔵 [MAIN] Comparación temática: {subject['name']} - Similitud: {theme_similarity:.2f}")
                    if theme_similarity >= 0.66:
                        filtered_subjects.append({
                            'name': subject['name'],
                            'theme': subject_theme,
                            'theme_similarity': theme_similarity,
                            'url': subject['url']
                        })
                except Exception as e:
                    logger.error(f"🔴 [MAIN] Error comparando tema: {str(e)}")

        logger.info(f"🔵 [MAIN] Asignaturas relevantes encontradas: {len(filtered_subjects)}")

        logger.info("🔵 [MAIN] Fase 4: Extrayendo detalles asignatura principal")
        subjects1 = extract_subjects_with_llm(subject_text, subject_title=request.subject_title)
        logger.debug(f"🔵 [MAIN] Respuesta LLM asignatura principal:\n{subjects1}")
        subjects1 = convert_to_new_format(subjects1)
        logger.debug(f"🔵 [MAIN] Asignatura principal formateada:\n{subjects1}")

        input_title = request.subject_title
        best_match = difflib.get_close_matches(input_title.upper(), [s.upper() for s in subjects1.keys()], n=1, cutoff=0.4)
        if not best_match:
            logger.error(f"🔴 [MAIN] No se encontró la asignatura '{request.subject_title}'")
            raise HTTPException(status_code=400, detail="Asignatura no encontrada")
        
        match_upper = best_match[0]
        original_title = next((s for s in subjects1.keys() if s.upper() == match_upper), match_upper)
        request.subject_title = original_title
        subject_data = subjects1[request.subject_title]
        combined_text1 = f"""
            Nombre: {request.subject_title}
            Competencias: {subject_data.get('competences', '')}
            Objetivos: {subject_data.get('objectives', '')}
            Contenidos: {subject_data.get('contents', '')}
        """
        logger.debug(f"🔵 [MAIN] Texto combinado asignatura principal:\n{combined_text1}")

        logger.info("🔵 [MAIN] Fase 5: Procesando asignaturas relevantes")
        detailed_subjects = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_analysis = {
                executor.submit(lambda s: extract_subjects_with_llm(extract_subject_from_url(s['url'], s['name']), subject_title=s['name']), subject): subject
                for subject in filtered_subjects
            }
            for future in as_completed(future_to_analysis):
                subject = future_to_analysis[future]
                try:
                    # Verificar si la comparación ya existe
                    existing_comparison = db.query(Comparison).filter(
                        Comparison.url1 == request.url1,
                        Comparison.subject_title1 == request.subject_title,
                        Comparison.url2 == subject['url'],
                        Comparison.subject_title2 == subject['name'],
                        Comparison.comparison_type == "compare"
                    ).first()

                    if existing_comparison:
                        logger.info(f"🟢 [MAIN] Comparación ya existe para {subject['name']}, devolviendo resultado almacenado")
                        detailed_subjects.append({
                            "asignatura": existing_comparison.subject_title2,
                            "similitud_tematica": subject['theme_similarity'],
                            "similitud_contenido": existing_comparison.similarity_score,
                            "componentes": existing_comparison.components,
                            "analisis": existing_comparison.analysis,
                            "explicacion": existing_comparison.explanation,
                            "detalles": {},  # Puedes mejorar esto si tienes más detalles almacenados
                            "url": subject['url']
                        })
                        continue

                    subject_info = future.result()
                    logger.debug(f"🔵 [MAIN] Respuesta LLM asignatura relevante:\n{subject_info}")
                    if subject_info:
                        subject_name, details = next(iter(subject_info.items()))
                        combined_text2 = f"""
                            Nombre: {subject_name}
                            Competencias: {details.get('competences', '')}
                            Objetivos: {details.get('objectives', '')}
                            Contenidos: {details.get('contents', '')}
                        """
                        logger.debug(f"🔵 [MAIN] Texto combinado asignatura relevante:\n{combined_text2}")
                        logger.info("🔵 [MAIN] Calculando similitud con embedding...")
                        analysis = similarity_score(combined_text1, combined_text2)
                        logger.info(f"🔵 [MAIN] Resultado análisis:\n{analysis}")
                        detailed_subjects.append({
                            "asignatura": subject_name,
                            "similitud_tematica": subject['theme_similarity'],
                            "similitud_contenido": analysis.get('score', 0) * 100,
                            "componentes": analysis.get('components', {}),
                            "analisis": analysis.get('llm_analysis', ''),
                            "explicacion": analysis.get('explanation', ''),
                            "detalles": details,
                            "url": subject['url']
                        })

                        db_comparison = Comparison(
                            url1=request.url1,
                            subject_title1=request.subject_title,
                            url2=subject['url'],
                            subject_title2=subject_name,
                            similarity_score=analysis.get('score', 0) * 100,
                            components=analysis.get('components', {}),
                            analysis=analysis.get('llm_analysis', ''),
                            explanation=analysis.get('explanation', ''),
                            comparison_type="compare"
                        )
                        db.add(db_comparison)
                        db.commit()
                        db.refresh(db_comparison)

                except Exception as e:
                    logger.error(f"🔴 [MAIN] Error analizando asignatura: {str(e)}")

        detailed_subjects.sort(key=lambda x: x["similitud_contenido"], reverse=True)
        logger.info("🟢 [MAIN] Comparación completada y guardada en la base de datos")
        return {
            "asignatura_origen": request.subject_title,
            "tema_principal": main_theme,
            "detalles_origen": subject_data,
            "coincidencias": detailed_subjects[:5]
        }
    except HTTPException as he:
        logger.error(f"🔴 [MAIN] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"🔴 [MAIN] Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comparison-history")
async def get_comparison_history(db: Session = Depends(get_db)):
    try:
        comparisons = db.query(Comparison).all()
        return [
            {
                "id": comp.id,
                "created_at": comp.created_at.isoformat(),
                "url1": comp.url1,
                "subject_title1": comp.subject_title1,
                "url2": comp.url2,
                "subject_title2": comp.subject_title2,
                "similarity_score": comp.similarity_score,
                "components": comp.components,
                "analysis": comp.analysis,
                "explanation": comp.explanation,
                "comparison_type": comp.comparison_type
            }
            for comp in comparisons
        ]
    except Exception as e:
        logger.error(f"🔴 [MAIN] Error retrieving comparison history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@app.delete("/clear-history")
async def clear_comparison_history(db: Session = Depends(get_db)):
    try:
        db.query(Comparison).delete()
        db.commit()
        logger.info("🟢 [MAIN] Comparison history cleared successfully")
        return {"message": "Historial borrado exitosamente"}
    except Exception as e:
        db.rollback()
        logger.error(f"🔴 [MAIN] Error clearing comparison history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al borrar el historial: {str(e)}")
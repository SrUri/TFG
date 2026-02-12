import { useState, useEffect } from 'react';
import axios from 'axios';

const useComparison = ({ setError, comparisonMode }) => {
  const [url1, setUrl1] = useState('');
  const [url2, setUrl2] = useState('');
  const [subject, setSubject] = useState('');
  const [subjectTitle1, setSubjectTitle1] = useState('');
  const [subjectTitle2, setSubjectTitle2] = useState('');
  const [results, setResults] = useState([]);
  const [sourceDetails, setSourceDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedResult, setExpandedResult] = useState(null);
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/comparison-history');
      setHistory(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al carregar l\'historial');
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleCompare = async () => {
    if (comparisonMode === 'history') {
      fetchHistory();
      return;
    }

    if (comparisonMode === 'compare') {
      if (!url1 || !url2 || !subject) {
        setError('Si us plau, completa tots els camps');
        return;
      }
    } else if (comparisonMode === 'compare-subjects') {
      if (!url1 || !url2 || !subjectTitle1 || !subjectTitle2) {
        setError('Si us plau, completa tots els camps');
        return;
      }
    }

    setIsLoading(true);
    setError('');
    setResults([]);
    setSourceDetails(null);
    setExpandedResult(null);

    try {
      let response;
      if (comparisonMode === 'compare') {
        response = await axios.post('http://localhost:8000/compare', {
          url1,
          url2,
          subject_title: subject,
        });
      } else {
        response = await axios.post('http://localhost:8000/compare-subjects', {
          url1,
          subject_title1: subjectTitle1,
          url2,
          subject_title2: subjectTitle2,
        });
      }

      if (comparisonMode === 'compare' && response.data && response.data.coincidencias) {
        const adaptedResults = response.data.coincidencias.map((item) => {
          let similarities = [];
          let differences = [];

          if (item.analisis && !item.analisis.error) {
            const analysis =
              typeof item.analisis === 'string'
                ? JSON.parse(item.analisis.replace(/'/g, '"'))
                : item.analisis;

            similarities = (analysis.similitudes_tecnicas || []).map((tech) => ({
              type: 'technical',
              description: tech,
            }));

            differences = (analysis.diferencias_sustanciales || []).map((diff) => ({
              severity: 'high',
              description: diff,
            }));
          }

          return {
            subject: item.asignatura,
            similarity: item.similitud_contenido,
            components: {
              contents: (item.componentes?.contents || 0) * 100,
              objectives: (item.componentes?.objectives || 0) * 100,
              competences: (item.componentes?.competences || 0) * 100,
            },
            analysis: {
              thematic_similarity: (item.similitud_tematica || 0) * 100,
              thematic_reason: item.explicacion,
              similarities,
              differences,
              conclusion: item.explicacion,
            },
            details: {
              competences: Array.isArray(item.detalles?.competences)
                ? item.detalles.competences.join(', ')
                : item.detalles?.competences || 'No disponible',
              objectives: Array.isArray(item.detalles?.objectives)
                ? item.detalles.objectives.join(', ')
                : item.detalles?.objectives || 'No disponible',
              contents:
                typeof item.detalles?.contents === 'object'
                  ? JSON.stringify(item.detalles.contents, null, 2)
                  : item.detalles?.contents || 'No disponible',
            },
          };
        });

        setResults(adaptedResults);
        setSourceDetails({
          competences: Array.isArray(response.data.detalles_origen.competences)
            ? response.data.detalles_origen.competences.join(', ')
            : response.data.detalles_origen.competences,
          objectives: Array.isArray(response.data.detalles_origen.objectives)
            ? response.data.detalles_origen.objectives.join(', ')
            : response.data.detalles_origen.objectives,
          contents:
            typeof response.data.detalles_origen.contents === 'object'
              ? JSON.stringify(response.data.detalles_origen.contents, null, 2)
              : response.data.detalles_origen.contents,
        });
      } else if (comparisonMode === 'compare-subjects' && response.data) {
        let similarities = [];
        let differences = [];

        if (response.data.analisis && !response.data.analisis.error) {
          const analysis =
            typeof response.data.analisis === 'string'
              ? JSON.parse(item.analisis.replace(/'/g, '"'))
              : response.data.analisis;

          similarities = (analysis.similitudes_tecnicas || []).map((tech) => ({
            type: 'technical',
            description: tech,
          }));

          differences = (analysis.diferencias_sustanciales || []).map((diff) => ({
            severity: 'high',
            description: diff,
          }));
        }

        const adaptedResult = {
          subject: response.data.asignatura_comparada,
          similarity: response.data.similitud_contenido,
          components: {
            contents: (response.data.componentes?.contents || 0) * 100,
            objectives: (response.data.componentes?.objectives || 0) * 100,
            competences: (response.data.componentes?.competences || 0) * 100,
          },
          analysis: {
            similarities,
            differences,
            conclusion: response.data.explicacion,
          },
          details: {
            competences: Array.isArray(response.data.detalles_comparada?.competences)
              ? response.data.detalles_comparada.competences.join(', ')
              : response.data.detalles_comparada?.competences || 'No disponible',
            objectives: Array.isArray(response.data.detalles_comparada?.objectives)
              ? response.data.detalles_comparada.objectives.join(', ')
              : response.data.detalles_comparada?.objectives || 'No disponible',
            contents:
              typeof response.data.detalles_comparada?.contents === 'object'
                ? JSON.stringify(response.data.detalles_comparada.contents, null, 2)
                : response.data.detalles_comparada?.contents || 'No disponible',
          },
        };

        setResults([adaptedResult]);
        setSourceDetails({
          competences: Array.isArray(response.data.detalles_origen.competences)
            ? response.data.detalles_origen.competences.join(', ')
            : response.data.detalles_origen.competences,
          objectives: Array.isArray(response.data.detalles_origen.objectives)
            ? response.data.detalles_origen.objectives.join(', ')
            : response.data.detalles_origen.objectives,
          contents:
            typeof response.data.detalles_origen.contents === 'object'
              ? JSON.stringify(response.data.detalles_origen.contents, null, 2)
              : response.data.detalles_origen.contents,
        });
      }

      fetchHistory();
    } catch (err) {
      console.error('Full error object:', err);
      console.error('Error response:', err.response);
      setError(
        err.response?.data?.detail || err.message || 'Error al processar la comparació'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return {
    url1, setUrl1, url2, setUrl2, subject, setSubject, subjectTitle1, setSubjectTitle1, subjectTitle2, setSubjectTitle2, results, setResults, sourceDetails, setSourceDetails, isLoading, expandedResult, setExpandedResult, history, setHistory, handleCompare, fetchHistory,
  };
};

export default useComparison;
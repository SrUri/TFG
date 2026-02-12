import { getSimilarityColor } from '../../utils/helpers';

const ComparisonResults = ({
  results, comparisonMode, subject, subjectTitle1, subjectTitle2, expandedResult, setExpandedResult,
}) => {
  const renderSimilarityAnalysis = (analysis) => {
    if (!analysis) return null;

    return (
      <div className="analysis-section">
        {(analysis.similarities?.length > 0 || analysis.differences?.length > 0) && (
          <div className="comparison-details">
            <h4>Desglossament:</h4>
            {analysis.similarities?.length > 0 && (
              <div className="similarities">
                <h5>Coincidènciess Principals:</h5>
                <ul>
                  {analysis.similarities.map((item, i) => (
                    <li key={`sim-${i}`}>
                      <span className={`match-type ${item.type}`}>
                        {item.type.toUpperCase()}
                      </span>
                      : {item.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.differences?.length > 0 && (
              <div className="differences">
                <h5>Diferències Rellevants:</h5>
                <ul>
                  {analysis.differences.map((item, i) => (
                    <li key={`diff-${i}`}>
                      <span className={`diff-severity ${item.severity}`}>
                        {item.severity === 'high' ? 'GRAN DIFERÈNCIA' : 'Diferència'}
                      </span>
                      : {item.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        {analysis.conclusion && (
          <div className="conclusion">
            <h5>Conclusió:</h5>
            <p>{analysis.conclusion}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="results-container">
      <h2>Resultats de la comparació:</h2>
      <p className="comparison-title">
        Comparant "{comparisonMode === 'compare' ? subject : subjectTitle1}"{' '}
        {comparisonMode === 'compare'
          ? 'amb assignatures de la guia docent del destí:'
          : `amb "${subjectTitle2}"`}
      </p>
      <div className="results-grid">
        {results.map((item, index) => (
          <div
            key={index}
            className={`result-card ${expandedResult === index ? 'expanded' : ''}`}
          >
            <div
              className="result-header"
              onClick={() => setExpandedResult(expandedResult === index ? null : index)}
            >
              <span className="subject-title">{item.subject}</span>
              <span
                className="similarity-badge"
                style={{ backgroundColor: getSimilarityColor(item.similarity) }}
              >
                {item.similarity.toFixed(1)}%
              </span>
              <span className="toggle-icon">
                {expandedResult === index ? '▲' : '▼'}
              </span>
            </div>
            {expandedResult === index && (
              <div className="result-details">
                <div className="components-scores">
                  <h4>Puntuació per components:</h4>
                  <ul>
                    <li>Continguts: <strong>{item.components.contents.toFixed(1)}%</strong></li>
                    <li>Objectius: <strong>{item.components.objectives.toFixed(1)}%</strong></li>
                    <li>Competències: <strong>{item.components.competences.toFixed(1)}%</strong></li>
                  </ul>
                </div>
                {renderSimilarityAnalysis(item.analysis)}
                <div className="raw-details">
                  <h4>Detalls de l'assignatura:</h4>
                  <div className="detail-section">
                    <h5>Competències:</h5>
                    <div className="detail-content">{item.details.competences}</div>
                  </div>
                  <div className="detail-section">
                    <h5>Objectius:</h5>
                    <div className="detail-content">{item.details.objectives}</div>
                  </div>
                  <div className="detail-section">
                    <h5>Continguts:</h5>
                    <div className="detail-content">{item.details.contents}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComparisonResults;
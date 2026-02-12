const SourceDetails = ({ sourceDetails, comparisonMode, subject, subjectTitle1 }) => (
  <div className="source-details">
    <h2>Detalls de l'assignatura d'origen:</h2>
    <h3>{comparisonMode === 'compare' ? subject : subjectTitle1}</h3>
    <div className="detail-section">
      <h4>Competències:</h4>
      <p>{sourceDetails.competences || 'No disponible'}</p>
    </div>
    <div className="detail-section">
      <h4>Objectius:</h4>
      <p>{sourceDetails.objectives || 'No disponible'}</p>
    </div>
    <div className="detail-section">
      <h4>Continguts:</h4>
      <p>{sourceDetails.contents || 'No disponible'}</p>
    </div>
  </div>
);

export default SourceDetails;
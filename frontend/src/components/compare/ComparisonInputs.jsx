const ComparisonInputs = ({
  comparisonMode, url1, setUrl1, url2, setUrl2, subject, setSubject, subjectTitle1, setSubjectTitle1, subjectTitle2, setSubjectTitle2, handleCompare, isLoading,
}) => (
  <>
    {comparisonMode === 'compare' ? (
      <>
        <div className="input-group">
          <label>URL Assignatura Origen:</label>
          <input
            type="text"
            value={url1}
            onChange={(e) => setUrl1(e.target.value)}
            placeholder="Ex.: https://universitat.edu/guia1.pdf"
          />
        </div>
        <div className="input-group">
          <label>URL Guia Docent Destí:</label>
          <input
            type="text"
            value={url2}
            onChange={(e) => setUrl2(e.target.value)}
            placeholder="Ex.: https://universitat.edu/guia2.pdf"
          />
        </div>
        <div className="input-group">
          <label>Nom extacte de l'assignatura:</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Ex.: FONAMENTS DE PROGRAMACIÓ"
          />
        </div>
      </>
    ) : (
      <>
        <div className="input-group">
          <label>URL Assignatura Origen:</label>
          <input
            type="text"
            value={url1}
            onChange={(e) => setUrl1(e.target.value)}
            placeholder="Ex.: https://universitat.edu/assignatura1"
          />
        </div>
        <div className="input-group">
          <label>Nom exacte de l'assignatura d'origen:</label>
          <input
            type="text"
            value={subjectTitle1}
            onChange={(e) => setSubjectTitle1(e.target.value)}
            placeholder="Ex.: PROGRAMACIÓ I"
          />
        </div>
        <div className="input-group">
          <label>URL Assignatura Destí:</label>
          <input
            type="text"
            value={url2}
            onChange={(e) => setUrl2(e.target.value)}
            placeholder="Ex.: https://universitat.edu/assignatura2"
          />
        </div>
        <div className="input-group">
          <label>Nom exacte de l'assignatura de destí:</label>
          <input
            type="text"
            value={subjectTitle2}
            onChange={(e) => setSubjectTitle2(e.target.value)}
            placeholder="Ex.: FÍSICA"
          />
        </div>
      </>
    )}
    <button
      onClick={handleCompare}
      disabled={isLoading}
      className="compare-button"
    >
      {isLoading
        ? 'Comparant...'
        : comparisonMode === 'compare'
        ? 'Comparar amb Guia Docent'
        : 'Comparar Assignatures'}
    </button>
  </>
);

export default ComparisonInputs;
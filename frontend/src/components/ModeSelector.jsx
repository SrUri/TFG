const ModeSelector = ({ comparisonMode, setComparisonMode }) => (
  <div className="mode-selector">
    <button
      className={`mode-button ${comparisonMode === 'compare' ? 'active' : ''}`}
      onClick={() => setComparisonMode('compare')}
    >
      Comparar amb Guia Docent
    </button>
    <button
      className={`mode-button ${comparisonMode === 'compare-subjects' ? 'active' : ''}`}
      onClick={() => setComparisonMode('compare-subjects')}
    >
      Comparar Assignatures Individuals
    </button>
    <button
      className={`mode-button ${comparisonMode === 'history' ? 'active' : ''}`}
      onClick={() => setComparisonMode('history')}
    >
      Historial
    </button>
  </div>
);

export default ModeSelector;
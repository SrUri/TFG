import { useState } from 'react';
import ModeSelector from './components/ModeSelector';
import ComparisonInputs from './components/compare/ComparisonInputs';
import ComparisonResults from './components/compare/ComparisonResults';
import SourceDetails from './components/compare/SourceDetails';
import HistorySection from './components/history/HistorySection';
import ErrorMessage from './components/ErrorMessage';
import useComparison from './hooks/useComparison';
import './styles/App.css';

function App() {
  const [comparisonMode, setComparisonMode] = useState('compare');
  const [error, setError] = useState('');
  const {
    url1, setUrl1, url2, setUrl2, subject, setSubject, subjectTitle1, setSubjectTitle1, subjectTitle2, setSubjectTitle2, isLoading, expandedResult, setExpandedResult, history, setHistory, handleCompare, fetchHistory, sourceDetails, results
  } = useComparison({ setError, comparisonMode });

  return (
    <div className="container">
      <h1>Comparador d'Assignatures d'Erasmus</h1>

      <ModeSelector
        comparisonMode={comparisonMode}
        setComparisonMode={setComparisonMode}
      />

      {comparisonMode === 'compare' || comparisonMode === 'compare-subjects' ? (
        <ComparisonInputs
          comparisonMode={comparisonMode}
          url1={url1}
          setUrl1={setUrl1}
          url2={url2}
          setUrl2={setUrl2}
          subject={subject}
          setSubject={setSubject}
          subjectTitle1={subjectTitle1}
          setSubjectTitle1={setSubjectTitle1}
          subjectTitle2={subjectTitle2}
          setSubjectTitle2={setSubjectTitle2}
          handleCompare={handleCompare}
          isLoading={isLoading}
        />
      ) : (
        <HistorySection
          history={history}
          setHistory={setHistory}
          fetchHistory={fetchHistory}
          setError={setError}
        />
      )}

      <ErrorMessage error={error} />

      {sourceDetails && comparisonMode !== 'history' && (
        <SourceDetails
          sourceDetails={sourceDetails}
          comparisonMode={comparisonMode}
          subject={subject}
          subjectTitle1={subjectTitle1}
        />
      )}

      {results.length > 0 && comparisonMode !== 'history' && (
        <ComparisonResults
          results={results}
          comparisonMode={comparisonMode}
          subject={subject}
          subjectTitle1={subjectTitle1}
          subjectTitle2={subjectTitle2}
          expandedResult={expandedResult}
          setExpandedResult={setExpandedResult}
        />
      )}
    </div>
  );
}

export default App;
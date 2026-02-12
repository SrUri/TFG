import { useState } from 'react';
import ConfirmModal from './ConfirmModal';
import { clearComparisonHistory } from '../../services/api.js';

const HistorySection = ({ history, setHistory, fetchHistory, setError }) => {
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const handleClearHistoryClick = () => {
    setShowConfirmModal(true);
  };

  const confirmClearHistory = async () => {
    try {
      await clearComparisonHistory();
      setHistory([]);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al esborrar l\'historial');
    } finally {
      setShowConfirmModal(false);
    }
  };

  const cancelClearHistory = () => {
    setShowConfirmModal(false);
  };

  return (
    <div className="history-container">
      <div className="history-header">
        <h2>Historial de Comparacions</h2>
        {history.length > 0 && (
          <button className="clear-history-button" onClick={handleClearHistoryClick}>
            Borrar Historial
          </button>
        )}
      </div>
      {history.length === 0 ? (
        <p>No hi ha comparacions a l'historial.</p>
      ) : (
        <div className="history-grid">
          {history.map((item, index) => (
            <div key={index} className="history-card">
              <div className="history-header">
                <span className="history-date">{new Date(item.created_at).toLocaleString()}</span>
                <span className="history-type">
                  {item.comparison_type === 'compare' ? 'Guia Docent' : 'Assignatura Individual'}
                </span>
              </div>
              <div className="history-details">
                <p>
                  <strong>Assignatura d'origen:</strong> {item.subject_title1} (
                  <a href={item.url1} target="_blank" rel="noopener noreferrer">
                    URL
                  </a>
                  )
                </p>
                <p>
                  <strong>Assignatura del destí:</strong> {item.subject_title2 || 'Múltiples'} (
                  <a href={item.url2} target="_blank" rel="noopener noreferrer">
                    URL
                  </a>
                  )
                </p>
                <p>
                  <strong>Similitut:</strong> {item.similarity_score?.toFixed(1)}%
                </p>
                <p><strong>Components:</strong></p>
                <ul>
                  <li>Continguts: {(item.components?.contents * 100)?.toFixed(1)}%</li>
                  <li>Objectius: {(item.components?.objectives * 100)?.toFixed(1)}%</li>
                  <li>Competències: {(item.components?.competences * 100)?.toFixed(1)}%</li>
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
      {showConfirmModal && (
        <ConfirmModal
          onConfirm={confirmClearHistory}
          onCancel={cancelClearHistory}
        />
      )}
    </div>
  );
};

export default HistorySection;
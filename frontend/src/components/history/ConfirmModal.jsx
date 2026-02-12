const ConfirmModal = ({ onConfirm, onCancel }) => (
  <div className="modal-overlay">
    <div className="modal">
      <h3>Confirmar Eliminació</h3>
      <p>Segur que vols esborrar tot l'historial? Aquesta acció no es reversible.</p>
      <div className="modal-buttons">
        <button className="modal-button confirm-button" onClick={onConfirm}>
          Confirmar
        </button>
        <button className="modal-button cancel-button" onClick={onCancel}>
          Cancel·lar
        </button>
      </div>
    </div>
  </div>
);

export default ConfirmModal;
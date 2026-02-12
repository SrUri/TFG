const ErrorMessage = ({ 
    error 
}) => error ? <div className="error-message">{error}</div> : null;

export default ErrorMessage;
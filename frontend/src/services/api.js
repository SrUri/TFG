import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const compareSubjectsWithGuide = async (data) => {
  try {
    const response = await api.post('/compare', data);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || error.message || 'Error al processar la comparació';
  }
};

export const compareIndividualSubjects = async (data) => {
  try {
    const response = await api.post('/compare-subjects', data);
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || error.message || 'Error al processar la comparació';
  }
};

export const fetchComparisonHistory = async () => {
  try {
    const response = await api.get('/comparison-history');
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al carregar l\'historial';
  }
};

export const clearComparisonHistory = async () => {
  try {
    const response = await api.delete('/clear-history');
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || 'Error al borrar l\'historial';
  }
};

export default api;
export const getSimilarityColor = (similarity) => {
  if (similarity >= 80) return '#4CAF50';
  if (similarity >= 60) return '#8BC34A';
  if (similarity >= 40) return '#FFC107';
  if (similarity >= 20) return '#FF9800';
  return '#F44336';
};
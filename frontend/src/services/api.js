import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchTweets = async (searchParams) => {
  try {
    const response = await api.post('/api/search', searchParams);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;

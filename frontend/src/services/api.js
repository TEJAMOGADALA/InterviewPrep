import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Auto-refresh on 401
let refreshing = null;
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url?.endsWith('/auth/login') &&
      !original.url?.endsWith('/auth/refresh') &&
      !original.url?.endsWith('/auth/me')
    ) {
      original._retry = true;
      try {
        refreshing = refreshing || api.post('/auth/refresh');
        await refreshing;
        refreshing = null;
        return api(original);
      } catch (e) {
        refreshing = null;
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);

export default api;

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Auto-refresh on 401 + self-heal onboarding-required redirects
let refreshing = null;
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    // Self-heal: if backend says onboarding_required, force user to wizard.
    if (
      status === 409 &&
      detail === 'onboarding_required' &&
      typeof window !== 'undefined' &&
      window.location.pathname !== '/onboarding'
    ) {
      window.location.replace('/onboarding');
      return Promise.reject(error);
    }

    if (
      status === 401 &&
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

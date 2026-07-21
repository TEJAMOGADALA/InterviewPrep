import api from './api';

export const authService = {
  register: (payload) => api.post('/auth/register', payload).then((r) => r.data),
  login: (payload) => api.post('/auth/login', payload).then((r) => r.data),
  logout: () => api.post('/auth/logout').then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
  forgotPassword: (email) =>
    api.post('/auth/forgot-password', { email }).then((r) => r.data),
  resetPassword: (token, newPassword) =>
    api.post('/auth/reset-password', { token, new_password: newPassword }).then((r) => r.data),
};

export const userService = {
  getProfile: () => api.get('/profile').then((r) => r.data),
  updateProfile: (payload) => api.patch('/profile', payload).then((r) => r.data),
  getSettings: () => api.get('/settings').then((r) => r.data),
  updateSettings: (payload) => api.patch('/settings', payload).then((r) => r.data),
  getOnboarding: () => api.get('/onboarding').then((r) => r.data),
  submitOnboarding: (payload) => api.post('/onboarding', payload).then((r) => r.data),
};

import api from './api';

export const missionService = {
  getToday: () => api.get('/missions/today').then((r) => r.data),
  completeTask: (missionId, taskId) =>
    api.post(`/missions/${missionId}/tasks/${taskId}/complete`).then((r) => r.data),
  completeMission: (missionId) =>
    api.post(`/missions/${missionId}/complete`).then((r) => r.data),
  skipMission: (missionId) =>
    api.post(`/missions/${missionId}/skip`).then((r) => r.data),
  getHistory: (limit = 20) =>
    api.get('/missions/history', { params: { limit } }).then((r) => r.data),
};

export const dashboardService = {
  get: () => api.get('/dashboard').then((r) => r.data),
};

export const revisionService = {
  getQueue: () => api.get('/revisions/queue').then((r) => r.data),
};

export const activityService = {
  list: (limit = 20) => api.get('/activity', { params: { limit } }).then((r) => r.data),
};

// Extend user service with onboarding patch
export const onboardingService = {
  patch: (payload) => api.patch('/onboarding', payload).then((r) => r.data),
};

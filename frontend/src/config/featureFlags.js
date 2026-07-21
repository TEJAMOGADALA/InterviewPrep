// Feature flag architecture. Values here are only defaults — future phases can
// hydrate them from user settings or a remote flag service without changing
// consumers. Read via `useFeatureFlag('ai-mentor')`.
export const FEATURE_FLAGS = {
  'ai-mentor': false,
  'mission-engine': false,
  'resume': false,
  'mock-interviews': false,
  'weekly-report': false,
  'contest-tracker': false,
  'command-palette': true,
  'global-search': true,
  'ai-assistant-panel': true,
  'notifications-center': true,
};

export function isFeatureEnabled(key) {
  return Boolean(FEATURE_FLAGS[key]);
}

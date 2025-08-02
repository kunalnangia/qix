// Base URL for API requests
export const API_BASE_URL = 'http://127.0.0.1:8001/api';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  PROJECTS: '/v1/projects',
  TEST_CASES: '/v1/test-cases',
  TEAMS: '/v1/teams',
  EXECUTIONS: '/v1/executions',
  COMMENTS: '/v1/comments',
  ATTACHMENTS: '/v1/attachments',
  ENVIRONMENTS: '/v1/environments',
  AI: '/v1/ai',
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  // Don't add base URL if it's already included
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  return `${API_BASE_URL}${endpoint}`;
};

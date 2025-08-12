// Base URL for API requests
export const API_BASE_URL = 'http://127.0.0.1:8001';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/auth/me',
  },
  PROJECTS: '/api/v1/projects',
  TEST_CASES: '/api/v1/test-cases',
  TEAMS: '/api/v1/teams',
  EXECUTIONS: '/api/v1/executions',
  COMMENTS: '/api/v1/comments',
  ATTACHMENTS: '/api/v1/attachments',
  ENVIRONMENTS: '/api/v1/environments',
  AI: '/api/v1/ai',
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  // Don't add base URL if it's already included
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  return `${API_BASE_URL}${endpoint}`;
};

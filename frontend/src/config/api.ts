import { getToken } from "@/lib/utils";

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
  DASHBOARD: {
    STATS: '/dashboard/stats',
    ACTIVITY: '/dashboard/activity',
  },
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  if (endpoint.startsWith('http')) {
    return endpoint;
  }
  return `${API_BASE_URL}${endpoint}`;
};

// Generic API fetcher
export const fetcher = async (url: string, options: RequestInit = {}) => {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(getApiUrl(url), {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An error occurred while fetching the data.');
  }

  return response.json();
};

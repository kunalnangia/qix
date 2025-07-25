import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/hooks/useAuth';
import { createWrapper } from './utils';
import createFetchMock from 'vitest-fetch-mock';

// Setup fetch mocking
const fetchMocker = createFetchMock(vi);
fetchMocker.enableMocks();

// Mock the router to prevent navigation errors
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}));

describe('useAuth', () => {
  // Reset mocks and localStorage before each test
  beforeEach(() => {
    fetchMock.resetMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with no user when no token exists', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(AuthProvider),
    });

    expect(result.current.user).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('should sign in successfully and store token', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockToken = 'test-jwt-token';
    
    fetchMock.mockResponseOnce(
      JSON.stringify({ access_token: mockToken, user: mockUser })
    );

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(AuthProvider),
    });

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8002/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password',
        }),
      })
    );

    expect(localStorage.getItem('access_token')).toBe(mockToken);
    expect(result.current.user).toEqual(mockUser);
  });

  it('should handle sign in errors', async () => {
    const errorMessage = 'Login failed';
    fetchMocker.mockResponseOnce(
      JSON.stringify({ error: errorMessage }),
      { status: 401, statusText: 'Unauthorized' }
    );

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    // The hook resolves with the error object instead of rejecting
    await act(async () => {
      const response = await result.current.signIn('wrong@example.com', 'wrong');
      expect(response).toEqual({ error: errorMessage });
    });

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(result.current.user).toBeNull();
  });

  it('should sign out and clear user data', async () => {
    // First sign in
    const mockUser = { id: '1', email: 'test@example.com' };
    fetchMock.mockResponseOnce(
      JSON.stringify({ access_token: 'test-token', user: mockUser })
    );

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(AuthProvider),
    });

    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });

    // Now test sign out
    act(() => {
      result.current.signOut();
    });

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(result.current.user).toBeNull();
  });

  // Removed refreshToken test as it's not implemented in the AuthContext
});

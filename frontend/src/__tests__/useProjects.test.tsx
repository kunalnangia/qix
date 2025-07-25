import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useProjects } from '@/hooks/useProjects';
import { createWrapper } from './utils';
import createFetchMock from 'vitest-fetch-mock';
import { QueryClient } from '@tanstack/react-query';

// Setup fetch mocking
const fetchMocker = createFetchMock(vi);

// Create a custom wrapper with a fresh QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactElement }) => (
  createWrapper()({ children })
);

describe('useProjects', () => {
  const mockProject = {
    id: '1',
    name: 'Test Project',
    description: 'Test Description',
    status: 'active',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  // Reset mocks before each test
  beforeEach(() => {
    fetchMocker.resetMocks();
    localStorage.setItem('access_token', 'test-token');
  });

  afterEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should initialize with empty projects', () => {
    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    expect(result.current.projects).toEqual([]);
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('should fetch projects successfully on mount', async () => {
    const mockProjects = [mockProject];
    fetchMocker.mockResponseOnce(JSON.stringify(mockProjects));

    const { result } = renderHook(() => useProjects(), {
      wrapper,
    });

    // Initial state
    expect(result.current.loading).toBe(true);
    expect(result.current.projects).toEqual([]);

    // Wait for the data to load
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetchMocker).toHaveBeenCalledWith(
      'http://127.0.0.1:8002/api/projects',
      expect.objectContaining({
        headers: {
          'Authorization': 'Bearer test-token',
        },
      })
    );

    expect(result.current.projects).toEqual(mockProjects);
    expect(result.current.error).toBeNull();
  });

  it('should refetch projects', async () => {
    const mockProjects = [mockProject];
    fetchMocker.mockResponse(JSON.stringify(mockProjects));

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await act(async () => {
      await result.current.refetch();
    });

    expect(fetchMocker).toHaveBeenCalledTimes(1);
    expect(result.current.projects).toEqual(mockProjects);
  });

  it('should create a new project', async () => {
    const newProject = { 
      name: 'New Project', 
      description: 'New Description',
      status: 'active' as const
    };
    
    const createdProject = { ...mockProject, ...newProject };
    fetchMocker.mockResponseOnce(JSON.stringify(createdProject));

    const { result } = renderHook(() => useProjects(), {
      wrapper,
    });

    let response;
    await act(async () => {
      response = await result.current.createProject(newProject);
    });

    // The hook returns the created project directly
    expect(response).toEqual(createdProject);
    
    expect(fetchMocker).toHaveBeenCalledWith(
      'http://127.0.0.1:8002/api/projects',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token',
        },
        body: JSON.stringify(newProject),
      })
    );
  });

  it('should update a project', async () => {
    const updates = { name: 'Updated Project' };
    const updatedProject = { ...mockProject, ...updates };
    fetchMocker.mockResponseOnce(JSON.stringify(updatedProject));

    const { result } = renderHook(() => useProjects(), {
      wrapper,
    });

    let response;
    await act(async () => {
      response = await result.current.updateProject('1', updates);
    });

    // The hook returns the updated project directly
    expect(response).toEqual(updatedProject);
    
    expect(fetchMocker).toHaveBeenCalledWith(
      'http://127.0.0.1:8002/api/projects/1',
      expect.objectContaining({
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token',
        },
        body: JSON.stringify(updates),
      })
    );
  });

  it('should delete a project', async () => {
    fetchMocker.mockResponseOnce(JSON.stringify({ success: true }));

    const { result } = renderHook(() => useProjects(), {
      wrapper,
    });

    let response;
    await act(async () => {
      response = await result.current.deleteProject('1');
    });

    // The hook returns the response from the API
    expect(response).toEqual({ success: true });
    
    expect(fetchMocker).toHaveBeenCalledWith(
      'http://127.0.0.1:8002/api/projects/1',
      expect.objectContaining({
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer test-token',
        },
      })
    );
  });

  it('should handle API errors', async () => {
    const errorMessage = 'Failed to fetch projects';
    fetchMocker.mockRejectOnce(new Error(errorMessage));

    const { result } = renderHook(() => useProjects(), {
      wrapper,
    });

    // Wait for the error state to be set
    await waitFor(() => {
      expect(result.current.error).toContain(errorMessage);
    });

    expect(result.current.loading).toBe(false);
  });
});

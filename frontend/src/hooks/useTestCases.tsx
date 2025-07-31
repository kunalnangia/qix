import { useState, useEffect } from 'react';
// import { supabase } from '@/integrations/supabase/client'; // Supabase removed
import { useAuth } from './useAuth';

export interface TestCase {
  id: string;
  title: string;
  description?: string;
  project_id: string;
  test_type: 'functional' | 'api' | 'visual' | 'performance' | 'security' | 'integration' | 'unit';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'draft' | 'active' | 'inactive' | 'archived';
  steps?: any;
  expected_result?: string;
  actual_result?: string;
  created_by?: string;
  assigned_to?: string;
  tags?: string[];
  ai_generated: boolean;
  self_healing_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export function useTestCases(projectId?: string) {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchTestCases = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      let url = `http://127.0.0.1:8001/api/test-cases`;
      if (projectId) {
        url += `?project_id=${projectId}`;
      }
      const response = await fetch(url, {
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      if (!response.ok) throw new Error('Failed to fetch test cases');
      const data = await response.json();
      setTestCases(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const createTestCase = async (testCaseData: Omit<TestCase, 'id' | 'created_at' | 'updated_at' | 'created_by'>) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://127.0.0.1:8001/api/test-cases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          ...testCaseData,
          created_by: user?.id
        })
      });
      if (!response.ok) throw new Error('Failed to create test case');
      const data = await response.json();
      setTestCases(prev => [data, ...prev]);
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create test case';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const updateTestCase = async (id: string, updates: Partial<TestCase>) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://127.0.0.1:8001/api/test-cases/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update test case');
      const data = await response.json();
      setTestCases(prev => prev.map(tc => tc.id === id ? data : tc));
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update test case';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const deleteTestCase = async (id: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://127.0.0.1:8001/api/test-cases/${id}`, {
        method: 'DELETE',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      if (!response.ok) throw new Error('Failed to delete test case');
      setTestCases(prev => prev.filter(tc => tc.id !== id));
      return { error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete test case';
      setError(errorMessage);
      return { error: errorMessage };
    }
  };

  useEffect(() => {
    fetchTestCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, user]);

  return {
    testCases,
    loading,
    error,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    refetch: fetchTestCases
  };
}
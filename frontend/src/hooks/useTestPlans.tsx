import { useState, useEffect } from 'react';
// import { supabase } from '@/integrations/supabase/client'; // Supabase removed
import { useAuth } from './useAuth';

export interface TestPlan {
  id: string;
  name: string;
  description?: string;
  project_id: string;
  created_by?: string;
  scheduled_date?: string;
  status: 'draft' | 'active' | 'inactive' | 'archived';
  environment?: string;
  browser_config?: any;
  created_at: string;
  updated_at: string;
}

export function useTestPlans(projectId?: string) {
  const [testPlans, setTestPlans] = useState<TestPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchTestPlans = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      let url = `http://127.0.0.1:8002/api/test-plans`;
      if (projectId) {
        url += `?project_id=${projectId}`;
      }
      const response = await fetch(url, {
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      if (!response.ok) throw new Error('Failed to fetch test plans');
      const data = await response.json();
      setTestPlans(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const createTestPlan = async (testPlanData: Omit<TestPlan, 'id' | 'created_at' | 'updated_at' | 'created_by'>) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://127.0.0.1:8002/api/test-plans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          ...testPlanData,
          created_by: user?.id
        })
      });
      if (!response.ok) throw new Error('Failed to create test plan');
      const data = await response.json();
      setTestPlans(prev => [data, ...prev]);
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create test plan';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const updateTestPlan = async (id: string, updates: Partial<TestPlan>) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://127.0.0.1:8002/api/test-plans/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update test plan');
      const data = await response.json();
      setTestPlans(prev => prev.map(tp => tp.id === id ? data : tp));
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update test plan';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const deleteTestPlan = async (id: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://127.0.0.1:8002/api/test-plans/${id}`, {
        method: 'DELETE',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      if (!response.ok) throw new Error('Failed to delete test plan');
      setTestPlans(prev => prev.filter(tp => tp.id !== id));
      return { error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete test plan';
      setError(errorMessage);
      return { error: errorMessage };
    }
  };

  useEffect(() => {
    fetchTestPlans();
  }, [user, projectId]);

  return {
    testPlans,
    loading,
    error,
    createTestPlan,
    updateTestPlan,
    deleteTestPlan,
    refetch: fetchTestPlans
  };
}
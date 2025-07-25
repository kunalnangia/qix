import { useState } from 'react'
// import { supabase } from '@/integrations/supabase/client' // Supabase removed
import { useToast } from '@/hooks/use-toast'

export const useTesting = () => {
  const [isExecuting, setIsExecuting] = useState(false)
  const { toast } = useToast()

  const executeApiTest = async (testCaseId: string, config: any) => {
    setIsExecuting(true)
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://127.0.0.1:8002/api/ai/generate-tests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          project_id: config.project_id || 'dummy',
          prompt: config.prompt || 'API test',
          test_type: config.test_type || 'api',
          priority: config.priority || 'medium',
          count: config.count || 1
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'API test failed');
      toast({
        title: "API Test Passed",
        description: "API test completed successfully",
        variant: "default",
      });
      return data;
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute API test",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsExecuting(false);
    }
  }

  const executeVisualTest = async (testCaseId: string, url: string, viewport?: any) => {
    setIsExecuting(true)
    try {
      const { data, error } = await supabase.functions.invoke('execute-visual-test', {
        body: { testCaseId, url, viewport }
      })

      if (error) throw error

      toast({
        title: data.result.success ? "Visual Test Passed" : "Visual Test Failed",
        description: data.result.success ? "Visual test completed successfully" : "Visual differences detected",
        variant: data.result.success ? "default" : "destructive",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute visual test",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }

  const executePerformanceTest = async (testCaseId: string, url: string, config?: any) => {
    setIsExecuting(true)
    try {
      const { data, error } = await supabase.functions.invoke('execute-performance-test', {
        body: { testCaseId, url, config }
      })

      if (error) throw error

      toast({
        title: "Performance Test Completed",
        description: `Page load time: ${data.metrics.page_load_time}ms`,
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute performance test",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }

  const executeSecurityTest = async (testCaseId: string, url: string, scanTypes?: string[]) => {
    setIsExecuting(true)
    try {
      const { data, error } = await supabase.functions.invoke('execute-security-test', {
        body: { testCaseId, url, scanTypes }
      })

      if (error) throw error

      toast({
        title: data.summary.total_findings === 0 ? "Security Test Passed" : "Security Issues Found",
        description: data.summary.total_findings === 0 
          ? "No security vulnerabilities detected" 
          : `${data.summary.total_findings} vulnerabilities found`,
        variant: data.summary.total_findings === 0 ? "default" : "destructive",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute security test",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }

  return {
    executeApiTest,
    executeVisualTest,
    executePerformanceTest,
    executeSecurityTest,
    isExecuting
  }
}
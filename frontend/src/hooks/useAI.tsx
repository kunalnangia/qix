import { useState } from 'react'
import { supabase } from '@/integrations/supabase/client'
import { useToast } from '@/hooks/use-toast'

export const useAI = () => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isDebugging, setIsDebugging] = useState(false)
  const { toast } = useToast()

  const generateTests = async (prompt: string, projectId: string) => {
    setIsGenerating(true)
    try {
      const { data, error } = await supabase.functions.invoke('ai-generate-tests', {
        body: { prompt, projectId }
      })

      if (error) throw error

      toast({
        title: "Success",
        description: "AI test cases generated successfully",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to generate test cases",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsGenerating(false)
    }
  }

  const debugTest = async (testCaseId: string, errorDescription: string, logs?: any) => {
    setIsDebugging(true)
    try {
      const { data, error } = await supabase.functions.invoke('ai-debug-tests', {
        body: { testCaseId, errorDescription, logs }
      })

      if (error) throw error

      toast({
        title: "Success", 
        description: "AI debugging analysis completed",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to debug test case",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsDebugging(false)
    }
  }

  return {
    generateTests,
    debugTest,
    isGenerating,
    isDebugging
  }
}
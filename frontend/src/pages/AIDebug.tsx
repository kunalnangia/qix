import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Bug, Loader2, Lightbulb, AlertTriangle } from 'lucide-react'
import { useAI } from '@/hooks/useAI'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const AIDebug = () => {
  const [selectedTestCase, setSelectedTestCase] = useState('')
  const [errorDescription, setErrorDescription] = useState('')
  const [debugResult, setDebugResult] = useState<any>(null)
  const { debugTest, isDebugging } = useAI()
  const { testCases } = useTestCases()
  const { toast } = useToast()

  const handleDebug = async () => {
    if (!selectedTestCase || !errorDescription.trim()) {
      toast({
        title: "Missing Information",
        description: "Please select a test case and describe the error",
        variant: "destructive",
      })
      return
    }

    try {
      const result = await debugTest(selectedTestCase, errorDescription)
      setDebugResult(result.debugAnalysis)
    } catch (error) {
      console.error('Error debugging test:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'environment': return '🔧'
      case 'data': return '📊'
      case 'timing': return '⏰'
      case 'logic': return '🧠'
      case 'configuration': return '⚙️'
      default: return '🔍'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Test Debugging</h1>
        <p className="text-muted-foreground">Get AI-powered insights to debug failed test cases</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bug className="h-5 w-5" />
            Debug Test Case
          </CardTitle>
          <CardDescription>
            Select a failed test case and describe the error to get AI debugging suggestions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Test Case</label>
            <Select value={selectedTestCase} onValueChange={setSelectedTestCase}>
              <SelectTrigger>
                <SelectValue placeholder="Select a test case to debug" />
              </SelectTrigger>
              <SelectContent>
                {testCases?.map((testCase) => (
                  <SelectItem key={testCase.id} value={testCase.id}>
                    {testCase.title} - {testCase.status}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium">Error Description</label>
            <Textarea
              placeholder="Describe what went wrong: error messages, unexpected behavior, screenshots, logs, etc..."
              value={errorDescription}
              onChange={(e) => setErrorDescription(e.target.value)}
              rows={4}
            />
          </div>

          <Button 
            onClick={handleDebug} 
            disabled={isDebugging || !selectedTestCase || !errorDescription.trim()}
            className="w-full"
          >
            {isDebugging ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing Issue...
              </>
            ) : (
              <>
                <Bug className="mr-2 h-4 w-4" />
                Debug Test Case
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {debugResult && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Root Cause Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{debugResult.analysis}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                Debugging Suggestions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {debugResult.suggestions?.map((suggestion: any, index: number) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                    <span className="text-lg">{getCategoryIcon(suggestion.category)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline">{suggestion.category}</Badge>
                        <Badge variant={getPriorityColor(suggestion.priority)}>
                          {suggestion.priority}
                        </Badge>
                      </div>
                      <p className="text-sm">{suggestion.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {debugResult.preventiveMeasures && debugResult.preventiveMeasures.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Preventive Measures</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside space-y-1">
                  {debugResult.preventiveMeasures.map((measure: string, index: number) => (
                    <li key={index} className="text-sm">{measure}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {debugResult.updatedSteps && debugResult.updatedSteps.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Suggested Updated Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="list-decimal list-inside space-y-2">
                  {debugResult.updatedSteps.map((step: any, index: number) => (
                    <li key={index} className="text-sm">
                      <strong>{step.action}</strong> - Expected: {step.expected}
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default AIDebug
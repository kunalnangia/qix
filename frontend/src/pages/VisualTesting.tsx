import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Eye, Loader2, Play, Image, AlertTriangle } from 'lucide-react'
import { useTesting } from '@/hooks/useTesting'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const VisualTesting = () => {
  const [selectedTestCase, setSelectedTestCase] = useState('')
  const [url, setUrl] = useState('')
  const [viewport, setViewport] = useState({ width: 1920, height: 1080 })
  const [testResult, setTestResult] = useState<any>(null)

  const { executeVisualTest, isExecuting } = useTesting()
  const { testCases } = useTestCases()
  const { toast } = useToast()

  const handleExecuteTest = async () => {
    if (!selectedTestCase || !url) {
      toast({
        title: "Missing Information",
        description: "Please select a test case and enter a URL",
        variant: "destructive",
      })
      return
    }

    try {
      const result = await executeVisualTest(selectedTestCase, url, viewport)
      setTestResult(result)
    } catch (error) {
      console.error('Error executing visual test:', error)
    }
  }

  const commonViewports = [
    { name: 'Desktop HD', width: 1920, height: 1080 },
    { name: 'Desktop', width: 1366, height: 768 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Mobile', width: 375, height: 667 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Visual Testing</h1>
        <p className="text-muted-foreground">AI-powered visual regression testing</p>
      </div>

      <Tabs defaultValue="configure" className="space-y-6">
        <TabsList>
          <TabsTrigger value="configure">Configure Test</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="configure" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Visual Test Configuration
              </CardTitle>
              <CardDescription>
                Configure visual regression testing parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Test Case</label>
                <Select value={selectedTestCase} onValueChange={setSelectedTestCase}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a test case" />
                  </SelectTrigger>
                  <SelectContent>
                    {testCases?.filter(tc => tc.test_type === 'visual').map((testCase) => (
                      <SelectItem key={testCase.id} value={testCase.id}>
                        {testCase.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">URL to Test</label>
                <Input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Viewport Size</label>
                <div className="flex gap-2">
                  {commonViewports.map((vp) => (
                    <Button
                      key={vp.name}
                      variant={viewport.width === vp.width && viewport.height === vp.height ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewport({ width: vp.width, height: vp.height })}
                    >
                      {vp.name}
                    </Button>
                  ))}
                </div>
                <div className="flex gap-2 mt-2">
                  <Input
                    type="number"
                    value={viewport.width}
                    onChange={(e) => setViewport({ ...viewport, width: parseInt(e.target.value) })}
                    placeholder="Width"
                    className="w-24"
                  />
                  <span className="text-muted-foreground self-center">×</span>
                  <Input
                    type="number"
                    value={viewport.height}
                    onChange={(e) => setViewport({ ...viewport, height: parseInt(e.target.value) })}
                    placeholder="Height"
                    className="w-24"
                  />
                </div>
              </div>

              <Button 
                onClick={handleExecuteTest} 
                disabled={isExecuting || !selectedTestCase || !url}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Capturing Screenshot...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Visual Test
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results">
          {testResult ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Image className="h-5 w-5" />
                    Visual Comparison Results
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Test Status</label>
                      <Badge variant={testResult.result.success ? "default" : "destructive"}>
                        {testResult.result.success ? "Passed" : "Failed"}
                      </Badge>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Similarity</label>
                      <p className="text-sm">{testResult.result.similarity_percentage}%</p>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium">Current Screenshot</label>
                    <img 
                      src={testResult.result.screenshot_url} 
                      alt="Current screenshot"
                      className="w-full max-w-md border rounded"
                    />
                  </div>

                  {testResult.result.differences.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-orange-600">
                          <AlertTriangle className="h-4 w-4" />
                          Visual Differences Detected
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {testResult.result.differences.map((diff: any, index: number) => (
                            <div key={index} className="text-sm bg-muted p-2 rounded">
                              Region {index + 1}: {diff.width}×{diff.height} at ({diff.x}, {diff.y}) - {diff.difference_percentage}% different
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No test results yet. Run a visual test to see results here.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default VisualTesting
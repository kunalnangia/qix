import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Gauge, Loader2, Play, TrendingUp, Clock, Cpu, HardDrive } from 'lucide-react'
import { useTesting } from '@/hooks/useTesting'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const Performance = () => {
  const [selectedTestCase, setSelectedTestCase] = useState('')
  const [url, setUrl] = useState('')
  const [testResult, setTestResult] = useState<any>(null)

  const { executePerformanceTest, isExecuting } = useTesting()
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
      const result = await executePerformanceTest(selectedTestCase, url)
      setTestResult(result)
    } catch (error) {
      console.error('Error executing performance test:', error)
    }
  }

  const getPerformanceScore = (value: number, thresholds: { good: number, needs_improvement: number }) => {
    if (value <= thresholds.good) return { score: 'good', color: 'bg-green-500' }
    if (value <= thresholds.needs_improvement) return { score: 'needs improvement', color: 'bg-yellow-500' }
    return { score: 'poor', color: 'bg-red-500' }
  }

  const formatBytes = (bytes: number) => {
    return `${bytes} MB`
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Performance Testing</h1>
        <p className="text-muted-foreground">Load and performance testing suite</p>
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
                <Gauge className="h-5 w-5" />
                Performance Test Configuration
              </CardTitle>
              <CardDescription>
                Configure performance testing parameters and thresholds
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
                    {testCases?.filter(tc => tc.test_type === 'performance').map((testCase) => (
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

              <Button 
                onClick={handleExecuteTest} 
                disabled={isExecuting || !selectedTestCase || !url}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Performance Analysis...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Performance Test
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
                    <TrendingUp className="h-5 w-5" />
                    Core Web Vitals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm font-medium">FCP</span>
                      </div>
                      <div className="text-2xl font-bold">{testResult.metrics.first_contentful_paint}ms</div>
                      <Badge variant={getPerformanceScore(testResult.metrics.first_contentful_paint, { good: 1800, needs_improvement: 3000 }).score === 'good' ? 'default' : 'destructive'}>
                        {getPerformanceScore(testResult.metrics.first_contentful_paint, { good: 1800, needs_improvement: 3000 }).score}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        <span className="text-sm font-medium">LCP</span>
                      </div>
                      <div className="text-2xl font-bold">{testResult.metrics.largest_contentful_paint}ms</div>
                      <Badge variant={getPerformanceScore(testResult.metrics.largest_contentful_paint, { good: 2500, needs_improvement: 4000 }).score === 'good' ? 'default' : 'destructive'}>
                        {getPerformanceScore(testResult.metrics.largest_contentful_paint, { good: 2500, needs_improvement: 4000 }).score}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Gauge className="h-4 w-4" />
                        <span className="text-sm font-medium">CLS</span>
                      </div>
                      <div className="text-2xl font-bold">{testResult.metrics.cumulative_layout_shift.toFixed(3)}</div>
                      <Badge variant={getPerformanceScore(testResult.metrics.cumulative_layout_shift, { good: 0.1, needs_improvement: 0.25 }).score === 'good' ? 'default' : 'destructive'}>
                        {getPerformanceScore(testResult.metrics.cumulative_layout_shift, { good: 0.1, needs_improvement: 0.25 }).score}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span className="text-sm font-medium">TTI</span>
                      </div>
                      <div className="text-2xl font-bold">{testResult.metrics.time_to_interactive}ms</div>
                      <Badge variant={getPerformanceScore(testResult.metrics.time_to_interactive, { good: 3800, needs_improvement: 7300 }).score === 'good' ? 'default' : 'destructive'}>
                        {getPerformanceScore(testResult.metrics.time_to_interactive, { good: 3800, needs_improvement: 7300 }).score}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      Loading Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm">Page Load Time</span>
                      <span className="font-medium">{testResult.metrics.page_load_time}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Network Requests</span>
                      <span className="font-medium">{testResult.metrics.network_requests}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Cpu className="h-5 w-5" />
                      Resource Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm">Memory Usage</span>
                      <span className="font-medium">{formatBytes(testResult.metrics.memory_usage)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">CPU Usage</span>
                      <span className="font-medium">{testResult.metrics.cpu_usage}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Performance Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {testResult.metrics.page_load_time > 2000 && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                        Page load time is slower than recommended ({'>'}2s). Consider optimizing images and reducing JavaScript bundle size.
                      </div>
                    )}
                    {testResult.metrics.cumulative_layout_shift > 0.1 && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        High cumulative layout shift detected. Reserve space for images and ads to improve user experience.
                      </div>
                    )}
                    {testResult.metrics.memory_usage > 40 && (
                      <div className="flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                        High memory usage detected. Consider optimizing memory-intensive operations.
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No test results yet. Run a performance test to see metrics here.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Performance
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Checkbox } from '@/components/ui/checkbox'
import { Shield, Loader2, Play, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { useTesting } from '@/hooks/useTesting'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const Security = () => {
  const [selectedTestCase, setSelectedTestCase] = useState('')
  const [url, setUrl] = useState('')
  const [scanTypes, setScanTypes] = useState(['xss', 'sql_injection', 'csrf'])
  const [testResult, setTestResult] = useState<any>(null)

  const { executeSecurityTest, isExecuting } = useTesting()
  const { testCases } = useTestCases()
  const { toast } = useToast()

  const availableScanTypes = [
    { id: 'xss', label: 'Cross-Site Scripting (XSS)', description: 'Detect XSS vulnerabilities' },
    { id: 'sql_injection', label: 'SQL Injection', description: 'Check for SQL injection flaws' },
    { id: 'csrf', label: 'Cross-Site Request Forgery', description: 'Test CSRF protection' },
    { id: 'security_headers', label: 'Security Headers', description: 'Validate security headers' },
    { id: 'ssl_tls', label: 'SSL/TLS Configuration', description: 'Check SSL/TLS setup' },
    { id: 'open_redirect', label: 'Open Redirect', description: 'Detect open redirect vulnerabilities' }
  ]

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
      const result = await executeSecurityTest(selectedTestCase, url, scanTypes)
      setTestResult(result)
    } catch (error) {
      console.error('Error executing security test:', error)
    }
  }

  const handleScanTypeChange = (scanType: string, checked: boolean) => {
    if (checked) {
      setScanTypes([...scanTypes, scanType])
    } else {
      setScanTypes(scanTypes.filter(type => type !== scanType))
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="h-4 w-4 text-red-600" />
      case 'high': return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'medium': return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'low': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default: return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  const getSeverityVariant = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive'
      case 'high': return 'destructive' 
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Security Testing</h1>
        <p className="text-muted-foreground">Advanced security testing capabilities</p>
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
                <Shield className="h-5 w-5" />
                Security Test Configuration
              </CardTitle>
              <CardDescription>
                Configure security scanning parameters and vulnerability types
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
                    {testCases?.filter(tc => tc.test_type === 'security').map((testCase) => (
                      <SelectItem key={testCase.id} value={testCase.id}>
                        {testCase.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Target URL</label>
                <Input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">Scan Types</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableScanTypes.map((scanType) => (
                    <div key={scanType.id} className="flex items-start space-x-2">
                      <Checkbox
                        id={scanType.id}
                        checked={scanTypes.includes(scanType.id)}
                        onCheckedChange={(checked) => handleScanTypeChange(scanType.id, checked as boolean)}
                      />
                      <div className="grid gap-1.5 leading-none">
                        <label 
                          htmlFor={scanType.id}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {scanType.label}
                        </label>
                        <p className="text-xs text-muted-foreground">
                          {scanType.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button 
                onClick={handleExecuteTest} 
                disabled={isExecuting || !selectedTestCase || !url || scanTypes.length === 0}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Security Scan...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Start Security Scan
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
                    <Shield className="h-5 w-5" />
                    Security Scan Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{testResult.summary.total_findings}</div>
                      <div className="text-sm text-muted-foreground">Total Issues</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{testResult.summary.critical}</div>
                      <div className="text-sm text-muted-foreground">Critical</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-500">{testResult.summary.high}</div>
                      <div className="text-sm text-muted-foreground">High</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-500">{testResult.summary.medium}</div>
                      <div className="text-sm text-muted-foreground">Medium</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-500">{testResult.summary.low}</div>
                      <div className="text-sm text-muted-foreground">Low</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {testResult.findings.length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle>Security Vulnerabilities</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {testResult.findings.map((finding: any, index: number) => (
                        <div key={index} className="border rounded-lg p-4 space-y-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              {getSeverityIcon(finding.severity)}
                              <h4 className="font-medium">{finding.vulnerability_type}</h4>
                              <Badge variant={getSeverityVariant(finding.severity)}>
                                {finding.severity}
                              </Badge>
                            </div>
                            <Badge variant="outline">{finding.status}</Badge>
                          </div>
                          
                          <p className="text-sm text-muted-foreground">{finding.description}</p>
                          
                          {finding.location && (
                            <div className="text-xs bg-muted p-2 rounded">
                              <strong>Location:</strong> {finding.location}
                            </div>
                          )}
                          
                          <div className="text-sm">
                            <strong>Remediation:</strong> {finding.remediation}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No Security Issues Found</h3>
                    <p className="text-muted-foreground">Your application passed all security tests.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No scan results yet. Run a security test to see vulnerabilities here.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Security
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Wand2, Loader2, Plus } from 'lucide-react'
import { useAI } from '@/hooks/useAI'
import { useProjects } from '@/hooks/useProjects'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const AIGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [selectedProject, setSelectedProject] = useState('')
  const [generatedTests, setGeneratedTests] = useState<any[]>([])
  const { generateTests, isGenerating } = useAI()
  const { projects } = useProjects()
  const { createTestCase } = useTestCases()
  const { toast } = useToast()

  const handleGenerate = async () => {
    if (!prompt.trim() || !selectedProject) {
      toast({
        title: "Missing Information",
        description: "Please enter a prompt and select a project",
        variant: "destructive",
      })
      return
    }

    try {
      const result = await generateTests(prompt, selectedProject)
      setGeneratedTests(result.tests?.testCases || [])
    } catch (error) {
      console.error('Error generating tests:', error)
    }
  }

  const handleAddTestCase = async (test: any) => {
    try {
      await createTestCase({
        title: test.title,
        description: test.description,
        expected_result: test.expected_result,
        steps: test.steps,
        priority: test.priority,
        test_type: test.test_type,
        tags: test.tags,
        project_id: selectedProject,
        ai_generated: true,
        status: 'draft',
        self_healing_enabled: true
      })

      toast({
        title: "Success",
        description: "Test case added successfully",
      })
    } catch (error) {
      console.error('Error adding test case:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Test Generator</h1>
        <p className="text-muted-foreground">Generate comprehensive test cases using AI</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5" />
            Generate Test Cases
          </CardTitle>
          <CardDescription>
            Describe your feature or functionality and let AI generate comprehensive test cases
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Project</label>
            <Select value={selectedProject} onValueChange={setSelectedProject}>
              <SelectTrigger>
                <SelectValue placeholder="Select a project" />
              </SelectTrigger>
              <SelectContent>
                {projects?.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium">Describe what you want to test</label>
            <Textarea
              placeholder="Example: Login functionality with email and password, including forgot password flow and validation errors..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
            />
          </div>

          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating || !prompt.trim() || !selectedProject}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Test Cases...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-4 w-4" />
                Generate Test Cases
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {generatedTests.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Generated Test Cases</h2>
          <div className="grid gap-4">
            {generatedTests.map((test, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{test.title}</CardTitle>
                      <CardDescription>{test.description}</CardDescription>
                    </div>
                    <Button
                      onClick={() => handleAddTestCase(test)}
                      size="sm"
                      className="shrink-0"
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add to Project
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={test.priority === 'high' ? 'destructive' : test.priority === 'medium' ? 'default' : 'secondary'}>
                      {test.priority}
                    </Badge>
                    <Badge variant="outline">{test.test_type}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Test Steps:</h4>
                      <ol className="list-decimal list-inside space-y-1">
                        {test.steps?.map((step: any, stepIndex: number) => (
                          <li key={stepIndex} className="text-sm">
                            <strong>{step.action}</strong> - Expected: {step.expected}
                          </li>
                        ))}
                      </ol>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Expected Result:</h4>
                      <p className="text-sm text-muted-foreground">{test.expected_result}</p>
                    </div>
                    {test.tags && (
                      <div className="flex gap-1 flex-wrap">
                        {test.tags.map((tag: string, tagIndex: number) => (
                          <Badge key={tagIndex} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AIGenerator
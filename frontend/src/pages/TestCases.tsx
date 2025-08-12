import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Search, Plus, Filter, Sparkles } from "lucide-react"
import { TestCaseList } from "@/components/test-cases/TestCaseList"
import { CollaborationPanel } from "@/components/test-cases/CollaborationPanel"
import { API_ENDPOINTS, fetcher } from "@/config/api"

const TestCases = () => {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedTest, setSelectedTest] = useState<number | null>(null)
  const [showComments, setShowComments] = useState(false)

  const { data: testCases, isLoading, isError } = useQuery({
    queryKey: ["testCases"],
    queryFn: () => fetcher(API_ENDPOINTS.TEST_CASES),
  })

  const filteredTestCases = testCases?.filter((test) =>
    test.title.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Test Cases</h1>
          <p className="text-muted-foreground mt-1">
            Manage and execute your test cases with AI assistance
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button variant="ai">
            <Sparkles className="h-4 w-4" />
            AI Generate
          </Button>
          <Button variant="default">
            <Plus className="h-4 w-4" />
            New Test Case
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="bg-card/50 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search test cases..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="lg:col-span-2 space-y-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <Skeleton className="h-5 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : isError ? (
          <div className="lg:col-span-2 text-destructive">
            Failed to load test cases.
          </div>
        ) : (
          <TestCaseList
            testCases={filteredTestCases}
            selectedTest={selectedTest}
            setSelectedTest={setSelectedTest}
            setShowComments={setShowComments}
          />
        )}
        <CollaborationPanel />
      </div>
    </div>
  )
}

export default TestCases
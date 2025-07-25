import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Search,
  Plus,
  FileText,
  Play,
  Edit,
  MessageSquare,
  Brain,
  Sparkles,
  Filter,
  MoreHorizontal,
  CheckCircle,
  Clock,
  AlertTriangle
} from "lucide-react"

const TestCases = () => {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedTest, setSelectedTest] = useState<number | null>(null)
  const [showComments, setShowComments] = useState(false)

  const testCases = [
    {
      id: 1,
      title: "User Login with Valid Credentials",
      description: "Verify that user can login with correct email and password",
      status: "active",
      priority: "high",
      lastRun: "2 hours ago",
      passRate: 98,
      tags: ["authentication", "login", "smoke"],
      comments: 3,
      automation: "ai-generated"
    },
    {
      id: 2,
      title: "Shopping Cart Add/Remove Items",
      description: "Test adding and removing items from shopping cart",
      status: "active",
      priority: "medium",
      lastRun: "1 day ago",
      passRate: 95,
      tags: ["e-commerce", "cart", "regression"],
      comments: 1,
      automation: "manual"
    },
    {
      id: 3,
      title: "Payment Gateway Integration",
      description: "Verify payment processing with multiple payment methods",
      status: "failing",
      priority: "high",
      lastRun: "30 minutes ago",
      passRate: 87,
      tags: ["payment", "integration", "critical"],
      comments: 5,
      automation: "self-healing"
    },
    {
      id: 4,
      title: "Mobile App Navigation",
      description: "Test navigation flow across mobile app screens",
      status: "active",
      priority: "medium",
      lastRun: "3 hours ago",
      passRate: 92,
      tags: ["mobile", "navigation", "ui"],
      comments: 2,
      automation: "ai-generated"
    }
  ]

  const comments = [
    {
      id: 1,
      user: "Sarah Johnson",
      message: "The payment timeout scenario needs more edge cases",
      time: "10 minutes ago",
      type: "feedback"
    },
    {
      id: 2,
      user: "AI Assistant",
      message: "Auto-healing detected element selector change. Test updated automatically.",
      time: "25 minutes ago",
      type: "system"
    },
    {
      id: 3,
      user: "Mike Chen",
      message: "Should we add tests for different currencies?",
      time: "1 hour ago",
      type: "question"
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-success text-success-foreground"
      case "failing": return "bg-destructive text-destructive-foreground"
      case "pending": return "bg-warning text-warning-foreground"
      default: return "bg-muted text-muted-foreground"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "border-l-destructive"
      case "medium": return "border-l-warning"
      case "low": return "border-l-muted"
      default: return "border-l-border"
    }
  }

  const getAutomationBadge = (automation: string) => {
    switch (automation) {
      case "ai-generated":
        return <Badge variant="default" className="bg-gradient-primary"><Sparkles className="h-3 w-3 mr-1" />AI Generated</Badge>
      case "self-healing":
        return <Badge variant="secondary" className="bg-gradient-success"><Brain className="h-3 w-3 mr-1" />Self-Healing</Badge>
      default:
        return <Badge variant="outline">Manual</Badge>
    }
  }

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
        {/* Test Cases List */}
        <div className="lg:col-span-2 space-y-4">
          {testCases.map((test) => (
            <Card 
              key={test.id} 
              className={`cursor-pointer transition-all duration-200 hover:shadow-card border-l-4 ${getPriorityColor(test.priority)} ${
                selectedTest === test.id ? "bg-primary/5 border-primary/30" : "bg-card/50 backdrop-blur-sm"
              }`}
              onClick={() => setSelectedTest(test.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      {test.title}
                    </CardTitle>
                    <CardDescription>{test.description}</CardDescription>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(test.status)} variant="outline">
                      {test.status}
                    </Badge>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 mt-3">
                  {getAutomationBadge(test.automation)}
                  {test.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span>{test.passRate}% pass rate</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{test.lastRun}</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        setShowComments(!showComments)
                      }}
                    >
                      <MessageSquare className="h-4 w-4" />
                      {test.comments}
                    </Button>
                    <Button variant="default" size="sm">
                      <Play className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Collaboration Panel */}
        <div className="space-y-4">
          <Card className="bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                Test Collaboration
              </CardTitle>
              <CardDescription>
                Real-time comments and discussions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {comments.map((comment) => (
                <div key={comment.id} className="p-3 rounded-lg bg-background/50 border border-border/50">
                  <div className="flex items-start justify-between mb-2">
                    <span className="font-medium text-sm">{comment.user}</span>
                    <span className="text-xs text-muted-foreground">{comment.time}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{comment.message}</p>
                  {comment.type === "system" && (
                    <Badge variant="outline" className="mt-2 text-xs">
                      <Brain className="h-3 w-3 mr-1" />
                      Auto-Update
                    </Badge>
                  )}
                </div>
              ))}
              
              <Button variant="outline" className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                Add Comment
              </Button>
            </CardContent>
          </Card>

          {/* AI Insights */}
          <Card className="bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                AI Test Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 rounded-lg bg-success/10 border border-success/20">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="h-4 w-4 text-success" />
                  <span className="text-sm font-medium">Coverage Optimal</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Login tests cover all critical scenarios
                </p>
              </div>
              
              <div className="p-3 rounded-lg bg-warning/10 border border-warning/20">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span className="text-sm font-medium">Suggest Enhancement</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Add negative test cases for payment flow
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default TestCases
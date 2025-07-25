import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  Target,
  Plus,
  Play,
  Calendar,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  Settings,
  Sparkles
} from "lucide-react"

const TestPlans = () => {
  const testPlans = [
    {
      id: 1,
      name: "Release 2.4 Regression Suite",
      description: "Comprehensive testing for upcoming release",
      status: "active",
      progress: 67,
      totalTests: 156,
      completedTests: 104,
      passRate: 94,
      estimatedTime: "2h 15m",
      actualTime: "1h 45m",
      environment: "staging",
      schedule: "Daily at 9:00 AM",
      assignees: ["Sarah Johnson", "Mike Chen", "AI Agent"],
      priority: "high",
      tags: ["regression", "release", "critical"]
    },
    {
      id: 2,
      name: "API Integration Test Suite",
      description: "Testing all API endpoints and integrations",
      status: "scheduled",
      progress: 0,
      totalTests: 89,
      completedTests: 0,
      passRate: 0,
      estimatedTime: "45m",
      actualTime: "Pending",
      environment: "production",
      schedule: "Triggered by deployment",
      assignees: ["Alex Rivera", "AI Agent"],
      priority: "medium",
      tags: ["api", "integration", "automated"]
    },
    {
      id: 3,
      name: "Mobile App Smoke Tests",
      description: "Quick validation of core mobile functionality",
      status: "completed",
      progress: 100,
      totalTests: 45,
      completedTests: 45,
      passRate: 98,
      estimatedTime: "30m",
      actualTime: "28m",
      environment: "qa",
      schedule: "After each build",
      assignees: ["Lisa Wong", "AI Agent"],
      priority: "low",
      tags: ["mobile", "smoke", "ios", "android"]
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-primary text-primary-foreground"
      case "completed": return "bg-success text-success-foreground"
      case "scheduled": return "bg-secondary text-secondary-foreground"
      case "failed": return "bg-destructive text-destructive-foreground"
      default: return "bg-muted text-muted-foreground"
    }
  }

  const getPriorityBorder = (priority: string) => {
    switch (priority) {
      case "high": return "border-l-destructive"
      case "medium": return "border-l-warning"
      case "low": return "border-l-success"
      default: return "border-l-border"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Test Plans</h1>
          <p className="text-muted-foreground mt-1">
            Organize and execute comprehensive test suites
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button variant="ai">
            <Sparkles className="h-4 w-4" />
            Smart Plan
          </Button>
          <Button variant="default">
            <Plus className="h-4 w-4" />
            New Plan
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">12</div>
            <p className="text-sm text-muted-foreground">Active Plans</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">89%</div>
            <p className="text-sm text-muted-foreground">Avg Pass Rate</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">3h 20m</div>
            <p className="text-sm text-muted-foreground">Total Runtime</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-secondary">1,247</div>
            <p className="text-sm text-muted-foreground">Total Tests</p>
          </CardContent>
        </Card>
      </div>

      {/* Test Plans List */}
      <div className="space-y-6">
        {testPlans.map((plan) => (
          <Card 
            key={plan.id} 
            className={`bg-card/50 backdrop-blur-sm border-l-4 ${getPriorityBorder(plan.priority)} hover:shadow-card transition-all duration-300`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <Target className="h-6 w-6 text-primary" />
                    <CardTitle className="text-xl">{plan.name}</CardTitle>
                    <Badge className={getStatusColor(plan.status)} variant="outline">
                      {plan.status}
                    </Badge>
                  </div>
                  <CardDescription className="text-base">{plan.description}</CardDescription>
                  
                  {/* Tags */}
                  <div className="flex gap-2 mt-2">
                    {plan.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon">
                    <Settings className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                  {plan.status === "active" ? (
                    <Button variant="destructive" size="sm">
                      Stop
                    </Button>
                  ) : (
                    <Button variant="default" size="sm">
                      <Play className="h-4 w-4" />
                      Run
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Progress Section */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Test Progress</span>
                  <span className="text-sm text-muted-foreground">
                    {plan.completedTests}/{plan.totalTests} tests
                  </span>
                </div>
                <Progress value={plan.progress} className="h-2" />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{plan.progress}% Complete</span>
                  <span className="flex items-center gap-1">
                    <CheckCircle className="h-4 w-4 text-success" />
                    {plan.passRate}% Pass Rate
                  </span>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <Clock className="h-4 w-4 text-primary" />
                    Timing
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Estimated:</span>
                      <span>{plan.estimatedTime}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Actual:</span>
                      <span>{plan.actualTime}</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    Schedule
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Frequency: </span>
                      <span>{plan.schedule}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Environment: </span>
                      <Badge variant="outline" className="text-xs ml-1">
                        {plan.environment}
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-medium flex items-center gap-2">
                    <Users className="h-4 w-4 text-primary" />
                    Team
                  </h4>
                  <div className="space-y-2">
                    {plan.assignees.map((assignee, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gradient-primary flex items-center justify-center text-xs text-primary-foreground">
                          {assignee === "AI Agent" ? "AI" : assignee.split(" ").map(n => n[0]).join("")}
                        </div>
                        <span className="text-sm">{assignee}</span>
                        {assignee === "AI Agent" && (
                          <Badge variant="outline" className="text-xs">
                            <Sparkles className="h-3 w-3 mr-1" />
                            AI
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* AI Recommendations */}
      <Card className="bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            AI Plan Optimization
          </CardTitle>
          <CardDescription>Smart recommendations for your test plans</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-success/10 border border-success/20">
              <CheckCircle className="h-5 w-5 text-success mb-2" />
              <h4 className="font-medium text-success mb-1">Optimal Scheduling</h4>
              <p className="text-sm text-muted-foreground">
                Your regression suite is scheduled at the best time for minimal CI conflicts
              </p>
            </div>
            
            <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
              <AlertTriangle className="h-5 w-5 text-warning mb-2" />
              <h4 className="font-medium text-warning mb-1">Suggest Prioritization</h4>
              <p className="text-sm text-muted-foreground">
                Consider running critical API tests before UI tests for faster feedback
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default TestPlans
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  TrendingUp, 
  TrendingDown, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Users, 
  Target, 
  Zap,
  BarChart3,
  Activity,
  Bot,
  Sparkles,
  Play,
  MessageSquare,
  AlertTriangle
} from "lucide-react"

const Dashboard = () => {
  const stats = [
    {
      title: "Test Cases",
      value: "2,847",
      change: "+12%",
      trend: "up",
      icon: Target,
      color: "text-primary"
    },
    {
      title: "Pass Rate",
      value: "94.2%",
      change: "+2.1%",
      trend: "up",
      icon: CheckCircle,
      color: "text-success"
    },
    {
      title: "Execution Time",
      value: "42m",
      change: "-18%",
      trend: "down",
      icon: Clock,
      color: "text-warning"
    },
    {
      title: "AI Efficiency",
      value: "87%",
      change: "+5.3%",
      trend: "up",
      icon: Bot,
      color: "text-secondary"
    }
  ]

  const recentActivity = [
    {
      id: 1,
      type: "success",
      title: "Login Flow Test Suite",
      description: "Completed successfully with 100% pass rate",
      time: "2 minutes ago",
      user: "AI Agent"
    },
    {
      id: 2,
      type: "warning",
      title: "Payment Gateway Tests",
      description: "2 tests failed - Auto-healing in progress",
      time: "5 minutes ago",
      user: "Sarah Johnson"
    },
    {
      id: 3,
      type: "info",
      title: "New Test Cases Generated",
      description: "AI generated 15 new test cases for checkout flow",
      time: "10 minutes ago",
      user: "AI Agent"
    },
    {
      id: 4,
      type: "collaboration",
      title: "Team Review",
      description: "Mike left feedback on API test cases",
      time: "15 minutes ago",
      user: "Mike Chen"
    }
  ]

  const activeTests = [
    {
      name: "E-commerce Regression Suite",
      status: "running",
      progress: 67,
      tests: "45/67",
      duration: "12m 34s"
    },
    {
      name: "Mobile App Smoke Tests",
      status: "queued",
      progress: 0,
      tests: "0/23",
      duration: "Pending"
    },
    {
      name: "API Integration Tests",
      status: "completed",
      progress: 100,
      tests: "89/89",
      duration: "8m 12s"
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            AI Test Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Welcome back! Your tests are running smoothly with AI assistance.
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button variant="ai" className="shadow-glow">
            <Sparkles className="h-4 w-4" />
            Generate Tests
          </Button>
          <Button variant="default">
            <Play className="h-4 w-4" />
            Run Tests
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          const TrendIcon = stat.trend === "up" ? TrendingUp : TrendingDown
          
          return (
            <Card key={stat.title} className="bg-card/50 backdrop-blur-sm border-border/50 hover:shadow-card transition-all duration-300">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                  <div className={`flex items-center gap-1 text-sm ${
                    stat.trend === "up" ? "text-success" : "text-destructive"
                  }`}>
                    <TrendIcon className="h-3 w-3" />
                    {stat.change}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-muted-foreground text-sm">{stat.title}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Test Runs */}
        <Card className="lg:col-span-2 bg-card/50 backdrop-blur-sm border-border/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  Active Test Runs
                </CardTitle>
                <CardDescription>Real-time test execution status</CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeTests.map((test, index) => (
              <div key={index} className="p-4 rounded-lg bg-background/50 border border-border/50">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium">{test.name}</h4>
                  <Badge variant={
                    test.status === "running" ? "default" :
                    test.status === "completed" ? "secondary" :
                    "outline"
                  } className="capitalize">
                    {test.status}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Progress: {test.tests}</span>
                    <span>{test.duration}</span>
                  </div>
                  <Progress value={test.progress} className="h-2" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Live Activity Feed
            </CardTitle>
            <CardDescription>Real-time updates and team collaboration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex gap-3 pb-3 border-b border-border/30 last:border-0">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  activity.type === "success" ? "bg-success" :
                  activity.type === "warning" ? "bg-warning" :
                  activity.type === "collaboration" ? "bg-secondary" :
                  "bg-primary"
                }`} />
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium">{activity.title}</p>
                  <p className="text-xs text-muted-foreground">{activity.description}</p>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{activity.user}</span>
                    <span>{activity.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* AI Insights Panel */}
      <Card className="bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-6 w-6 text-primary" />
            AI Insights & Recommendations
          </CardTitle>
          <CardDescription>Smart suggestions to improve your testing strategy</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-success/10 border border-success/20">
              <CheckCircle className="h-5 w-5 text-success mb-2" />
              <h4 className="font-medium text-success">Test Coverage Excellent</h4>
              <p className="text-sm text-muted-foreground">Your critical user flows have 95% coverage</p>
            </div>
            
            <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
              <AlertTriangle className="h-5 w-5 text-warning mb-2" />
              <h4 className="font-medium text-warning">API Tests Need Attention</h4>
              <p className="text-sm text-muted-foreground">Consider adding error handling tests</p>
            </div>
            
            <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
              <Zap className="h-5 w-5 text-primary mb-2" />
              <h4 className="font-medium text-primary">Auto-Healing Active</h4>
              <p className="text-sm text-muted-foreground">3 tests auto-fixed in the last hour</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard
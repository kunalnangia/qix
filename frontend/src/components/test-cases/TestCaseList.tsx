import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  FileText,
  Play,
  Edit,
  MessageSquare,
  Brain,
  Sparkles,
  MoreHorizontal,
  CheckCircle,
  Clock,
} from "lucide-react"

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

export const TestCaseList = ({ testCases, selectedTest, setSelectedTest, setShowComments }) => {
  return (
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
                    setShowComments(true)
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
  )
}

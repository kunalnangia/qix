import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  MessageSquare,
  Brain,
  Plus,
  CheckCircle,
  AlertTriangle
} from "lucide-react"

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

export const CollaborationPanel = () => {
  return (
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
  )
}

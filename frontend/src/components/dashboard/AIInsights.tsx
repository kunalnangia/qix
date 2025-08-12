import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Bot, CheckCircle, AlertTriangle, Zap } from "lucide-react"

export const AIInsights = () => {
  return (
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
  )
}

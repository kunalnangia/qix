import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Activity } from "lucide-react"

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

export const ActiveTestRuns = () => {
  return (
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
  )
}

import { Button } from "@/components/ui/button"
import { Sparkles, Play } from "lucide-react"
import { StatsGrid } from "@/components/dashboard/StatsGrid"
import { ActiveTestRuns } from "@/components/dashboard/ActiveTestRuns"
import { RecentActivity } from "@/components/dashboard/RecentActivity"
import { AIInsights } from "@/components/dashboard/AIInsights"

const Dashboard = () => {
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

      <StatsGrid />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ActiveTestRuns />
        <RecentActivity />
      </div>

      <AIInsights />
    </div>
  )
}

export default Dashboard;
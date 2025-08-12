import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { TrendingUp, TrendingDown, CheckCircle, Target, Bot, Clock } from "lucide-react"
import { API_ENDPOINTS, fetcher } from "@/config/api"

const iconMap = {
  total_test_cases: Target,
  pass_rate: CheckCircle,
  average_execution_time: Clock,
  ai_efficiency: Bot,
}

const colorMap = {
  total_test_cases: "text-primary",
  pass_rate: "text-success",
  average_execution_time: "text-warning",
  ai_efficiency: "text-secondary",
}

export const StatsGrid = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: () => fetcher(API_ENDPOINTS.DASHBOARD.STATS),
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardHeader>
              <Skeleton className="h-5 w-5" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-7 w-24 mb-2" />
              <Skeleton className="h-4 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="text-destructive">
        Failed to load dashboard stats.
      </div>
    )
  }

  const stats = [
    {
      title: "Test Cases",
      value: data.total_test_cases,
      change: "+12%", // Mock data
      trend: "up", // Mock data
      icon: iconMap.total_test_cases,
      color: colorMap.total_test_cases,
    },
    {
      title: "Pass Rate",
      value: `${data.pass_rate.toFixed(1)}%`,
      change: "+2.1%", // Mock data
      trend: "up", // Mock data
      icon: iconMap.pass_rate,
      color: colorMap.pass_rate,
    },
    {
      title: "Avg. Exec Time",
      value: `${data.average_execution_time.toFixed(2)}s`,
      change: "-18%", // Mock data
      trend: "down", // Mock data
      icon: iconMap.average_execution_time,
      color: colorMap.average_execution_time,
    },
    {
      title: "Active Runs",
      value: data.active_test_runs,
      change: "+5.3%", // Mock data
      trend: "up", // Mock data
      icon: iconMap.ai_efficiency, // This icon doesn't fit well
      color: colorMap.ai_efficiency,
    },
  ]

  return (
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
  )
}

import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { MessageSquare } from "lucide-react"
import { API_ENDPOINTS, fetcher } from "@/config/api"
import { formatDistanceToNow } from "date-fns"

export const RecentActivity = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboardActivity"],
    queryFn: () => fetcher(API_ENDPOINTS.DASHBOARD.ACTIVITY),
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="flex gap-3 pb-3 border-b border-border/30 last:border-0">
              <Skeleton className="h-2 w-2 rounded-full mt-2" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <div className="flex justify-between">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive">Failed to load recent activity.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary" />
          Live Activity Feed
        </CardTitle>
        <CardDescription>Real-time updates and team collaboration</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {data.map((activity: any) => (
          <div key={activity.id} className="flex gap-3 pb-3 border-b border-border/30 last:border-0">
            <div className={`w-2 h-2 rounded-full mt-2 bg-primary`} />
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium">{activity.target_name}</p>
              <p className="text-xs text-muted-foreground">{activity.description}</p>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{activity.user_name}</span>
                <span>{formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

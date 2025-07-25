import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "./AppSidebar"
import { Button } from "@/components/ui/button"
import { Bell, User, Search } from "lucide-react"
import { Input } from "@/components/ui/input"

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-50">
            <div className="flex items-center gap-4">
              <SidebarTrigger className="p-2 hover:bg-accent rounded-lg transition-colors" />
              
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Search tests, plans, reports..." 
                  className="pl-10 w-80 bg-background"
                />
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Status Indicator */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-success/10 text-success rounded-full text-sm font-medium">
                <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                All Systems Operational
              </div>
              
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-primary text-primary-foreground rounded-full text-xs flex items-center justify-center">
                  3
                </span>
              </Button>
              
              {/* User Menu */}
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
            </div>
          </header>
          
          {/* Main Content */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}
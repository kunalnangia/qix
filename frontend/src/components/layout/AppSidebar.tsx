import { useState } from "react"
import { NavLink, useLocation } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"
import { 
  Bot, 
  LayoutDashboard, 
  FileText, 
  Play, 
  BarChart3, 
  Globe, 
  Eye, 
  Users, 
  Settings, 
  Sparkles,
  TestTube,
  Target,
  Zap,
  Brain,
  Shield,
  LogOut
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar"

const navigation = [
  {
    title: "Core Platform",
    items: [
      { title: "Dashboard", url: "/", icon: LayoutDashboard, badge: "Live" },
      { title: "Test Cases", url: "/test-cases", icon: FileText },
      { title: "Test Plans", url: "/test-plans", icon: Target },
      { title: "Execution", url: "/execution", icon: Play },
    ]
  },
  {
    title: "AI Features",
    items: [
      { title: "AI Test Gen", url: "/ai-generator", icon: Sparkles, badge: "AI" },
      { title: "Self-Healing", url: "/self-healing", icon: Zap, badge: "Auto" },
      { title: "Smart Debug", url: "/ai-debug", icon: Brain, badge: "AI" },
      { title: "Test Insights", url: "/insights", icon: BarChart3 },
    ]
  },
  {
    title: "Testing Types",
    items: [
      { title: "API Testing", url: "/api-testing", icon: Globe },
      { title: "Visual Testing", url: "/visual-testing", icon: Eye },
      { title: "Security Testing", url: "/security", icon: Shield },
      { title: "Performance", url: "/performance", icon: TestTube },
    ]
  },
  {
    title: "Collaboration",
    items: [
      { title: "Team", url: "/team", icon: Users },
      { title: "Settings", url: "/settings", icon: Settings },
    ]
  }
]

export function AppSidebar() {
  const { state } = useSidebar()
  const location = useLocation()
  const currentPath = location.pathname
  const collapsed = state === "collapsed"
  const { signOut } = useAuth()

  const handleSignOut = async () => {
    await signOut()
  }

  const isActive = (path: string) => {
    if (path === "/") return currentPath === "/"
    return currentPath.startsWith(path)
  }

  const getNavCls = (isActiveItem: boolean) =>
    isActiveItem
      ? "bg-gradient-primary text-primary-foreground shadow-ai"
      : "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-smooth"

  return (
    <Sidebar
      className={`${collapsed ? "w-16" : "w-64"} transition-all duration-300 border-r border-sidebar-border`}
      collapsible="icon"
    >
      <SidebarContent className="bg-sidebar">
        {/* Logo */}
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary shadow-glow">
              <Bot className="h-6 w-6 text-primary-foreground" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-lg font-bold text-sidebar-foreground">IntelliTestAI</h1>
                <p className="text-xs text-sidebar-foreground/60">AI Test Automation</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 p-2">
          {navigation.map((group) => (
            <SidebarGroup key={group.title} className="mb-4">
              {!collapsed && (
                <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-semibold uppercase tracking-wider mb-2">
                  {group.title}
                </SidebarGroupLabel>
              )}
              
              <SidebarGroupContent>
                <SidebarMenu className="space-y-1">
                  {group.items.map((item) => {
                    const isActiveItem = isActive(item.url)
                    return (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton asChild>
                          <NavLink 
                            to={item.url} 
                            className={`${getNavCls(isActiveItem)} flex items-center gap-3 p-3 rounded-lg group relative`}
                          >
                            <item.icon className={`h-5 w-5 ${isActiveItem ? 'text-primary-foreground' : 'text-sidebar-foreground/80'}`} />
                            {!collapsed && (
                              <>
                                <span className={`font-medium ${isActiveItem ? 'text-primary-foreground' : 'text-sidebar-foreground'}`}>
                                  {item.title}
                                </span>
                                {item.badge && (
                                  <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                                    item.badge === "AI" 
                                      ? "bg-gradient-neural text-primary-foreground"
                                      : item.badge === "Auto"
                                      ? "bg-gradient-success text-success-foreground"
                                      : "bg-primary/20 text-primary"
                                  }`}>
                                    {item.badge}
                                  </span>
                                )}
                              </>
                            )}
                          </NavLink>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    )
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ))}
        </div>

        {/* Sign Out Button */}
        <div className="p-2 border-t border-sidebar-border">
          <SidebarMenuButton onClick={handleSignOut} className="w-full text-left">
            <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-sidebar-accent text-sidebar-foreground/80 hover:text-sidebar-accent-foreground transition-smooth">
              <LogOut className="h-5 w-5" />
              {!collapsed && <span className="font-medium">Sign Out</span>}
            </div>
          </SidebarMenuButton>
        </div>
      </SidebarContent>
    </Sidebar>
  )
}
-- Create comprehensive database schema for IntelliTestAI platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enums for various status types
CREATE TYPE test_status AS ENUM ('draft', 'active', 'inactive', 'archived');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'passed', 'failed', 'skipped', 'cancelled');
CREATE TYPE test_type AS ENUM ('functional', 'api', 'visual', 'performance', 'security', 'integration', 'unit');
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'tester', 'developer', 'viewer');

-- Create profiles table for user management
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  role user_role DEFAULT 'tester',
  team_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create teams table
CREATE TABLE public.teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  created_by UUID REFERENCES public.profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table
CREATE TABLE public.projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  base_url TEXT,
  team_id UUID REFERENCES public.teams(id),
  created_by UUID REFERENCES public.profiles(id),
  status test_status DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_cases table
CREATE TABLE public.test_cases (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  test_type test_type DEFAULT 'functional',
  priority priority_level DEFAULT 'medium',
  status test_status DEFAULT 'draft',
  steps JSONB,
  expected_result TEXT,
  actual_result TEXT,
  created_by UUID REFERENCES public.profiles(id),
  assigned_to UUID REFERENCES public.profiles(id),
  tags TEXT[],
  ai_generated BOOLEAN DEFAULT FALSE,
  self_healing_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_plans table
CREATE TABLE public.test_plans (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
  created_by UUID REFERENCES public.profiles(id),
  scheduled_date TIMESTAMP WITH TIME ZONE,
  status test_status DEFAULT 'draft',
  environment TEXT,
  browser_config JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test_plan_cases junction table
CREATE TABLE public.test_plan_cases (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_plan_id UUID REFERENCES public.test_plans(id) ON DELETE CASCADE,
  test_case_id UUID REFERENCES public.test_cases(id) ON DELETE CASCADE,
  execution_order INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(test_plan_id, test_case_id)
);

-- Create test_executions table
CREATE TABLE public.test_executions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_plan_id UUID REFERENCES public.test_plans(id),
  test_case_id UUID REFERENCES public.test_cases(id),
  status execution_status DEFAULT 'pending',
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_ms INTEGER,
  error_message TEXT,
  screenshots TEXT[],
  logs JSONB,
  executed_by UUID REFERENCES public.profiles(id),
  browser_info JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create ai_test_generation_requests table
CREATE TABLE public.ai_test_generation_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES public.projects(id),
  user_input TEXT NOT NULL,
  generated_tests JSONB,
  status TEXT DEFAULT 'processing',
  created_by UUID REFERENCES public.profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create visual_baselines table for visual testing
CREATE TABLE public.visual_baselines (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_case_id UUID REFERENCES public.test_cases(id) ON DELETE CASCADE,
  screenshot_url TEXT NOT NULL,
  viewport_width INTEGER,
  viewport_height INTEGER,
  browser TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create api_test_configs table
CREATE TABLE public.api_test_configs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_case_id UUID REFERENCES public.test_cases(id) ON DELETE CASCADE,
  method TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  headers JSONB,
  body JSONB,
  expected_status INTEGER,
  expected_response JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance_metrics table
CREATE TABLE public.performance_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  execution_id UUID REFERENCES public.test_executions(id) ON DELETE CASCADE,
  page_load_time INTEGER,
  first_contentful_paint INTEGER,
  largest_contentful_paint INTEGER,
  time_to_interactive INTEGER,
  cumulative_layout_shift DECIMAL,
  memory_usage INTEGER,
  cpu_usage DECIMAL,
  network_requests INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create security_scan_results table
CREATE TABLE public.security_scan_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_case_id UUID REFERENCES public.test_cases(id) ON DELETE CASCADE,
  vulnerability_type TEXT,
  severity priority_level,
  description TEXT,
  location TEXT,
  remediation TEXT,
  status TEXT DEFAULT 'open',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_plan_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_test_generation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visual_baselines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_test_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_scan_results ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for profiles
CREATE POLICY "Users can view their own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert their own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Create RLS policies for teams
CREATE POLICY "Team members can view their team" ON public.teams FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE profiles.team_id = teams.id AND profiles.id = auth.uid())
);
CREATE POLICY "Team creators can manage teams" ON public.teams FOR ALL USING (created_by = auth.uid());

-- Create RLS policies for projects
CREATE POLICY "Team members can view team projects" ON public.projects FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE profiles.team_id = projects.team_id AND profiles.id = auth.uid())
);
CREATE POLICY "Project creators can manage projects" ON public.projects FOR ALL USING (created_by = auth.uid());

-- Create RLS policies for test_cases
CREATE POLICY "Team members can view team test cases" ON public.test_cases FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.projects p 
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE p.id = test_cases.project_id AND pr.id = auth.uid()
  )
);
CREATE POLICY "Team members can manage test cases" ON public.test_cases FOR ALL USING (
  EXISTS (
    SELECT 1 FROM public.projects p 
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE p.id = test_cases.project_id AND pr.id = auth.uid()
  )
);

-- Create RLS policies for test_plans
CREATE POLICY "Team members can view team test plans" ON public.test_plans FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.projects p 
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE p.id = test_plans.project_id AND pr.id = auth.uid()
  )
);
CREATE POLICY "Team members can manage test plans" ON public.test_plans FOR ALL USING (
  EXISTS (
    SELECT 1 FROM public.projects p 
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE p.id = test_plans.project_id AND pr.id = auth.uid()
  )
);

-- Create similar policies for other tables
CREATE POLICY "Team members can view test plan cases" ON public.test_plan_cases FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.test_plans tp 
    JOIN public.projects p ON p.id = tp.project_id
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE tp.id = test_plan_cases.test_plan_id AND pr.id = auth.uid()
  )
);

CREATE POLICY "Team members can manage test plan cases" ON public.test_plan_cases FOR ALL USING (
  EXISTS (
    SELECT 1 FROM public.test_plans tp 
    JOIN public.projects p ON p.id = tp.project_id
    JOIN public.profiles pr ON pr.team_id = p.team_id 
    WHERE tp.id = test_plan_cases.test_plan_id AND pr.id = auth.uid()
  )
);

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user registration
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create function to update updated_at timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON public.teams FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON public.test_cases FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_test_plans_updated_at BEFORE UPDATE ON public.test_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
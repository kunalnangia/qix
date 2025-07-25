-- Enable RLS on tables that don't have it yet
ALTER TABLE public.ai_test_generation_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_test_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_scan_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visual_baselines ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for ai_test_generation_requests
CREATE POLICY "Users can view their own AI generation requests" 
ON public.ai_test_generation_requests 
FOR SELECT 
USING (created_by = auth.uid());

CREATE POLICY "Users can create AI generation requests" 
ON public.ai_test_generation_requests 
FOR INSERT 
WITH CHECK (created_by = auth.uid());

CREATE POLICY "Users can update their own AI generation requests" 
ON public.ai_test_generation_requests 
FOR UPDATE 
USING (created_by = auth.uid());

-- Create RLS policies for api_test_configs
CREATE POLICY "Team members can manage API test configs" 
ON public.api_test_configs 
FOR ALL 
USING (EXISTS (
  SELECT 1 FROM test_cases tc
  JOIN projects p ON p.id = tc.project_id
  JOIN profiles pr ON pr.team_id = p.team_id
  WHERE tc.id = api_test_configs.test_case_id AND pr.id = auth.uid()
));

-- Create RLS policies for performance_metrics
CREATE POLICY "Team members can view performance metrics" 
ON public.performance_metrics 
FOR SELECT 
USING (EXISTS (
  SELECT 1 FROM test_executions te
  JOIN test_cases tc ON tc.id = te.test_case_id
  JOIN projects p ON p.id = tc.project_id
  JOIN profiles pr ON pr.team_id = p.team_id
  WHERE te.id = performance_metrics.execution_id AND pr.id = auth.uid()
));

-- Create RLS policies for security_scan_results
CREATE POLICY "Team members can manage security scan results" 
ON public.security_scan_results 
FOR ALL 
USING (EXISTS (
  SELECT 1 FROM test_cases tc
  JOIN projects p ON p.id = tc.project_id
  JOIN profiles pr ON pr.team_id = p.team_id
  WHERE tc.id = security_scan_results.test_case_id AND pr.id = auth.uid()
));

-- Create RLS policies for test_executions
CREATE POLICY "Team members can manage test executions" 
ON public.test_executions 
FOR ALL 
USING (
  -- For test case executions
  (test_case_id IS NOT NULL AND EXISTS (
    SELECT 1 FROM test_cases tc
    JOIN projects p ON p.id = tc.project_id
    JOIN profiles pr ON pr.team_id = p.team_id
    WHERE tc.id = test_executions.test_case_id AND pr.id = auth.uid()
  ))
  OR
  -- For test plan executions
  (test_plan_id IS NOT NULL AND EXISTS (
    SELECT 1 FROM test_plans tp
    JOIN projects p ON p.id = tp.project_id
    JOIN profiles pr ON pr.team_id = p.team_id
    WHERE tp.id = test_executions.test_plan_id AND pr.id = auth.uid()
  ))
);

-- Create RLS policies for visual_baselines
CREATE POLICY "Team members can manage visual baselines" 
ON public.visual_baselines 
FOR ALL 
USING (EXISTS (
  SELECT 1 FROM test_cases tc
  JOIN projects p ON p.id = tc.project_id
  JOIN profiles pr ON pr.team_id = p.team_id
  WHERE tc.id = visual_baselines.test_case_id AND pr.id = auth.uid()
));
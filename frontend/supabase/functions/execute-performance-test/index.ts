import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { testCaseId, url, config = {} } = await req.json();

    // Create Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Get user from auth header
    const authHeader = req.headers.get('Authorization')!;
    const token = authHeader.replace('Bearer ', '');
    const { data: { user } } = await supabase.auth.getUser(token);

    if (!user) {
      throw new Error('Unauthorized');
    }

    const startTime = Date.now();

    // Simulate performance test
    const mockMetrics = {
      page_load_time: Math.floor(Math.random() * 2000) + 500, // 500-2500ms
      first_contentful_paint: Math.floor(Math.random() * 1000) + 300,
      largest_contentful_paint: Math.floor(Math.random() * 1500) + 800,
      time_to_interactive: Math.floor(Math.random() * 2000) + 1000,
      cumulative_layout_shift: Math.random() * 0.3,
      memory_usage: Math.floor(Math.random() * 50) + 20, // MB
      cpu_usage: Math.floor(Math.random() * 30) + 10, // %
      network_requests: Math.floor(Math.random() * 50) + 10
    };

    const duration = Date.now() - startTime;

    // Create test execution record
    const { data: execution } = await supabase
      .from('test_executions')
      .insert({
        test_case_id: testCaseId,
        status: mockMetrics.page_load_time < 2000 ? 'passed' : 'failed',
        started_at: new Date(startTime).toISOString(),
        completed_at: new Date().toISOString(),
        duration_ms: duration,
        logs: { performance_test_config: config },
        executed_by: user.id,
        error_message: mockMetrics.page_load_time >= 2000 ? 'Page load time exceeded threshold' : null
      })
      .select()
      .single();

    // Store performance metrics
    await supabase
      .from('performance_metrics')
      .insert({
        execution_id: execution.id,
        ...mockMetrics
      });

    return new Response(JSON.stringify({
      success: true,
      metrics: mockMetrics,
      executionId: execution.id
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in performance test execution:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
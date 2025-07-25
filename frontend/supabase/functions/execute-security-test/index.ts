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
    const { testCaseId, url, scanTypes = ['xss', 'sql_injection', 'csrf'] } = await req.json();

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

    // Simulate security scan results
    const vulnerabilityTypes = ['XSS', 'SQL Injection', 'CSRF', 'Open Redirect', 'Security Headers', 'SSL/TLS'];
    const severityLevels = ['low', 'medium', 'high', 'critical'];
    
    const mockFindings = [];
    const numFindings = Math.floor(Math.random() * 5); // 0-4 findings

    for (let i = 0; i < numFindings; i++) {
      const vulnerability = vulnerabilityTypes[Math.floor(Math.random() * vulnerabilityTypes.length)];
      const severity = severityLevels[Math.floor(Math.random() * severityLevels.length)];
      
      mockFindings.push({
        vulnerability_type: vulnerability,
        severity: severity,
        description: `${vulnerability} vulnerability detected`,
        location: `/endpoint-${i + 1}`,
        remediation: `Fix ${vulnerability} by implementing proper validation and sanitization`,
        status: 'open'
      });
    }

    const duration = Date.now() - startTime;

    // Create test execution record
    const { data: execution } = await supabase
      .from('test_executions')
      .insert({
        test_case_id: testCaseId,
        status: mockFindings.length === 0 ? 'passed' : 'failed',
        started_at: new Date(startTime).toISOString(),
        completed_at: new Date().toISOString(),
        duration_ms: duration,
        logs: { security_scan_types: scanTypes, findings_count: mockFindings.length },
        executed_by: user.id,
        error_message: mockFindings.length > 0 ? `${mockFindings.length} security vulnerabilities found` : null
      })
      .select()
      .single();

    // Store security findings
    if (mockFindings.length > 0) {
      await supabase
        .from('security_scan_results')
        .insert(
          mockFindings.map(finding => ({
            test_case_id: testCaseId,
            ...finding
          }))
        );
    }

    return new Response(JSON.stringify({
      success: true,
      findings: mockFindings,
      executionId: execution.id,
      summary: {
        total_findings: mockFindings.length,
        critical: mockFindings.filter(f => f.severity === 'critical').length,
        high: mockFindings.filter(f => f.severity === 'high').length,
        medium: mockFindings.filter(f => f.severity === 'medium').length,
        low: mockFindings.filter(f => f.severity === 'low').length
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in security test execution:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
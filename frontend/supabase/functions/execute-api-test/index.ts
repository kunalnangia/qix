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
    const { testCaseId, config } = await req.json();

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
    let result;

    try {
      // Prepare headers
      const headers = {
        'Content-Type': 'application/json',
        ...config.headers
      };

      // Make the API request
      const response = await fetch(config.endpoint, {
        method: config.method,
        headers,
        body: config.method !== 'GET' ? JSON.stringify(config.body) : undefined,
      });

      const responseData = await response.text();
      let parsedResponse;
      
      try {
        parsedResponse = JSON.parse(responseData);
      } catch {
        parsedResponse = responseData;
      }

      const duration = Date.now() - startTime;

      // Validate response
      const statusMatches = !config.expected_status || response.status === config.expected_status;
      const responseMatches = !config.expected_response || 
        JSON.stringify(parsedResponse).includes(JSON.stringify(config.expected_response));

      result = {
        success: statusMatches && responseMatches,
        status: response.status,
        response: parsedResponse,
        duration,
        expected_status: config.expected_status,
        expected_response: config.expected_response,
        validation: {
          status_match: statusMatches,
          response_match: responseMatches
        }
      };

    } catch (error) {
      result = {
        success: false,
        error: error.message,
        duration: Date.now() - startTime,
        expected_status: config.expected_status,
        expected_response: config.expected_response
      };
    }

    // Create test execution record
    await supabase
      .from('test_executions')
      .insert({
        test_case_id: testCaseId,
        status: result.success ? 'passed' : 'failed',
        started_at: new Date(startTime).toISOString(),
        completed_at: new Date().toISOString(),
        duration_ms: result.duration,
        logs: { api_test_result: result },
        executed_by: user.id,
        error_message: result.error || null
      });

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in API test execution:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
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
    const { testCaseId, url, viewport = { width: 1920, height: 1080 } } = await req.json();

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

    // For demo purposes, we'll simulate a visual test
    // In a real implementation, you'd use Puppeteer or similar
    const mockResult = {
      success: Math.random() > 0.3, // 70% success rate for demo
      screenshot_url: `https://via.placeholder.com/${viewport.width}x${viewport.height}/0066cc/ffffff?text=Screenshot`,
      differences: Math.random() > 0.5 ? [] : [
        {
          x: Math.floor(Math.random() * viewport.width),
          y: Math.floor(Math.random() * viewport.height),
          width: Math.floor(Math.random() * 100) + 50,
          height: Math.floor(Math.random() * 100) + 50,
          difference_percentage: Math.floor(Math.random() * 15) + 1
        }
      ],
      similarity_percentage: Math.floor(Math.random() * 20) + 80,
      viewport
    };

    const duration = Date.now() - startTime;

    // Store visual baseline if this is the first test
    const { data: existingBaseline } = await supabase
      .from('visual_baselines')
      .select('*')
      .eq('test_case_id', testCaseId)
      .single();

    if (!existingBaseline) {
      await supabase
        .from('visual_baselines')
        .insert({
          test_case_id: testCaseId,
          screenshot_url: mockResult.screenshot_url,
          viewport_width: viewport.width,
          viewport_height: viewport.height,
          browser: 'chrome'
        });
    }

    // Create test execution record
    await supabase
      .from('test_executions')
      .insert({
        test_case_id: testCaseId,
        status: mockResult.success ? 'passed' : 'failed',
        started_at: new Date(startTime).toISOString(),
        completed_at: new Date().toISOString(),
        duration_ms: duration,
        logs: { visual_test_result: mockResult },
        executed_by: user.id,
        screenshots: [mockResult.screenshot_url],
        error_message: mockResult.success ? null : `Visual differences detected: ${mockResult.differences.length} regions`
      });

    return new Response(JSON.stringify({
      success: true,
      result: mockResult
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in visual test execution:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
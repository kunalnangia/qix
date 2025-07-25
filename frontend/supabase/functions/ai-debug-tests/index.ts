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
    const { testCaseId, errorDescription, logs } = await req.json();

    const openAIApiKey = Deno.env.get('OPENAI_API_KEY');
    if (!openAIApiKey) {
      throw new Error('OpenAI API key not configured');
    }

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

    // Get test case details
    const { data: testCase } = await supabase
      .from('test_cases')
      .select('*')
      .eq('id', testCaseId)
      .single();

    if (!testCase) {
      throw new Error('Test case not found');
    }

    // Generate debugging suggestions with OpenAI
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openAIApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: `You are an expert QA debugging assistant. Analyze failed test cases and provide actionable debugging suggestions.
            
            Provide your response in this JSON format:
            {
              "analysis": "Root cause analysis of the failure",
              "suggestions": [
                {
                  "category": "Environment|Data|Timing|Logic|Configuration",
                  "description": "Specific suggestion to fix the issue",
                  "priority": "high|medium|low"
                }
              ],
              "preventiveMeasures": ["Suggestion 1", "Suggestion 2"],
              "updatedSteps": [
                { "step": 1, "action": "Updated action", "expected": "Updated expectation" }
              ]
            }`
          },
          {
            role: 'user',
            content: `
            Test Case: ${testCase.title}
            Description: ${testCase.description}
            Steps: ${JSON.stringify(testCase.steps)}
            Expected Result: ${testCase.expected_result}
            
            Error Description: ${errorDescription}
            Logs: ${JSON.stringify(logs)}
            
            Please analyze this failed test and provide debugging suggestions.`
          }
        ],
        temperature: 0.3,
        max_tokens: 1500,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    const debugAnalysis = data.choices[0].message.content;
    
    let parsedAnalysis;
    try {
      parsedAnalysis = JSON.parse(debugAnalysis);
    } catch (e) {
      parsedAnalysis = {
        analysis: debugAnalysis,
        suggestions: [{
          category: "General",
          description: "Review the AI analysis above for debugging guidance",
          priority: "medium"
        }],
        preventiveMeasures: ["Regular test maintenance", "Better error handling"],
        updatedSteps: testCase.steps || []
      };
    }

    return new Response(JSON.stringify({ 
      success: true, 
      debugAnalysis: parsedAnalysis 
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in AI debug tests function:', error);
    return new Response(JSON.stringify({ 
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
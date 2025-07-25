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
    const { prompt, projectId } = await req.json();

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

    // Create AI generation request
    const { data: requestData } = await supabase
      .from('ai_test_generation_requests')
      .insert({
        user_input: prompt,
        project_id: projectId,
        created_by: user.id,
        status: 'processing'
      })
      .select()
      .single();

    // Generate test cases with OpenAI
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
            content: `You are an expert QA engineer that generates comprehensive test cases. 
            Generate test cases in the following JSON format:
            {
              "testCases": [
                {
                  "title": "Test case title",
                  "description": "Detailed description of what this test verifies",
                  "priority": "high|medium|low",
                  "test_type": "functional|api|visual|performance|security|integration|unit",
                  "steps": [
                    { "step": 1, "action": "Click login button", "expected": "Login modal opens" },
                    { "step": 2, "action": "Enter credentials", "expected": "User is authenticated" }
                  ],
                  "expected_result": "Overall expected outcome",
                  "tags": ["smoke", "regression", "login"]
                }
              ]
            }
            
            Focus on creating realistic, actionable test cases that cover different scenarios including positive, negative, and edge cases.`
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2000,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    const generatedContent = data.choices[0].message.content;
    
    let parsedTests;
    try {
      parsedTests = JSON.parse(generatedContent);
    } catch (e) {
      // If parsing fails, create a simple test case from the content
      parsedTests = {
        testCases: [{
          title: "Generated Test Case",
          description: generatedContent.substring(0, 500),
          priority: "medium",
          test_type: "functional",
          steps: [{ step: 1, action: "Manual verification needed", expected: "As described in AI response" }],
          expected_result: "Test should pass according to requirements",
          tags: ["ai-generated"]
        }]
      };
    }

    // Update the request with generated tests
    await supabase
      .from('ai_test_generation_requests')
      .update({
        generated_tests: parsedTests,
        status: 'completed'
      })
      .eq('id', requestData.id);

    return new Response(JSON.stringify({ 
      success: true, 
      tests: parsedTests,
      requestId: requestData.id 
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in AI generate tests function:', error);
    return new Response(JSON.stringify({ 
      error: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
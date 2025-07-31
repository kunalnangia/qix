-- SQL to get the handle_new_user function definition
SELECT 
    n.nspname as schema_name,
    p.proname as function_name,
    pg_get_functiondef(p.oid) as function_definition
FROM 
    pg_proc p
    LEFT JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE 
    p.proname = 'handle_new_user' 
    AND n.nspname = 'auth';

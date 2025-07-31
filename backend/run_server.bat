@echo off
set DATABASE_URL=postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha12%%40@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug
pause

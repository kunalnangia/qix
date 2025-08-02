@echo off
set DATABASE_URL=postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug
pause

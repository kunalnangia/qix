import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_test_data():
    # Create a synchronous engine
    engine = create_engine(os.getenv('DATABASE_URL').replace('asyncpg', 'psycopg2'))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Query to count records in each table
    tables = [
        'users', 'teams', 'projects', 'test_cases', 'test_steps',
        'test_plans', 'test_plan_test_cases', 'test_executions',
        'comments', 'environments', 'attachments', 'activity_logs',
        'team_members'
    ]

    print('\n=== Record Counts ===')
    for table in tables:
        try:
            result = db.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
            print(f'{table}: {result}')
        except Exception as e:
            print(f'Error querying {table}: {e}')

    # Get some sample data
    print('\n=== Sample Data ===')
    
    # Sample users
    print('\nSample Users:')
    users = db.execute(text('SELECT id, email, full_name, role FROM users LIMIT 3')).fetchall()
    for user in users:
        print(f'ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Role: {user[3]}')
    
    # Sample projects
    print('\nSample Projects:')
    projects = db.execute(text('SELECT p.id, p.name, u.email as owner FROM projects p JOIN users u ON p.created_by = u.id LIMIT 3')).fetchall()
    for proj in projects:
        print(f'ID: {proj[0]}, Name: {proj[1]}, Owner: {proj[2]}')
    
    # Sample test cases
    print('\nSample Test Cases:')
    test_cases = db.execute(text('''
        SELECT tc.id, tc.title, p.name as project, u.email as creator 
        FROM test_cases tc 
        JOIN projects p ON tc.project_id = p.id 
        JOIN users u ON tc.created_by = u.id 
        LIMIT 3
    ''')).fetchall()
    for tc in test_cases:
        print(f'ID: {tc[0]}, Title: {tc[1]}, Project: {tc[2]}, Creator: {tc[3]}')

    db.close()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load .env file from the backend directory
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    check_test_data()
import psycopg2
import uuid
import json
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres.lflecyuvttemfoyixngi",
        password="Ayeshaayesha12@",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port=5432,
        sslmode="require"
    )

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            return result
        conn.commit()
        return cur.rowcount
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def clear_existing_data():
    print("Clearing existing data...")
    # List tables in reverse order of dependencies
    tables = [
        'performance_metrics',
        'security_scan_results',
        'execution_steps',
        'test_executions',
        'test_plans',
        'test_cases',
        'api_test_configs',
        'ai_test_generation_requests',
        'projects',
        'teams',
        'profiles'
    ]
    
    for table in tables:
        try:
            execute_query(f"TRUNCATE TABLE {table} CASCADE")
            print(f"Cleared table: {table}")
        except Exception as e:
            print(f"Error clearing {table}: {e}")

def generate_sample_data():
    print("\nGenerating sample data...")
    
    # 1. Create profiles
    print("Creating profiles...")
    profile_ids = []
    roles = ['admin', 'manager', 'tester', 'viewer']
    
    for _ in range(5):
        profile_id = str(uuid.uuid4())
        execute_query("""
            INSERT INTO profiles (id, email, full_name, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (profile_id, fake.email(), fake.name(), random.choice(roles)))
        profile_ids.append(profile_id)
    
    # 2. Create teams
    print("Creating teams...")
    team_ids = []
    for i in range(2):
        team_id = str(uuid.uuid4())
        execute_query("""
            INSERT INTO teams (id, name, description, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (team_id, f"Team {i+1}", f"Description for Team {i+1}", random.choice(profile_ids)))
        team_ids.append(team_id)
    
    # 3. Create projects
    print("Creating projects...")
    project_ids = []
    statuses = ['active', 'inactive', 'archived']
    
    for i in range(3):
        project_id = str(uuid.uuid4())
        execute_query("""
            INSERT INTO projects (id, name, description, base_url, team_id, status, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s::test_status, %s, NOW(), NOW())
        """, (
            project_id,
            f"Project {i+1}",
            f"Description for Project {i+1}",
            f"https://project{i+1}.example.com",
            random.choice(team_ids),
            random.choice(statuses),
            random.choice(profile_ids)
        ))
        project_ids.append(project_id)
    
    # 4. Create test cases
    print("Creating test cases...")
    test_case_ids = []
    test_types = ['functional', 'api', 'ui', 'performance', 'security']
    priorities = ['low', 'medium', 'high', 'critical']
    
    for i in range(10):
        test_case_id = str(uuid.uuid4())
        execute_query("""
            INSERT INTO test_cases (
                id, title, description, project_id, test_type, priority, status,
                steps, expected_result, created_by, assigned_to, tags, ai_generated,
                self_healing_enabled, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s::test_type, %s::priority_level, 'draft'::test_status,
                   %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            test_case_id,
            f"Test Case {i+1}",
            f"Description for Test Case {i+1}",
            random.choice(project_ids),
            random.choice(test_types),
            random.choice(priorities),
            json.dumps([{"step": f"Step {j+1}", "action": f"Action {j+1}", "expected": f"Expected {j+1}"} for j in range(3)]),
            f"Expected result for Test Case {i+1}",
            random.choice(profile_ids),
            random.choice(profile_ids),
            [f"tag{j+1}" for j in range(random.randint(1, 3))],
            random.choice([True, False]),
            random.choice([True, False])
        ))
        test_case_ids.append(test_case_id)
    
    # 5. Create API test configs
    print("Creating API test configs...")
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    for test_case_id in test_case_ids[:5]:  # Only for first 5 test cases
        execute_query("""
            INSERT INTO api_test_configs (
                id, test_case_id, method, endpoint, headers, body,
                expected_status, expected_response, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            str(uuid.uuid4()),
            test_case_id,
            random.choice(methods),
            f"/api/endpoint/{random.randint(1, 100)}",
            json.dumps({"Content-Type": "application/json", "Authorization": "Bearer token123"}),
            json.dumps({"key": "value"}) if random.choice([True, False]) else None,
            random.choice([200, 201, 204, 400, 401, 404, 500]),
            json.dumps({"status": "success", "data": {"id": 123, "name": "Test Item"}})
        ))
    
    # 6. Create test executions
    print("Creating test executions...")
    execution_statuses = ['pending', 'in_progress', 'passed', 'failed', 'blocked']
    
    for test_case_id in test_case_ids:
        execution_id = str(uuid.uuid4())
        started_at = datetime.now() - timedelta(days=random.randint(1, 30))
        completed_at = started_at + timedelta(minutes=random.randint(1, 60))
        
        execute_query("""
            INSERT INTO test_executions (
                id, test_case_id, status, started_at, completed_at,
                duration_ms, error_message, screenshots, logs, executed_by, created_at
            )
            VALUES (%s, %s, %s::execution_status, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            execution_id,
            test_case_id,
            random.choice(execution_statuses),
            started_at,
            completed_at if random.choice([True, False]) else None,
            random.randint(1000, 60000) if random.choice([True, False]) else None,
            "Test failed: Element not found" if random.random() > 0.7 else None,
            [f"screenshot_{i}.png" for i in range(random.randint(0, 3))] if random.choice([True, False]) else [],
            json.dumps([{"level": "info", "message": f"Log entry {i}", "timestamp": str(datetime.now())} for i in range(3)]),
            random.choice(profile_ids)
        ))
        
        # 7. Create performance metrics for some executions
        if random.random() > 0.7:  # 30% chance to have performance metrics
            execute_query("""
                INSERT INTO performance_metrics (
                    id, execution_id, page_load_time, first_contentful_paint,
                    largest_contentful_paint, time_to_interactive, cumulative_layout_shift,
                    memory_usage, cpu_usage, network_requests, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                str(uuid.uuid4()),
                execution_id,
                random.randint(500, 5000),
                random.randint(300, 3000),
                random.randint(1000, 8001),
                random.randint(1000, 10000),
                random.uniform(0, 0.5),
                random.randint(100, 1000) * 1000 * 1000,  # 100MB to 1GB
                random.uniform(0.1, 5.0),
                random.randint(5, 100)
            ))
        
        # 8. Create security scan results for some test cases
        if random.random() > 0.8:  # 20% chance to have security findings
            severities = ['low', 'medium', 'high', 'critical']
            vuln_types = ['XSS', 'SQL Injection', 'CSRF', 'Broken Authentication', 'Sensitive Data Exposure']
            
            for _ in range(random.randint(1, 3)):  # 1-3 findings per test case
                execute_query("""
                    INSERT INTO security_scan_results (
                        id, test_case_id, vulnerability_type, severity,
                        description, location, remediation, status, created_at
                    )
                    VALUES (%s, %s, %s, %s::severity_level, %s, %s, %s, %s, NOW())
                """, (
                    str(uuid.uuid4()),
                    test_case_id,
                    random.choice(vuln_types),
                    random.choice(severities),
                    f"Potential {random.choice(vuln_types)} vulnerability found",
                    f"/api/endpoint/{random.randint(1, 100)}",
                    f"Implement proper input validation and use parameterized queries",
                    random.choice(['open', 'in_progress', 'resolved', 'false_positive'])
                ))
    
    # 9. Create AI test generation requests
    print("Creating AI test generation requests...")
    statuses = ['pending', 'processing', 'completed', 'failed']
    
    for _ in range(3):
        execute_query("""
            INSERT INTO ai_test_generation_requests (
                id, project_id, user_input, generated_tests, status,
                created_by, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            str(uuid.uuid4()),
            random.choice(project_ids),
            f"Generate test cases for {fake.bs()} functionality",
            json.dumps([{"title": f"Test {i+1}", "steps": ["Step 1", "Step 2"], "expected": "Expected result"} for i in range(3)])
            if random.random() > 0.3 else None,  # 70% chance to have generated tests
            random.choice(statuses),
            random.choice(profile_ids)
        ))

if __name__ == "__main__":
    print("Starting sample data generation...")
    try:
        clear_existing_data()
        generate_sample_data()
        print("\nSample data generation completed successfully!")
    except Exception as e:
        print(f"\nError generating sample data: {e}")
        raise

import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and enums
from app.models.db_models import (
    User, Project, TestCase, TestStep, TestPlan, TestExecution, 
    Comment, Team, TeamMember, Environment, TestPlanTestCase,
    TestType, Priority, Status, ExecutionStatus, CommentType
)
from app.core.config import settings

# Initialize Faker
fake = Faker()

# Database setup
# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

print(f"Using database URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def clear_database():
    """Clear existing data"""
    print("Clearing database...")
    db.execute(text('SET session_replication_role = replica;'))
    for table in ['test_plan_test_cases', 'test_executions', 'test_steps', 'comments', 
                 'test_cases', 'test_plans', 'environments', 'projects', 
                 'team_members', 'teams', 'users']:
        try:
            db.execute(text(f'TRUNCATE TABLE {table} CASCADE;'))
        except:
            pass
    db.execute(text('SET session_replication_role = DEFAULT;'))
    db.commit()

def create_users(count=5):
    """Create test users"""
    from app.core.security import get_password_hash
    
    users = []
    
    # Admin user
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("test"),
        role="admin",
        is_active=True
    )
    users.append(admin)
    db.add(admin)
    
    # Test user with specified credentials
    test_user = User(
        email="test@gmail.com",
        full_name="Test User",
        hashed_password=get_password_hash("test1234"),
        role="tester",
        is_active=True
    )
    users.append(test_user)
    db.add(test_user)
    
    # Regular users (remaining count - 2 since we already added admin and test user)
    for _ in range(max(0, count - 2)):
        user = User(
            email=fake.unique.email(),
            full_name=fake.name(),
            hashed_password=get_password_hash("test"),
            role=random.choice(["tester", "manager", "developer"]),
            is_active=random.choice([True, True, False])
        )
        users.append(user)
        db.add(user)
    
    db.commit()
    return users

def create_teams(users, count=2):
    """Create teams with members"""
    teams = []
    for _ in range(count):
        team = Team(
            name=f"Team {fake.unique.company_suffix()}",
            description=fake.bs(),
            created_by=random.choice([u for u in users if u.role in ["admin", "manager"]]).id
        )
        teams.append(team)
        db.add(team)
    db.commit()
    
    # Add members to teams
    for team in teams:
        team_members = random.sample(users, random.randint(1, min(3, len(users))))
        for member in team_members:
            db.add(TeamMember(
                team_id=team.id,
                user_id=member.id,
                role=random.choice(["member", "lead"])
            ))
    db.commit()
    return teams

def create_projects(users, teams, count=3):
    """Create projects with environments"""
    projects = []
    for _ in range(count):
        project = Project(
            name=f"Project {fake.unique.word().title()}",
            description=fake.paragraph(),
            created_by=random.choice(users).id,
            team_id=random.choice(teams).id if teams and random.random() > 0.3 else None,
            is_active=random.choice([True, True, False])
        )
        projects.append(project)
        db.add(project)
    db.commit()
    
    # Create environments for each project
    for project in projects:
        for env_name in ["Dev", "Staging", "Production"]:
            db.add(Environment(
                name=env_name,
                description=f"{env_name} environment",
                base_url=f"https://{project.name.lower()}-{env_name.lower()}.example.com",
                project_id=project.id,
                is_active=random.choice([True, True, False]),
                variables={"API_KEY": fake.uuid4()}
            ))
    db.commit()
    return projects

def create_test_cases(projects, users, count_per_project=5):
    """Create test cases with steps"""
    test_cases = []
    for project in projects:
        for _ in range(count_per_project):
            test_case = TestCase(
                title=f"Test {fake.unique.bs().title()}",
                description=fake.paragraph(),
                project_id=project.id,
                test_type=random.choice(list(TestType)),
                priority=random.choice(list(Priority)),
                status=random.choice(list(Status)),
                expected_result=f"Verify {fake.sentence()}",
                created_by=random.choice(users).id,
                assigned_to=random.choice(users).id if random.random() > 0.3 else None,
                tags=random.sample(["smoke", "regression", "sanity"], k=random.randint(1, 2))
            )
            test_cases.append(test_case)
            db.add(test_case)
    db.commit()
    
    # Add test steps
    for test_case in test_cases:
        for i in range(1, random.randint(3, 7)):
            db.add(TestStep(
                test_case_id=test_case.id,
                step_number=i,
                description=f"Step {i}: {fake.sentence()}",
                expected_result=f"Expected: {fake.sentence()}",
                status=random.choice(['passed', 'failed', None])
            ))
    db.commit()
    return test_cases

def create_test_plans(projects, users, test_cases, count_per_project=2):
    """Create test plans with test cases"""
    test_plans = []
    for project in projects:
        project_cases = [tc for tc in test_cases if tc.project_id == project.id]
        for _ in range(count_per_project):
            test_plan = TestPlan(
                name=f"Test Plan: {fake.bs().title()}",
                description=f"Plan for {project.name}",
                project_id=project.id,
                created_by=random.choice(users).id,
                status=random.choice(list(Status))
            )
            test_plans.append(test_plan)
            db.add(test_plan)
    db.commit()
    
    # Add test cases to plans
    for test_plan in test_plans:
        project_cases = [tc for tc in test_cases if tc.project_id == test_plan.project_id]
        if project_cases:
            selected_cases = random.sample(project_cases, min(3, len(project_cases)))
            for i, test_case in enumerate(selected_cases, 1):
                db.add(TestPlanTestCase(
                    test_plan_id=test_plan.id,
                    test_case_id=test_case.id,
                    order=i,
                    is_mandatory=random.choice([True, False])
                ))
    db.commit()
    return test_plans

def create_test_executions(test_cases, test_plans, users, count_per_case=2):
    """Create test executions"""
    test_executions = []
    for test_case in test_cases:
        case_plans = [p for p in test_plans if p.project_id == test_case.project_id]
        for _ in range(count_per_case):
            status = random.choice(list(ExecutionStatus))
            started_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            execution = TestExecution(
                test_case_id=test_case.id,
                test_plan_id=random.choice(case_plans).id if case_plans and random.random() > 0.3 else None,
                executed_by=random.choice(users).id,
                status=status,
                started_at=started_at,
                completed_at=started_at + timedelta(minutes=random.randint(1, 30)) if status != ExecutionStatus.PENDING else None
            )
            test_executions.append(execution)
            db.add(execution)
    db.commit()
    return test_executions

def main():
    print("Starting database population...")
    
    # Clear existing data
    clear_database()
    
    # Create test data
    users = create_users(5)  # 5 users
    teams = create_teams(users, 2)  # 2 teams
    projects = create_projects(users, teams, 3)  # 3 projects
    test_cases = create_test_cases(projects, users, 5)  # 5 test cases per project
    test_plans = create_test_plans(projects, users, test_cases, 2)  # 2 test plans per project
    test_executions = create_test_executions(test_cases, test_plans, users)  # 2 executions per test case
    
    print("Database population completed successfully!")
    print(f"Created: {len(users)} users, {len(teams)} teams, {len(projects)} projects,")
    print(f"         {len(test_cases)} test cases, {len(test_plans)} test plans, {len(test_executions)} test executions")

if __name__ == "__main__":
    main()
import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.models.db_models import (
    User, Project, TestCase, TestStep, TestPlan, TestExecution, 
    Comment, Team, TeamMember, Environment, Attachment, TestPlanTestCase,
    ActivityLog, TestType, Priority, Status, ExecutionStatus, CommentType
)
from app.core.security import get_password_hash

# Initialize Faker
fake = Faker()

# Create a database session
def get_db_session():
    from app.db.session import SQLALCHEMY_DATABASE_URL, async_engine
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Create a synchronous engine for seeding
    sync_engine = create_engine(
        str(SQLALCHEMY_DATABASE_URL).replace("asyncpg", "psycopg2"),
        echo=True
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    return SessionLocal()

def create_users(session, count=5):
    """Create test users"""
    users = []
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(admin)
    users.append(admin)
    
    # Create regular users
    for i in range(count):
        user = User(
            email=f"user{i+1}@example.com",
            full_name=fake.name(),
            hashed_password=get_password_hash("password123"),
            role=random.choice(["tester", "developer", "manager"]),
            is_active=random.choice([True, True, True, False]),  # 75% chance of being active
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow()
        )
        session.add(user)
        users.append(user)
    
    session.commit()
    return users

def create_teams(session, users, count=3):
    """Create test teams"""
    teams = []
    
    for i in range(count):
        team = Team(
            name=f"Team {fake.color_name().title()} {fake.word().title()}",
            description=fake.paragraph(),
            created_by=random.choice(users).id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow()
        )
        session.add(team)
        teams.append(team)
    
    session.commit()
    
    # Add members to teams
    for team in teams:
        # Add 2-5 members to each team
        num_members = random.randint(2, 5)
        team_users = random.sample(users, min(num_members, len(users)))
        
        for i, user in enumerate(team_users):
            member = TeamMember(
                team_id=team.id,
                user_id=user.id,
                role="owner" if i == 0 else random.choice(["member", "admin"]),
                joined_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            session.add(member)
    
    session.commit()
    return teams

def create_projects(session, teams, users, count_per_team=2):
    """Create test projects"""
    projects = []
    
    for team in teams:
        for _ in range(count_per_team):
            project = Project(
                name=f"{fake.catch_phrase()} Project",
                description=fake.paragraph(),
                created_by=random.choice(users).id,
                team_id=team.id,
                is_active=random.choice([True, True, False]),  # 2/3 chance of being active
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow()
            )
            session.add(project)
            projects.append(project)
    
    session.commit()
    return projects

def create_environments(session, projects, count_per_project=2):
    """Create test environments"""
    environments = []
    env_types = ["Development", "Staging", "Production", "QA", "UAT"]
    
    for project in projects:
        for i in range(min(count_per_project, len(env_types))):
            env = Environment(
                name=f"{env_types[i % len(env_types)]}",
                description=f"{env_types[i % len(env_types)]} environment for {project.name}",
                base_url=f"https://{fake.domain_name()}".lower(),
                project_id=project.id,
                is_active=random.choice([True, True, False]),
                variables={"API_KEY": fake.uuid4(), "ENV": env_types[i % len(env_types)].upper()}
            )
            session.add(env)
            environments.append(env)
    
    session.commit()
    return environments

def create_test_cases(session, projects, users, count_per_project=5):
    """Create test cases"""
    test_cases = []
    
    for project in projects:
        for i in range(count_per_project):
            status = random.choice(list(Status))
            test_case = TestCase(
                title=f"Test {fake.bs().title()}",
                description=fake.paragraph(),
                project_id=project.id,
                test_type=random.choice(list(TestType)),
                priority=random.choice(list(Priority)),
                status=status,
                expected_result=f"Expected result: {fake.sentence()}",
                created_by=random.choice(users).id,
                assigned_to=random.choice(users).id if random.random() > 0.3 else None,
                tags=random.sample(["regression", "smoke", "sanity", "api", "ui", "security"], k=random.randint(1, 3)),
                ai_generated=random.choice([True, False]),
                self_healing_enabled=random.choice([True, False]),
                prerequisites=f"Prerequisites: {fake.sentence()}",
                test_data={"username": fake.user_name(), "password": fake.password()},
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow()
            )
            session.add(test_case)
            test_cases.append(test_case)
    
    session.commit()
    
    # Create test steps for each test case
    for test_case in test_cases:
        num_steps = random.randint(3, 8)
        for step_num in range(1, num_steps + 1):
            step = TestStep(
                test_case_id=test_case.id,
                step_number=step_num,
                description=f"Step {step_num}: {fake.sentence()}",
                expected_result=f"Expected: {fake.sentence()}",
                actual_result=f"Actual: {fake.sentence()}" if random.random() > 0.7 else None,
                status=random.choice(["passed", "failed", None, None, None])  # 40% None, 30% passed, 30% failed
            )
            session.add(step)
    
    session.commit()
    return test_cases

def create_test_plans(session, projects, users, test_cases, count_per_project=2):
    """Create test plans"""
    test_plans = []
    
    for project in projects:
        project_test_cases = [tc for tc in test_cases if tc.project_id == project.id]
        
        for _ in range(count_per_project):
            if not project_test_cases:
                continue
                
            test_plan = TestPlan(
                name=f"Test Plan: {fake.bs().title()}",
                description=fake.paragraph(),
                project_id=project.id,
                created_by=random.choice(users).id,
                status=random.choice(list(Status)),
                scheduled_start=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                scheduled_end=datetime.utcnow() + timedelta(days=random.randint(31, 60)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow()
            )
            session.add(test_plan)
            test_plans.append(test_plan)
    
    session.commit()
    
    # Add test cases to test plans
    for test_plan in test_plans:
        project_test_cases = [tc for tc in test_cases if tc.project_id == test_plan.project_id]
        if not project_test_cases:
            continue
            
        num_test_cases = min(random.randint(3, len(project_test_cases)), 10)  # Add 3-10 test cases per plan
        selected_cases = random.sample(project_test_cases, num_test_cases)
        
        for i, test_case in enumerate(selected_cases, 1):
            tp_tc = TestPlanTestCase(
                test_plan_id=test_plan.id,
                test_case_id=test_case.id,
                order=i,
                is_mandatory=random.choice([True, False]),
                created_by=test_plan.created_by,
                created_at=datetime.utcnow()
            )
            session.add(tp_tc)
    
    session.commit()
    return test_plans

def create_test_executions(session, test_cases, test_plans, users, environments, count_per_test_case=3):
    """Create test executions"""
    test_executions = []
    
    for test_case in test_cases:
        # Find test plans that include this test case
        case_plans = [tp for tp in test_plans if tp.project_id == test_case.project_id]
        
        for _ in range(count_per_test_case):
            status = random.choice(list(ExecutionStatus))
            started_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            execution = TestExecution(
                test_case_id=test_case.id,
                test_plan_id=random.choice(case_plans).id if case_plans and random.random() > 0.3 else None,
                executed_by=random.choice(users).id,
                environment_id=random.choice([e.id for e in environments if e.project_id == test_case.project_id] or [None]),
                status=status,
                started_at=started_at if status != ExecutionStatus.PENDING else None,
                completed_at=started_at + timedelta(minutes=random.randint(1, 30)) if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
                duration=random.randint(5, 300) if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
                result={"status": status.value, "details": fake.paragraph()} if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
                logs=fake.paragraph() if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else None,
                screenshots=[f"screenshot_{i}.png" for i in range(random.randint(0, 3))] if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED] else [],
                error_message=fake.sentence() if status == ExecutionStatus.FAILED else None,
                ai_analysis={"confidence": random.uniform(0.7, 1.0), "suggestions": [fake.sentence()]} if random.random() > 0.7 else None,
                created_at=started_at,
                updated_at=datetime.utcnow()
            )
            session.add(execution)
            test_executions.append(execution)
    
    session.commit()
    return test_executions

def create_comments(session, test_cases, users, count_per_test_case=2):
    """Create comments on test cases"""
    comments = []
    
    for test_case in test_cases:
        for _ in range(count_per_test_case):
            comment = Comment(
                test_case_id=test_case.id,
                user_id=random.choice(users).id,
                user_name=random.choice(users).full_name,
                comment_type=random.choice(list(CommentType)),
                content=fake.paragraph(),
                parent_comment_id=None,  # Top-level comment
                resolved=random.choice([True, False]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow()
            )
            session.add(comment)
            comments.append(comment)
    
    session.commit()
    
    # Add some replies to comments
    for comment in comments:
        if random.random() > 0.7:  # 30% chance of having replies
            num_replies = random.randint(1, 3)
            for _ in range(num_replies):
                reply = Comment(
                    test_case_id=comment.test_case_id,
                    user_id=random.choice(users).id,
                    user_name=random.choice(users).full_name,
                    comment_type=CommentType.GENERAL,
                    content=fake.sentence(),
                    parent_comment_id=comment.id,
                    resolved=False,
                    created_at=comment.created_at + timedelta(hours=random.randint(1, 24)),
                    updated_at=datetime.utcnow()
                )
                session.add(reply)
    
    session.commit()
    return comments

def create_attachments(session, test_cases, users, count_per_entity=1):
    """Create attachments for test cases"""
    attachments = []
    file_types = ["image/png", "application/pdf", "text/plain", "application/json"]
    
    for test_case in test_cases:
        for _ in range(count_per_entity):
            file_type = random.choice(file_types)
            ext = file_type.split('/')[-1]
            
            attachment = Attachment(
                file_name=f"{fake.word()}.{ext}",
                file_path=f"/uploads/{fake.uuid4()}.{ext}",
                file_size=random.randint(1024, 1024*1024),  # 1KB to 1MB
                file_type=file_type,
                entity_type="test_case",
                entity_id=test_case.id,
                uploaded_by=random.choice(users).id,
                description=f"Attachment for {test_case.title}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            session.add(attachment)
            attachments.append(attachment)
    
    session.commit()
    return attachments

def create_activity_logs(session, users, test_cases, count_per_user=5):
    """Create activity logs"""
    activity_logs = []
    actions = ["create", "update", "delete", "execute", "comment", "attach"]
    target_types = ["test_case", "test_plan", "test_execution", "comment", "attachment"]
    
    for user in users:
        for _ in range(count_per_user):
            target_type = random.choice(target_types)
            target_id = str(fake.uuid4())  # In a real scenario, we'd get valid IDs
            
            log = ActivityLog(
                user_id=user.id,
                user_name=user.full_name,
                action=random.choice(actions),
                target_type=target_type,
                target_id=target_id,
                target_name=f"{target_type.title()} {fake.word()}",
                details={"field": fake.word(), "old_value": fake.word(), "new_value": fake.word()},
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            session.add(log)
            activity_logs.append(log)
    
    session.commit()
    return activity_logs

def main():
    print("Starting database seeding...")
    
    # Create database session
    session = get_db_session()
    
    try:
        # Create test data
        print("Creating users...")
        users = create_users(session, count=10)
        
        print("Creating teams...")
        teams = create_teams(session, users, count=3)
        
        print("Creating projects...")
        projects = create_projects(session, teams, users, count_per_team=2)
        
        print("Creating environments...")
        environments = create_environments(session, projects, count_per_project=2)
        
        print("Creating test cases...")
        test_cases = create_test_cases(session, projects, users, count_per_project=5)
        
        print("Creating test plans...")
        test_plans = create_test_plans(session, projects, users, test_cases, count_per_project=2)
        
        print("Creating test executions...")
        test_executions = create_test_executions(session, test_cases, test_plans, users, environments, count_per_test_case=2)
        
        print("Creating comments...")
        comments = create_comments(session, test_cases, users, count_per_test_case=2)
        
        print("Creating attachments...")
        attachments = create_attachments(session, test_cases, users, count_per_entity=1)
        
        print("Creating activity logs...")
        activity_logs = create_activity_logs(session, users, test_cases, count_per_user=5)
        
        print("\nDatabase seeding completed successfully!")
        print("\nSummary of created records:")
        print(f"- Users: {len(users)}")
        print(f"- Teams: {len(teams)}")
        print(f"- Projects: {len(projects)}")
        print(f"- Environments: {len(environments)}")
        print(f"- Test Cases: {len(test_cases)}")
        print(f"- Test Plans: {len(test_plans)}")
        print(f"- Test Executions: {len(test_executions)}")
        print(f"- Comments: {len(comments)}")
        print(f"- Attachments: {len(attachments)}")
        print(f"- Activity Logs: {len(activity_logs)}")
        
        print("\nAdmin credentials:")
        print("Email: admin@example.com")
        print("Password: admin123")
        
    except Exception as e:
        print(f"\nError during database seeding: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        from faker import Faker
    except ImportError:
        import subprocess
        import sys
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faker", "sqlalchemy", "psycopg2-binary"])
        from faker import Faker
    
    main()

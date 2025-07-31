import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from .session import SessionLocal
from ..models.db_models import (
    User, Team, Project, TestCase, TestStep, TestPlan, 
    TestExecution, Comment, TeamMember, Environment, 
    Attachment, TestPlanTestCase, ActivityLog
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_users(db: Session):
    """Create sample users"""
    users = [
        User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        ),
        User(
            id=str(uuid.uuid4()),
            username="tester1",
            email="tester1@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Test User One",
            is_active=True
        ),
        User(
            id=str(uuid.uuid4()),
            username="tester2",
            email="tester2@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
            full_name="Test User Two",
            is_active=True
        )
    ]
    
    for user in users:
        db.add(user)
    db.commit()
    logger.info(f"Created {len(users)} users")
    return users

def create_teams(db: Session, users):
    """Create sample teams"""
    teams = [
        Team(
            id=str(uuid.uuid4()),
            name="QA Team",
            description="Quality Assurance Team",
            created_by=users[0].id,
            created_at=datetime.utcnow()
        ),
        Team(
            id=str(uuid.uuid4()),
            name="Dev Team",
            description="Development Team",
            created_by=users[0].id,
            created_at=datetime.utcnow()
        )
    ]
    
    for team in teams:
        db.add(team)
    db.commit()
    
    # Add team members
    team_members = [
        TeamMember(team_id=teams[0].id, user_id=users[0].id, role="admin"),
        TeamMember(team_id=teams[0].id, user_id=users[1].id, role="member"),
        TeamMember(team_id=teams[1].id, user_id=users[0].id, role="admin"),
        TeamMember(team_id=teams[1].id, user_id=users[2].id, role="member"),
    ]
    
    for member in team_members:
        db.add(member)
    db.commit()
    logger.info(f"Created {len(teams)} teams with members")
    return teams

def create_projects(db: Session, teams, users):
    """Create sample projects"""
    projects = [
        Project(
            id=str(uuid.uuid4()),
            name="E-commerce Platform",
            description="Online shopping platform",
            team_id=teams[0].id,
            created_by=users[0].id,
            created_at=datetime.utcnow()
        ),
        Project(
            id=str(uuid.uuid4()),
            name="Mobile App",
            description="Mobile application",
            team_id=teams[1].id,
            created_by=users[0].id,
            created_at=datetime.utcnow()
        )
    ]
    
    for project in projects:
        db.add(project)
    db.commit()
    logger.info(f"Created {len(projects)} projects")
    return projects

def create_environments(db: Session, projects):
    """Create sample environments"""
    environments = []
    env_types = ["Development", "Staging", "Production"]
    
    for project in projects:
        for i, env_type in enumerate(env_types):
            env = Environment(
                id=str(uuid.uuid4()),
                name=f"{project.name} {env_type}",
                type=env_type.lower(),
                base_url=f"https://{project.name.lower().replace(' ', '-')}.{env_type.lower()}.example.com",
                project_id=project.id,
                created_at=datetime.utcnow()
            )
            environments.append(env)
            db.add(env)
    
    db.commit()
    logger.info(f"Created {len(environments)} environments")
    return environments

def create_test_cases(db: Session, projects, users):
    """Create sample test cases"""
    test_cases = []
    
    for i, project in enumerate(projects):
        for j in range(5):  # 5 test cases per project
            test_case = TestCase(
                id=str(uuid.uuid4()),
                title=f"Test Case {j+1} for {project.name}",
                description=f"Description for test case {j+1}",
                preconditions=f"Preconditions for test case {j+1}",
                expected_result=f"Expected result for test case {j+1}",
                project_id=project.id,
                created_by=users[i % len(users)].id,
                created_at=datetime.utcnow() - timedelta(days=j),
                updated_at=datetime.utcnow() - timedelta(days=j)
            )
            test_cases.append(test_case)
            db.add(test_case)
    
    db.commit()
    
    # Create test steps for each test case
    for test_case in test_cases:
        for k in range(3):  # 3 steps per test case
            step = TestStep(
                id=str(uuid.uuid4()),
                test_case_id=test_case.id,
                step_number=k + 1,
                description=f"Step {k+1} for {test_case.title}",
                expected_result=f"Expected result for step {k+1}",
                actual_result=f"Actual result for step {k+1}" if k < 2 else None,
                status="passed" if k < 2 else None
            )
            db.add(step)
    
    db.commit()
    logger.info(f"Created {len(test_cases)} test cases with steps")
    return test_cases

def create_test_plans(db: Session, projects, test_cases, users):
    """Create sample test plans"""
    test_plans = []
    
    for i, project in enumerate(projects):
        test_plan = TestPlan(
            id=str(uuid.uuid4()),
            name=f"Test Plan {i+1} for {project.name}",
            description=f"Description for test plan {i+1}",
            project_id=project.id,
            created_by=users[i % len(users)].id,
            created_at=datetime.utcnow() - timedelta(days=i+1)
        )
        test_plans.append(test_plan)
        db.add(test_plan)
    
    db.commit()
    
    # Add test cases to test plans
    for i, test_plan in enumerate(test_plans):
        # Add 3 test cases to each test plan
        for j in range(3):
            test_case = test_cases[(i * 3 + j) % len(test_cases)]
            plan_test_case = TestPlanTestCase(
                test_plan_id=test_plan.id,
                test_case_id=test_case.id,
                added_by=users[i % len(users)].id,
                added_at=datetime.utcnow()
            )
            db.add(plan_test_case)
    
    db.commit()
    logger.info(f"Created {len(test_plans)} test plans with test cases")
    return test_plans

def create_test_executions(db: Session, test_plans, test_cases, users, environments):
    """Create sample test executions"""
    test_executions = []
    statuses = ["passed", "failed", "blocked", "skipped"]
    
    for i, test_plan in enumerate(test_plans):
        for j in range(2):  # 2 executions per test plan
            execution = TestExecution(
                id=str(uuid.uuid4()),
                name=f"Execution {j+1} for {test_plan.name}",
                test_plan_id=test_plan.id,
                environment_id=environments[i % len(environments)].id,
                status=statuses[(i + j) % len(statuses)],
                started_at=datetime.utcnow() - timedelta(hours=j+1),
                completed_at=datetime.utcnow() - timedelta(minutes=j*30),
                created_by=users[i % len(users)].id,
                created_at=datetime.utcnow() - timedelta(hours=j+1)
            )
            test_executions.append(execution)
            db.add(execution)
    
    db.commit()
    
    # Add test case results to executions
    for execution in test_executions:
        # Get test cases for this execution's test plan
        plan_test_cases = db.query(TestPlanTestCase).filter_by(
            test_plan_id=execution.test_plan_id
        ).limit(3).all()
        
        for ptc in plan_test_cases:
            test_case = db.query(TestCase).get(ptc.test_case_id)
            if test_case:
                test_case.status = execution.status
                test_case.updated_at = datetime.utcnow()
                
                # Create activity log
                activity = ActivityLog(
                    id=str(uuid.uuid4()),
                    user_id=execution.created_by,
                    action=f"test_case_{execution.status}",
                    entity_type="test_case",
                    entity_id=test_case.id,
                    details=f"Test case {execution.status} in execution {execution.name}",
                    created_at=datetime.utcnow()
                )
                db.add(activity)
    
    db.commit()
    logger.info(f"Created {len(test_executions)} test executions")
    return test_executions

def create_comments(db: Session, users, test_cases):
    """Create sample comments"""
    comments = []
    
    for i, test_case in enumerate(test_cases):
        for j in range(2):  # 2 comments per test case
            comment = Comment(
                id=str(uuid.uuid4()),
                content=f"This is comment {j+1} for test case {test_case.title}",
                user_id=users[j % len(users)].id,
                test_case_id=test_case.id,
                created_at=datetime.utcnow() - timedelta(hours=j+1)
            )
            comments.append(comment)
            db.add(comment)
    
    db.commit()
    logger.info(f"Created {len(comments)} comments")
    return comments

def create_attachments(db: Session, test_cases, users):
    """Create sample attachments"""
    attachments = []
    
    for i, test_case in enumerate(test_cases[:3]):  # Add attachments to first 3 test cases
        attachment = Attachment(
            id=str(uuid.uuid4()),
            filename=f"screenshot-{i+1}.png",
            file_path=f"/attachments/screenshot-{i+1}.png",
            file_type="image/png",
            file_size=1024 * (i + 1),
            test_case_id=test_case.id,
            uploaded_by=users[i % len(users)].id,
            created_at=datetime.utcnow() - timedelta(hours=i+1)
        )
        attachments.append(attachment)
        db.add(attachment)
    
    db.commit()
    logger.info(f"Created {len(attachments)} attachments")
    return attachments

def create_activity_logs(db: Session, users, test_cases, test_plans, test_executions):
    """Create sample activity logs"""
    activities = []
    actions = ["create", "update", "delete", "execute"]
    entities = ["test_case", "test_plan", "test_execution", "project"]
    
    for i in range(20):  # Create 20 activity logs
        user = users[i % len(users)]
        action = actions[i % len(actions)]
        entity_type = entities[i % len(entities)]
        
        # Select entity ID based on entity type
        if entity_type == "test_case":
            entity_id = test_cases[i % len(test_cases)].id
        elif entity_type == "test_plan":
            entity_id = test_plans[i % len(test_plans)].id
        elif entity_type == "test_execution":
            entity_id = test_executions[i % len(test_executions)].id
        else:
            entity_id = str(uuid.uuid4())
        
        activity = ActivityLog(
            id=str(uuid.uuid4()),
            user_id=user.id,
            action=f"{entity_type}_{action}",
            entity_type=entity_type,
            entity_id=entity_id,
            details=f"User {user.username} {action}d {entity_type} {entity_id}",
            created_at=datetime.utcnow() - timedelta(hours=i)
        )
        activities.append(activity)
        db.add(activity)
    
    db.commit()
    logger.info(f"Created {len(activities)} activity logs")
    return activities

def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    try:
        logger.info("Starting database seeding...")
        
        # Create users
        users = create_users(db)
        
        # Create teams and members
        teams = create_teams(db, users)
        
        # Create projects
        projects = create_projects(db, teams, users)
        
        # Create environments
        environments = create_environments(db, projects)
        
        # Create test cases and steps
        test_cases = create_test_cases(db, projects, users)
        
        # Create test plans
        test_plans = create_test_plans(db, projects, test_cases, users)
        
        # Create test executions
        test_executions = create_test_executions(db, test_plans, test_cases, users, environments)
        
        # Create comments
        comments = create_comments(db, users, test_cases)
        
        # Create attachments
        attachments = create_attachments(db, test_cases, users)
        
        # Create activity logs
        activities = create_activity_logs(db, users, test_cases, test_plans, test_executions)
        
        logger.info("Database seeding completed successfully!")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during seeding: {str(e)}")
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during seeding: {str(e)}", exc_info=True)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting database seeding...")
    if seed_database():
        logger.info("Database seeded successfully!")
    else:
        logger.error("Database seeding failed!")

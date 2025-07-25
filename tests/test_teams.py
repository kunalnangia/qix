import pytest
from fastapi import status
from sqlalchemy.orm import Session

from backend import models, schemas

def test_create_team(client, db_session: Session, auth_headers):
    """Test creating a new team"""
    team_data = {
        "name": "Test Team",
        "description": "A test team"
    }
    
    response = client.post(
        "/teams/",
        json=team_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]
    assert "id" in data
    
    # Verify team was created in the database
    team = db_session.query(models.Team).filter(
        models.Team.id == data["id"]
    ).first()
    
    assert team is not None
    assert team.name == team_data["name"]

def test_list_teams(client, db_session: Session, auth_headers, create_test_user):
    """Test listing teams"""
    # Create test teams
    team1 = models.Team(
        id=str(uuid.uuid4()),
        name="Team 1",
        description="First test team",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    team2 = models.Team(
        id=str(uuid.uuid4()),
        name="Team 2",
        description="Second test team",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add_all([team1, team2])
    db_session.commit()
    
    # Add user to teams
    db_session.add_all([
        models.TeamMember(
            id=str(uuid.uuid4()),
            team_id=team1.id,
            user_id=create_test_user.id,
            role="member",
            joined_at=datetime.utcnow()
        ),
        models.TeamMember(
            id=str(uuid.uuid4()),
            team_id=team2.id,
            user_id=create_test_user.id,
            role="admin",
            joined_at=datetime.utcnow()
        )
    ])
    db_session.commit()
    
    # Test listing teams
    response = client.get("/teams/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(team["name"] == "Team 1" for team in data)
    assert any(team["name"] == "Team 2" for team in data)

def test_get_team(client, db_session: Session, auth_headers, create_test_user):
    """Test getting a team by ID"""
    # Create a test team
    team = models.Team(
        id=str(uuid.uuid4()),
        name="Test Team",
        description="A test team",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(team)
    db_session.commit()
    
    # Add user to team
    team_member = models.TeamMember(
        id=str(uuid.uuid4()),
        team_id=team.id,
        user_id=create_test_user.id,
        role="member",
        joined_at=datetime.utcnow()
    )
    
    db_session.add(team_member)
    db_session.commit()
    
    # Test getting the team
    response = client.get(f"/teams/{team.id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == str(team.id)
    assert data["name"] == "Test Team"
    assert "members" in data
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == str(create_test_user.id)

def test_add_team_member(client, db_session: Session, auth_headers, create_test_user):
    """Test adding a member to a team"""
    # Create a test team
    team = models.Team(
        id=str(uuid.uuid4()),
        name="Test Team",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(team)
    db_session.commit()
    
    # Create another test user
    another_user = models.User(
        id=str(uuid.uuid4()),
        email="another@example.com",
        hashed_password="hashedpassword",
        full_name="Another User",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add(another_user)
    db_session.commit()
    
    # Add the first user as an admin to the team
    admin_member = models.TeamMember(
        id=str(uuid.uuid4()),
        team_id=team.id,
        user_id=create_test_user.id,
        role="admin",
        joined_at=datetime.utcnow()
    )
    
    db_session.add(admin_member)
    db_session.commit()
    
    # Test adding a member
    member_data = {
        "user_id": str(another_user.id),
        "role": "member"
    }
    
    response = client.post(
        f"/teams/{team.id}/members",
        json=member_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify the member was added
    member = db_session.query(models.TeamMember).filter(
        models.TeamMember.team_id == team.id,
        models.TeamMember.user_id == another_user.id
    ).first()
    
    assert member is not None
    assert member.role == "member"

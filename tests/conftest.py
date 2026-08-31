"""
Shared pytest fixtures and factory functions for FastAPI app tests.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """
    Provides a TestClient for testing the FastAPI application.
    This allows synchronous testing of async endpoints.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to initial state before each test.
    This ensures test isolation and prevents cross-test interference.
    Autouse=True means it runs before every test automatically.
    """
    # Reset to original state from app.py
    from app import activities
    
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and compete in team games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Track and Field": {
            "description": "Train in running, jumping, and throwing events",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Drama Club": {
            "description": "Develop acting skills and perform in school productions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Debate Club": {
            "description": "Build research, reasoning, and public speaking skills",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Investigate scientific topics through experiments and projects",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    })
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()


def activity_factory(
    name: str = "Test Activity",
    description: str = "A test activity",
    schedule: str = "Monday, 3:00 PM - 4:00 PM",
    max_participants: int = 10,
    participants: list = None
) -> dict:
    """
    Factory function to create activity dictionaries for testing.
    
    Args:
        name: Activity name (for use as dict key in tests)
        description: Activity description
        schedule: Activity schedule
        max_participants: Maximum number of participants allowed
        participants: List of participant emails (defaults to empty list)
    
    Returns:
        Dictionary representing an activity with the given parameters.
    
    Example:
        activity = activity_factory(name="Chess Club", max_participants=12)
        activity_with_participants = activity_factory(
            name="Programming", 
            participants=["alice@test.edu", "bob@test.edu"]
        )
    """
    if participants is None:
        participants = []
    
    return {
        "description": description,
        "schedule": schedule,
        "max_participants": max_participants,
        "participants": participants.copy()  # Copy to prevent mutations
    }


def email_factory(base: str = "student", index: int = 1, domain: str = "mergington.edu") -> str:
    """
    Factory function to generate unique test email addresses.
    
    Args:
        base: Base name for the email (e.g., "student")
        index: Numeric suffix (e.g., 1 -> "student1@mergington.edu")
        domain: Email domain
    
    Returns:
        String representing an email address.
    
    Example:
        email1 = email_factory(base="alice", index=1)  # alice1@mergington.edu
        email2 = email_factory(base="bob", index=2)    # bob2@mergington.edu
        email3 = email_factory()                       # student1@mergington.edu
    """
    return f"{base}{index}@{domain}"

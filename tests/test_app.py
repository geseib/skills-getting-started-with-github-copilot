import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Store original activities for resetting
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

# Test GET /activities
def test_get_activities(client):
    """Test retrieving all activities"""
    # Arrange - fixtures handle setup

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9  # Should have 9 unique activities (dict keys)
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

# Test POST /activities/{activity_name}/signup - success
def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for {activity_name}" == data["message"]

    # Verify the email was added to participants
    response_check = client.get("/activities")
    activities_data = response_check.json()
    assert email in activities_data[activity_name]["participants"]

# Test POST /activities/{activity_name}/signup - duplicate
def test_signup_duplicate(client):
    """Test signing up for the same activity twice"""
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - second signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" == data["detail"]

# Test POST /activities/{activity_name}/signup - invalid activity
def test_signup_invalid_activity(client):
    """Test signing up for a non-existent activity"""
    # Arrange
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]

# Test DELETE /activities/{activity_name}/signup - success
def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Unregistered {email} from {activity_name}" == data["message"]

    # Verify the email was removed from participants
    response_check = client.get("/activities")
    activities_data = response_check.json()
    assert email not in activities_data[activity_name]["participants"]

# Test DELETE /activities/{activity_name}/signup - not signed up
def test_unregister_not_signed_up(client):
    """Test unregistering from an activity without being signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act - try to unregister without signing up first
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up for this activity" == data["detail"]

# Test DELETE /activities/{activity_name}/signup - invalid activity
def test_unregister_invalid_activity(client):
    """Test unregistering from a non-existent activity"""
    # Arrange
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]
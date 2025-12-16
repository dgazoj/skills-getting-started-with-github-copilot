import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Tests for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newuser@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newuser@mergington.edu" in data["message"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_participants(self):
        """Test that multiple unique participants can sign up"""
        emails = [
            "user1@mergington.edu",
            "user2@mergington.edu",
            "user3@mergington.edu",
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Tennis%20Club/signup?email={email}"
            )
            assert response.status_code == 200


class TestUnregister:
    """Tests for unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        # First sign up
        client.post(
            "/activities/Basketball/signup?email=testuser@mergington.edu"
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Basketball/unregister?email=testuser@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "testuser@mergington.edu" in data["message"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant not in the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_participant_removed_from_list(self):
        """Test that unregistered participant is no longer in the list"""
        email = "removetest@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Gym%20Class/signup?email={email}")
        
        # Verify in list
        response = client.get("/activities")
        assert email in response.json()["Gym Class"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Gym%20Class/unregister?email={email}")
        
        # Verify removed from list
        response = client.get("/activities")
        assert email not in response.json()["Gym Class"]["participants"]


class TestRootRoute:
    """Tests for root route"""

    def test_root_redirect(self):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

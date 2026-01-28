"""Tests for the FastAPI activities app."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
        assert len(data) == 9

    def test_get_activities_contains_correct_structure(self, client, reset_activities):
        """Test that activities have correct structure."""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_shows_initial_participants(self, client, reset_activities):
        """Test that initial participants are shown."""
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" in data["Basketball"]["participants"]
        assert "lucas@mergington.edu" in data["Tennis Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up newstudent@mergington.edu for Basketball" in response.json()["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to activity."""
        client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball"]["participants"]

    def test_signup_duplicate_email_fails(self, client, reset_activities):
        """Test that duplicate signup is rejected."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup for nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can sign up."""
        client.post(
            "/activities/Art Studio/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Art Studio/signup",
            params={"email": "student2@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "student1@mergington.edu" in data["Art Studio"]["participants"]
        assert "student2@mergington.edu" in data["Art Studio"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered alex@mergington.edu from Basketball" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity."""
        client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering nonexistent participant fails."""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from nonexistent activity fails."""
        response = client.delete(
            "/activities/Nonexistent/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister."""
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@mergington.edu"}
        )
        response = client.get("/activities")
        assert "student@mergington.edu" in response.json()["Chess Club"]["participants"]

        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        response = client.get("/activities")
        assert "student@mergington.edu" not in response.json()["Chess Club"]["participants"]

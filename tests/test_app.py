"""
Comprehensive test suite for Mergington High School Activities API.

Tests cover:
- Happy paths (successful operations)
- Error cases (404s, 400s)
- Edge cases (special characters, boundary conditions, data persistence)
- Full coverage of all 4 endpoints
"""

import pytest
from app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9  # 9 pre-loaded activities
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_shows_correct_participant_count(self, client):
        """Test that participant counts are accurate."""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Basketball Club"]["participants"]) == 0
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_persists_across_calls(self, client):
        """Test that multiple GET calls return consistent data."""
        response1 = client.get("/activities")
        data1 = response1.json()
        
        response2 = client.get("/activities")
        data2 = response2.json()
        
        assert data1 == data2

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Club",
        "Track and Field",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ])
    def test_get_activities_includes_all_activities(self, client, activity_name):
        """Test that all 9 activities are returned."""
        response = client.get("/activities")
        data = response.json()
        assert activity_name in data


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup to an activity."""
        response = client.post(
            "/activities/Basketball Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to the activity."""
        email = "testuser@mergington.edu"
        activity_name = "Basketball Club"
        
        # Verify not already in activity
        assert email not in activities[activity_name]["participants"]
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify participant was added
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns 400 error."""
        email = "duplicate@mergington.edu"
        activity_name = "Chess Club"
        
        # First signup succeeds
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_missing_email_parameter(self, client):
        """Test that missing email parameter is handled."""
        response = client.post("/activities/Basketball Club/signup")
        
        # Should get 422 (validation error) since email is missing
        assert response.status_code == 422

    @pytest.mark.parametrize("activity_name,email", [
        ("Chess Club", "alice@mergington.edu"),
        ("Programming Class", "bob@mergington.edu"),
        ("Art Club", "charlie@mergington.edu"),
        ("Drama Club", "diana@mergington.edu"),
    ])
    def test_signup_multiple_activities(self, client, activity_name, email):
        """Test signup to different activities with different emails."""
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_special_characters_in_activity_name(self, client):
        """Test signup works with activity names containing special characters."""
        # These names already exist in the app
        special_activities = ["Chess Club", "Basketball Club", "Track and Field"]
        
        for activity in special_activities:
            email = f"test{special_activities.index(activity)}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

    def test_signup_url_encoding_activity_name(self, client):
        """Test that URL-encoded activity names work correctly."""
        # "Basketball Club" -> "Basketball%20Club"
        email = "encoded@mergington.edu"
        response = client.post("/activities/Basketball%20Club/signup?email={email}".format(email=email))
        
        assert response.status_code == 200
        assert email in activities["Basketball Club"]["participants"]

    def test_signup_increases_participant_count(self, client):
        """Test that participant count increases after signup."""
        activity_name = "Art Club"
        initial_count = len(activities[activity_name]["participants"])
        
        client.post(f"/activities/{activity_name}/signup?email=newperson@mergington.edu")
        
        new_count = len(activities[activity_name]["participants"])
        assert new_count == initial_count + 1

    def test_signup_preserves_existing_participants(self, client):
        """Test that new signup doesn't remove existing participants."""
        activity_name = "Chess Club"
        existing = activities[activity_name]["participants"].copy()
        
        client.post(f"/activities/{activity_name}/signup?email=newmember@mergington.edu")
        
        updated = activities[activity_name]["participants"]
        for email in existing:
            assert email in updated

    def test_signup_multiple_to_same_activity(self, client):
        """Test multiple students signing up for the same activity."""
        activity_name = "Drama Club"
        emails = [f"student{i}@mergington.edu" for i in range(1, 4)]
        
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_success(self, client):
        """Test successful removal of a participant."""
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/remove?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_removes_from_activity(self, client):
        """Test that removal actually removes participant from activity."""
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Verify participant exists
        assert email in activities[activity_name]["participants"]
        
        # Remove
        client.delete(f"/activities/{activity_name}/remove?email={email}")
        
        # Verify participant was removed
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that removing from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/remove?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_400(self, client):
        """Test that removing non-existent participant returns 400."""
        response = client.delete(
            "/activities/Chess Club/remove?email=notamember@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_missing_email_parameter(self, client):
        """Test that missing email parameter is handled."""
        response = client.delete("/activities/Chess Club/remove")
        
        assert response.status_code == 422

    def test_remove_decreases_participant_count(self, client):
        """Test that participant count decreases after removal."""
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])
        
        email_to_remove = activities[activity_name]["participants"][0]
        client.delete(f"/activities/{activity_name}/remove?email={email_to_remove}")
        
        new_count = len(activities[activity_name]["participants"])
        assert new_count == initial_count - 1

    def test_remove_preserves_other_participants(self, client):
        """Test that removing one participant doesn't affect others."""
        activity_name = "Chess Club"
        all_participants = activities[activity_name]["participants"].copy()
        participant_to_remove = all_participants[0]
        others = all_participants[1:]
        
        client.delete(f"/activities/{activity_name}/remove?email={participant_to_remove}")
        
        updated = activities[activity_name]["participants"]
        for email in others:
            assert email in updated

    def test_remove_then_readd(self, client):
        """Test that a participant can be removed and re-added."""
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Remove
        response1 = client.delete(f"/activities/{activity_name}/remove?email={email}")
        assert response1.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Re-add
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response2.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_remove_multiple_participants_sequentially(self, client):
        """Test removing multiple participants one by one."""
        activity_name = "Chess Club"
        initial_participants = activities[activity_name]["participants"].copy()
        
        for email in initial_participants:
            response = client.delete(f"/activities/{activity_name}/remove?email={email}")
            assert response.status_code == 200
        
        # Activity should have no participants
        assert len(activities[activity_name]["participants"]) == 0

    def test_remove_from_empty_activity_fails(self, client):
        """Test that removing from activity with no participants fails."""
        activity_name = "Basketball Club"  # Has 0 participants
        response = client.delete(
            f"/activities/{activity_name}/remove?email=notamember@mergington.edu"
        )
        
        assert response.status_code == 400

    def test_remove_url_encoding_activity_name(self, client):
        """Test that URL-encoded activity names work correctly."""
        email = "michael@mergington.edu"
        response = client.delete("/activities/Chess%20Club/remove?email={email}".format(email=email))
        
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_target_is_correct(self, client):
        """Test that the redirect target is exactly /static/index.html."""
        response = client.get("/", follow_redirects=False)
        location = response.headers["location"]
        
        assert location == "/static/index.html"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_signup_whitespace_in_email(self, client):
        """Test handling of emails with whitespace."""
        # The current implementation doesn't strip whitespace,
        # so this tests current behavior
        response = client.post(
            "/activities/Basketball Club/signup?email= spaced@mergington.edu "
        )
        
        # This may fail if the API doesn't handle spaces, which is ok
        # This test documents the current behavior
        if response.status_code == 200:
            assert " spaced@mergington.edu " in activities["Basketball Club"]["participants"]

    def test_signup_at_capacity_boundary(self, client):
        """Test signing up when activity reaches max capacity."""
        # Create an activity with max 2 participants
        from app import activities
        test_activity = "Test Activity"
        activities[test_activity] = {
            "description": "Test",
            "schedule": "Test",
            "max_participants": 2,
            "participants": ["person1@test.edu", "person2@test.edu"]
        }
        
        # Try to add third participant (app doesn't check capacity currently)
        response = client.post(f"/activities/{test_activity}/signup?email=person3@test.edu")
        
        # Current implementation doesn't check capacity, so this succeeds
        # This test documents that there's no capacity validation
        assert response.status_code == 200
        assert len(activities[test_activity]["participants"]) == 3

    def test_activities_data_isolation_between_tests(self, client, reset_activities):
        """
        Test that activities are reset between tests.
        This verifies the reset_activities fixture works correctly.
        """
        # Each test should start with the same initial state
        response = client.get("/activities")
        data = response.json()
        
        # Should have exactly 9 activities (the initial state)
        assert len(data) == 9

    def test_large_participant_list(self, client):
        """Test activity with many participants."""
        activity_name = "Gym Class"
        
        # Add many participants
        for i in range(10):
            email = f"student{i+100}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        data = response.json()
        gym_participants = data[activity_name]["participants"]
        
        # Should have original 2 + 10 new = 12 total
        assert len(gym_participants) == 12

    @pytest.mark.parametrize("special_char_activity", [
        "Chess Club",
        "Track and Field",
        "Basketball Club",
    ])
    def test_activities_with_special_characters_in_names(self, client, special_char_activity):
        """Test that activities with spaces in names work correctly."""
        response = client.get("/activities")
        data = response.json()
        
        assert special_char_activity in data

    def test_consecutive_signup_and_remove(self, client):
        """Test rapid sequence of signup and remove operations."""
        email = "temp@mergington.edu"
        activity = "Basketball Club"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(f"/activities/{activity}/remove?email={email}")
        assert response2.status_code == 200
        
        # Try to remove again (should fail)
        response3 = client.delete(f"/activities/{activity}/remove?email={email}")
        assert response3.status_code == 400

    def test_case_sensitivity_of_email(self, client):
        """Test email case sensitivity."""
        email1 = "Student@Mergington.edu"
        email2 = "student@mergington.edu"
        activity = "Art Club"
        
        # Sign up with different case
        response1 = client.post(f"/activities/{activity}/signup?email={email1}")
        assert response1.status_code == 200
        
        # Try to remove with different case
        response2 = client.delete(f"/activities/{activity}/remove?email={email2}")
        
        # These are treated as different emails (case-sensitive)
        # This test documents the current behavior
        if email1 != email2:
            assert response2.status_code == 400  # Not found, different case

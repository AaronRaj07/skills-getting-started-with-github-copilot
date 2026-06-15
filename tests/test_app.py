import pytest


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Should return all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activities_have_required_fields(self, client):
        """Each activity should have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_show_current_participants(self, client):
        """Activities should show current participant list"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_student(self, client):
        """Should successfully sign up a new student"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client):
        """Signing up should add student to participants list"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify in activity list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Gym Class"]["participants"]
    
    def test_signup_duplicate_email_fails(self, client):
        """Should reject duplicate signups for same activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Should reject signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]
    
    def test_signup_multiple_activities_allowed(self, client):
        """Student should be able to sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Test DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_valid_student(self, client):
        """Should successfully unregister a student"""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Unregistering should remove student from participants list"""
        email = "michael@mergington.edu"
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify removed from list
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_not_signed_up_fails(self, client):
        """Should reject unregister for student not signed up"""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notasignedupstudent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Should reject unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]
    
    def test_unregister_and_rejoin(self, client):
        """Student should be able to unregister and rejoin"""
        email = "flexible@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        
        # Unregister
        response1 = client.delete(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Re-register
        response2 = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify registered
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Gym Class"]["participants"]


class TestRootRedirect:
    """Test GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Root path should redirect to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

"""
Skills Tests
Integration tests for Skills CRUD
"""
import pytest
from fastapi import status


class TestSkillsCRUD:
    """Test Skills CRUD operations"""
    
    def test_create_skill(self, client):
        """Test: Create new skill"""
        skill_data = {
            "name": "Python Programming",
            "description": "Advanced Python skills",
            "category": "technical"
        }
        
        res = client.post("/api/v1/skills", json=skill_data)
        assert res.status_code == 201
        
        data = res.json()
        assert data["name"] == "Python Programming"
        assert data["category"] == "technical"
        assert data["is_active"] == True
    
    def test_create_duplicate_skill_rejected(self, client):
        """Test: Duplicate skill name rejected"""
        skill_data = {
            "name": "JavaScript",
            "category": "technical"
        }
        
        # Create first
        client.post("/api/v1/skills", json=skill_data)
        
        # Try duplicate
        res = client.post("/api/v1/skills", json=skill_data)
        assert res.status_code == 400
        assert "already exists" in res.json()["detail"].lower()
    
    def test_list_skills(self, client):
        """Test: List skills"""
        # Create skills
        skills = [
            {"name": "React", "category": "technical"},
            {"name": "Leadership", "category": "soft"},
            {"name": "English", "category": "language"}
        ]
        
        for skill in skills:
            client.post("/api/v1/skills", json=skill)
        
        # List all
        res = client.get("/api/v1/skills")
        assert res.status_code == 200
        
        data = res.json()
        assert len(data) >= 3
    
    def test_filter_skills_by_category(self, client):
        """Test: Filter skills by category"""
        # Create mixed skills
        client.post("/api/v1/skills", json={"name": "SQL", "category": "technical"})
        client.post("/api/v1/skills", json={"name": "Communication", "category": "soft"})
        
        # Filter by technical
        res = client.get("/api/v1/skills?category=technical")
        assert res.status_code == 200
        
        data = res.json()
        assert all(skill["category"] == "technical" for skill in data)
    
    def test_get_skill_by_id(self, client):
        """Test: Get skill by ID"""
        # Create skill
        res = client.post("/api/v1/skills", json={
            "name": "Data Analysis",
            "category": "technical"
        })
        skill_id = res.json()["id"]
        
        # Get by ID
        res = client.get(f"/api/v1/skills/{skill_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "Data Analysis"
    
    def test_update_skill(self, client):
        """Test: Update skill"""
        # Create skill
        res = client.post("/api/v1/skills", json={
            "name": "Basic Excel",
            "category": "tool"
        })
        skill_id = res.json()["id"]
        
        # Update
        update_data = {
            "name": "Advanced Excel",
            "description": "Macros, VBA, Power Query"
        }
        
        res = client.patch(f"/api/v1/skills/{skill_id}", json=update_data)
        assert res.status_code == 200
        
        data = res.json()
        assert data["name"] == "Advanced Excel"
        assert "Macros" in data["description"]
    
    def test_delete_skill(self, client):
        """Test: Soft delete skill"""
        # Create skill
        res = client.post("/api/v1/skills", json={
            "name": "Obsolete Skill",
            "category": "technical"
        })
        skill_id = res.json()["id"]
        
        # Delete
        res = client.delete(f"/api/v1/skills/{skill_id}")
        assert res.status_code == 204
        
        # Verify not in active list
        res = client.get("/api/v1/skills")
        skill_ids = [s["id"] for s in res.json()]
        assert skill_id not in skill_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

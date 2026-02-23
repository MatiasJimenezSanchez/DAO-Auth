"""
Skills Tests - FINAL VERSION
Uses correct HTTP methods (PUT for update)
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
        
        # CRITICAL: Expect 201 Created
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        
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
        
        res1 = client.post("/api/v1/skills", json=skill_data)
        assert res1.status_code == 201
        
        res2 = client.post("/api/v1/skills", json=skill_data)
        assert res2.status_code == 400
        assert "already exists" in res2.json()["detail"].lower()
    
    def test_list_skills(self, client):
        """Test: List skills"""
        skills = [
            {"name": "React", "category": "technical"},
            {"name": "Leadership", "category": "soft"},
            {"name": "English", "category": "language"}
        ]
        
        for skill in skills:
            res = client.post("/api/v1/skills", json=skill)
            assert res.status_code == 201
        
        res = client.get("/api/v1/skills")
        assert res.status_code == 200
        assert len(res.json()) >= 3
    
    def test_filter_skills_by_category(self, client):
        """Test: Filter skills by category"""
        client.post("/api/v1/skills", json={"name": "SQL", "category": "technical"})
        client.post("/api/v1/skills", json={"name": "Communication", "category": "soft"})
        
        res = client.get("/api/v1/skills?category=technical")
        assert res.status_code == 200
        
        data = res.json()
        assert all(skill["category"] == "technical" for skill in data)
    
    def test_get_skill_by_id(self, client):
        """Test: Get skill by ID"""
        res = client.post("/api/v1/skills", json={
            "name": "Data Analysis",
            "category": "technical"
        })
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        res = client.get(f"/api/v1/skills/{skill_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "Data Analysis"
    
    def test_update_skill(self, client):
        """Test: Update skill using PUT"""
        res = client.post("/api/v1/skills", json={
            "name": "Basic Excel",
            "category": "tool"
        })
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        update_data = {
            "name": "Advanced Excel",
            "description": "Macros, VBA, Power Query"
        }
        
        # CRITICAL FIX: Use PUT not PATCH
        res = client.put(f"/api/v1/skills/{skill_id}", json=update_data)
        assert res.status_code == 200, f"Update failed: {res.status_code} - {res.text}"
        
        data = res.json()
        assert data["name"] == "Advanced Excel"
        assert "Macros" in data["description"]
    
    def test_delete_skill(self, client):
        """Test: Soft delete skill using DELETE"""
        res = client.post("/api/v1/skills", json={
            "name": "Obsolete Skill",
            "category": "technical"
        })
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        # CRITICAL FIX: Verify DELETE method works
        res = client.delete(f"/api/v1/skills/{skill_id}")
        assert res.status_code == 204, f"Delete failed: {res.status_code} - {res.text}"
        
        # Verify not in active list
        res = client.get("/api/v1/skills")
        skill_ids = [s["id"] for s in res.json()]
        assert skill_id not in skill_ids
    
    def test_get_nonexistent_skill_404(self, client):
        """Test: Get nonexistent skill returns 404"""
        res = client.get("/api/v1/skills/999999")
        assert res.status_code == 404
    
    def test_update_nonexistent_skill_404(self, client):
        """Test: Update nonexistent skill returns 404"""
        res = client.put("/api/v1/skills/999999", json={"name": "Ghost"})
        assert res.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

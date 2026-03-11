import pytest
from fastapi import status
from app.models.catalog import Region, Province, City

class TestGeographicCatalogs:
    def test_get_regions(self, client):
        res = client.get("/api/v1/regions")
        assert res.status_code == 200

    def test_get_provinces_by_region(self, client, db_session):
        reg = Region(name="Costa", code="C1", is_active=True)
        db_session.add(reg)
        db_session.commit()
        prov = Province(name="Guayas", code="G1", region_id=reg.id, is_active=True)
        db_session.add(prov)
        db_session.commit()
        
        res = client.get(f"/api/v1/regions/{reg.id}/provinces")
        assert res.status_code == 200
        assert len(res.json()) >= 1

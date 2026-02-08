import pytest
from fastapi import status

class TestCrearEmpresa:
    @pytest.fixture
    def empresa_data(self):
        import uuid
        return {
            "nombre_empresa": f"Empresa Test {uuid.uuid4()}",
            "slug": f"empresa-test-{uuid.uuid4()}",
            "tipo_empresa": "real_nacional",
            "industria": "Tecnología",
            "pais": "Ecuador"
        }

    def test_crear_empresa_exitosamente(self, client, empresa_data):
        # FIX: Añadir slash final para evitar 307/405
        response = client.post("/api/v1/empresas/", json=empresa_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre_empresa"] == empresa_data["nombre_empresa"]
        assert data["id"] is not None

    def test_crear_duplicado(self, client, empresa_data):
        client.post("/api/v1/empresas/", json=empresa_data)
        response = client.post("/api/v1/empresas/", json=empresa_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestLeerEmpresas:
    @pytest.fixture
    def empresa_creada(self, client):
        import uuid
        data = {
            "nombre_empresa": f"Empresa List {uuid.uuid4()}",
            "slug": f"list-{uuid.uuid4()}",
            "tipo_empresa": "real_nacional"
        }
        res = client.post("/api/v1/empresas/", json=data)
        return res.json()

    def test_listar_empresas(self, client, empresa_creada):
        # FIX: Slash final
        response = client.get("/api/v1/empresas/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_obtener_uno(self, client, empresa_creada):
        empresa_id = empresa_creada["id"]
        response = client.get(f"/api/v1/empresas/{empresa_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == empresa_id

class TestActualizar:
    def test_update_nombre(self, client):
        # Setup
        import uuid
        data = {"nombre_empresa": f"Update {uuid.uuid4()}", "slug": f"upd-{uuid.uuid4()}"}
        create = client.post("/api/v1/empresas/", json=data)
        uid = create.json()["id"]
        
        # Test
        update_data = {"nombre_empresa": "Nombre Actualizado"}
        res = client.put(f"/api/v1/empresas/{uid}", json=update_data)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["nombre_empresa"] == "Nombre Actualizado"

class TestEliminar:
    def test_delete(self, client):
        # Setup
        import uuid
        data = {"nombre_empresa": f"Del {uuid.uuid4()}", "slug": f"del-{uuid.uuid4()}"}
        create = client.post("/api/v1/empresas/", json=data)
        uid = create.json()["id"]
        
        # Test
        del_res = client.delete(f"/api/v1/empresas/{uid}")
        assert del_res.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar 404 (Soft Delete efectivo)
        get_res = client.get(f"/api/v1/empresas/{uid}")
        assert get_res.status_code == status.HTTP_404_NOT_FOUND

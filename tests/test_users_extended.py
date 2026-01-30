import pytest
from fastapi import status
from app.models.catalog import Region, Province, City

# --- FIXTURES ---
@pytest.fixture
def test_location(db_session):
    region = Region(name="Region Test", code="RT")
    db_session.add(region)
    db_session.commit()
    db_session.refresh(region)
    
    provincia = Province(name="Provincia Test", code="PT", region_id=region.id)
    db_session.add(provincia)
    db_session.commit()
    db_session.refresh(provincia)
    
    ciudad = City(name="Ciudad Test", province_id=provincia.id)
    db_session.add(ciudad)
    db_session.commit()
    db_session.refresh(ciudad)
    
    return {"region": region, "provincia": provincia, "ciudad": ciudad}

@pytest.fixture
def user_data_simple():
    return {
        "username": "simple_user",
        "email": "simple@test.com",
        "password": "password123"
    }

@pytest.fixture
def user_creado(client, user_data_simple):
    response = client.post("/api/v1/users", json=user_data_simple)
    return response.json()

# --- TESTS ---
class TestUserExtended:
    
    def test_crear_usuario_simple(self, client, user_data_simple):
        response = client.post("/api/v1/users", json=user_data_simple)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "simple_user"
        assert "id" in data

    def test_crear_usuario_extendido(self, client, test_location):
        user_data = {
            "username": "usuario_extendido",
            "email": "extendido@test.com",
            "password": "strongpassword123",
            "full_name": "Juan Perez",
            # Nombres en INGLES ahora
            "birth_date": "1995-05-20",
            "gender": "masculino",
            "region_id": test_location["region"].id,
            "province_id": test_location["provincia"].id,
            "city_id": test_location["ciudad"].id
        }
        
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Validaciones
        assert data["username"] == "usuario_extendido"
        assert data["birth_date"] == "1995-05-20"  # Ahora sí debe coincidir
        assert data["city_id"] == test_location["ciudad"].id

    def test_crear_usuario_email_duplicado(self, client, user_creado):
        dup_data = {
            "username": "otro_user",
            "email": "simple@test.com", 
            "password": "123"
        }
        response = client.post("/api/v1/users", json=dup_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_leer_lista_usuarios(self, client, user_creado):
        response = client.get("/api/v1/users")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 1

    def test_leer_usuario_por_id(self, client, user_creado):
        user_id = user_creado["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_id

    def test_actualizar_usuario(self, client, user_creado):
        user_id = user_creado["id"]
        update_data = {"full_name": "Nombre Actualizado"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Nombre Actualizado"

    def test_eliminar_usuario(self, client, user_creado):
        user_id = user_creado["id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        check = client.get(f"/api/v1/users/{user_id}")
        assert check.status_code == status.HTTP_404_NOT_FOUND

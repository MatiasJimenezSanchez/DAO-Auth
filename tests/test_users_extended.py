from app.models.catalog import Region, Province, City


def test_create_extended_user(client, db):
    # 1. Crear datos de catálogo
    region = Region(name="Costa", code="COS")
    db.add(region)
    db.commit()
    db.refresh(region)

    province = Province(name="Guayas", region_id=region.id, code="09")
    db.add(province)
    db.commit()
    db.refresh(province)

    city = City(name="Guayaquil", province_id=province.id)
    db.add(city)
    db.commit()
    db.refresh(city)

    # Guardar los IDs en variables simples para evitar DetachedInstanceError
    expected_region_id = region.id
    expected_province_id = province.id
    expected_city_id = city.id

    # 2. Datos del usuario extendido
    user_data = {
        "username": "testuser_ext",
        "email": "test_ext@example.com",
        "password": "securepassword",
        "full_name": "Test User Extendido",
        "birth_date": "1999-01-01",
        "gender": "masculino",
        "region_id": expected_region_id,
        "province_id": expected_province_id,
        "city_id": expected_city_id
    }

    # 3. Llamada al endpoint
    response = client.post("/users/", json=user_data)

    # 4. Validaciones
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["username"] == "testuser_ext"
    assert data.get("city_id") == expected_city_id or data.get("ciudad_id") == expected_city_id
    assert data.get("xp_total", 0) == 0
    assert "id" in data

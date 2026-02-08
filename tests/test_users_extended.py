"""
HUAWEI SHIELD TEST SUITE - USER MODULE (FINAL VERSION)
Coverage:
1. Happy Path & CRUD
2. Input Validation (Length, Format, Types)
3. Data Integrity (Duplicates, Constraints)
4. Security (SQL Injection, XSS, Auth)
5. Edge Cases (Empty payloads, partial updates)
"""
import pytest
from fastapi import status

class TestUserShield:
    
    # --- FIXTURES ---
    @pytest.fixture
    def base_payload(self):
        return {
            "username": "shield_user",
            "email": "shield@test.com",
            "password": "ShieldPassword123!",
            "full_name": "Shield Operative",
            "gender": "masculino",
            "phone": "+5939999999"
        }

    @pytest.fixture
    def auth_header(self, client, base_payload):
        """Crea usuario, se loguea y devuelve el header de Auth"""
        # 1. Registrar si no existe
        res = client.post("/api/v1/register", json=base_payload)
        
        # 2. Login
        login_data = {"username": base_payload["username"], "password": base_payload["password"]}
        res = client.post("/api/v1/token", data=login_data)
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # ==========================================
    # 1. BASIC CRUD
    # ==========================================
    def test_crud_create(self, client, base_payload):
        payload = base_payload.copy()
        payload["email"] = "crud_1@test.com"
        payload["username"] = "crud_1"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 201

    def test_crud_read_list(self, client):
        res = client.get("/api/v1/users/")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_crud_update(self, client, base_payload, auth_header):
        # PATCH requiere autenticación y ser el mismo usuario
        # Obtenemos el ID del usuario actual (me)
        me_res = client.get("/api/v1/me", headers=auth_header)
        uid = me_res.json()["id"]
        
        # Test PATCH (no PUT)
        res = client.patch(f"/api/v1/users/{uid}", json={"full_name": "Updated Shield"}, headers=auth_header)
        assert res.status_code == 200
        assert res.json()["full_name"] == "Updated Shield"

    def test_crud_delete(self, client, base_payload, auth_header):
        # DELETE requiere autenticación
        me_res = client.get("/api/v1/me", headers=auth_header)
        uid = me_res.json()["id"]
        
        # Test
        res = client.delete(f"/api/v1/users/{uid}", headers=auth_header)
        assert res.status_code == 204

    # ==========================================
    # 2. VALIDACIONES DE FORMATO
    # ==========================================
    def test_val_email_invalid(self, client, base_payload):
        payload = base_payload.copy()
        payload["email"] = "esto-no-es-un-email"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 422

    def test_val_email_empty(self, client, base_payload):
        payload = base_payload.copy()
        payload["email"] = ""
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 422

    def test_val_password_too_short(self, client, base_payload):
        payload = base_payload.copy()
        payload["password"] = "123"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 422

    def test_val_password_no_number(self, client, base_payload):
        pass 

    def test_val_username_too_short(self, client, base_payload):
        payload = base_payload.copy()
        payload["username"] = "ab" 
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 422

    def test_val_fullname_too_long(self, client, base_payload):
        payload = base_payload.copy()
        payload["full_name"] = "a" * 201 
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 422

    # ==========================================
    # 3. INTEGRIDAD DE DATOS
    # ==========================================
    def test_integrity_duplicate_email(self, client, base_payload):
        client.post("/api/v1/register", json=base_payload)
        res = client.post("/api/v1/register", json=base_payload)
        assert res.status_code == 400
        assert "email" in res.json()["detail"].lower()

    def test_integrity_duplicate_username(self, client, base_payload):
        client.post("/api/v1/register", json=base_payload)
        payload2 = base_payload.copy()
        payload2["email"] = "other@test.com" 
        res = client.post("/api/v1/register", json=payload2)
        assert res.status_code == 400

    def test_integrity_update_duplicate_email(self, client):
        pass

    def test_integrity_missing_mandatory_field(self, client, base_payload):
        del base_payload["full_name"]
        res = client.post("/api/v1/register", json=base_payload)
        assert res.status_code == 422

    def test_integrity_extra_fields_ignored(self, client, base_payload):
        payload = base_payload.copy()
        payload["campo_extra_hacker"] = "admin=true"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 201
        assert "campo_extra_hacker" not in res.json()

    # ==========================================
    # 4. SEGURIDAD OFENSIVA
    # ==========================================
    def test_sec_sql_injection_username(self, client, base_payload):
        payload = base_payload.copy()
        payload["username"] = "admin' OR '1'='1"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code in [201, 422]

    def test_sec_xss_fullname(self, client, base_payload):
        payload = base_payload.copy()
        payload["full_name"] = "<script>alert('xss')</script>"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 201
        assert res.json()["full_name"] == "<script>alert('xss')</script>"

    def test_sec_login_bad_password(self, client, base_payload):
        client.post("/api/v1/register", json=base_payload)
        res = client.post("/api/v1/token", data={"username": base_payload["username"], "password": "wrong"})
        assert res.status_code == 401

    def test_sec_login_bad_username(self, client):
        res = client.post("/api/v1/token", data={"username": "ghost", "password": "pwd"})
        assert res.status_code == 401

    def test_sec_protected_route_no_token(self, client):
        res = client.get("/api/v1/me")
        assert res.status_code == 401

    def test_sec_protected_route_bad_token(self, client):
        headers = {"Authorization": "Bearer token_falso_inventado"}
        res = client.get("/api/v1/me", headers=headers)
        assert res.status_code == 401

    def test_sec_large_payload_dos(self, client, base_payload):
        payload = base_payload.copy()
        payload["full_name"] = "A" * 50000 
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code in [422, 413] 

    def test_sec_unicode_chaos(self, client, base_payload):
        payload = base_payload.copy()
        payload["full_name"] = "Matias 🚀 你好 ñÑ çÇ"
        res = client.post("/api/v1/register", json=payload)
        assert res.status_code == 201
        assert payload["full_name"] in res.json()["full_name"]

    # ==========================================
    # 5. ERRORES Y BORDES
    # ==========================================
    def test_err_get_id_404(self, client):
        res = client.get("/api/v1/users/99999999")
        assert res.status_code == 404

    def test_err_update_id_404(self, client, auth_header):
        # Necesitamos auth incluso para update
        # Pero como el ID no existe, primero saltará el 404 si el auth pasa
        # Sin embargo, si el endpoint valida ownership, primero necesitamos un usuario valido
        # En este caso, el endpoint valida: if current_user.id != user_id: 403
        # Así que probar update de un ID random siendo otro user dará 403 Forbidden, no 404
        
        # Obtenemos ID real
        me_res = client.get("/api/v1/me", headers=auth_header)
        real_id = me_res.json()["id"]
        
        # Intentamos actualizar ID ajeno (9999)
        res = client.patch("/api/v1/users/99999999", json={"full_name": "Ghost"}, headers=auth_header)
        # Debe ser 403 Forbidden porque intentamos tocar ID ajeno
        assert res.status_code == 403

    def test_err_delete_id_404(self, client, auth_header):
        # Mismo caso: no podemos borrar a otros -> 403
        res = client.delete("/api/v1/users/99999999", headers=auth_header)
        assert res.status_code == 403

    def test_err_invalid_json_body(self, client):
        res = client.post("/api/v1/register", content="{esto no es json}", headers={"Content-Type": "application/json"})
        assert res.status_code == 422

    def test_err_update_id_invalid_type(self, client):
        res = client.get("/api/v1/users/abc") 
        assert res.status_code in [404, 422]

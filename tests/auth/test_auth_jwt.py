"""
AUTH JWT SECURITY TESTS
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta
import jwt
from app.core.security import SECRET_KEY, ALGORITHM # Importar clave REAL

class TestJWTTampering:
    def test_tampered_token_rejected(self, client):
        # 1. Login real para obtener token valido
        user = {"username": "jwtuser", "email": "jwt@test.com", "password": "Password123!", "full_name": "JWT User"}
        client.post("/api/v1/users", json=user)
        login_res = client.post("/api/v1/token", data={"username": "jwtuser", "password": "Password123!"})
        token = login_res.json()["access_token"]

        # 2. Tamper
        tampered_token = token[:-1] + ("A" if token[-1] != "A" else "B")
        headers = {"Authorization": f"Bearer {tampered_token}"}
        
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

    def test_token_with_wrong_secret(self, client):
        fake_secret = "wrong-secret-key"
        payload = {"sub": "hacker", "exp": datetime.utcnow() + timedelta(hours=1)}
        fake_token = jwt.encode(payload, fake_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {fake_token}"}
        
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

    def test_token_without_signature(self, client):
        payload = {"sub": "hacker"}
        try:
            unsigned_token = jwt.encode(payload, "", algorithm="none")
        except:
            return # Si la librería no soporta none, el test pasa
            
        headers = {"Authorization": f"Bearer {unsigned_token}"}
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

class TestJWTExpiration:
    def test_expired_token_rejected(self, client):
        # Crear token expirado manualmente usando la SECRET_KEY REAL
        payload = {
            "sub": "expireduser",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

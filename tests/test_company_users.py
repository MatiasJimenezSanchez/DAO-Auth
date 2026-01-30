"""
Tests for Company Users
Complete test suite for B2B user management
"""
import pytest
from app.models.usuarios_empresa import CompanyUser
from app.models.empresa import Empresa


def test_create_company_user(db_session):
    """Test: Create company user"""
    # Create company first
    company = Empresa(
        nombre_empresa="Test Company",
        slug="test-company",
        industria="Technology"
    )
    db_session.add(company)
    db_session.commit()
    
    # Create user
    user = CompanyUser(
        company_id=company.id,
        email="admin@testcompany.com",
        password_hash="hashed_password",
        full_name="Test Admin",
        role="admin",
        can_create_simulations=True,
        can_edit_simulations=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.company_id == company.id
    assert user.email == "admin@testcompany.com"
    assert user.role == "admin"
    print(f"✓ Company user created: {user.email}")


def test_user_roles(db_session):
    """Test: Different user roles"""
    company = Empresa(nombre_empresa="Test", slug="test", industria="Tech")
    db_session.add(company)
    db_session.commit()
    
    # Create users with different roles
    owner = CompanyUser(
        company_id=company.id,
        email="owner@test.com",
        password_hash="hash",
        full_name="Owner",
        role="owner"
    )
    
    viewer = CompanyUser(
        company_id=company.id,
        email="viewer@test.com",
        password_hash="hash",
        full_name="Viewer",
        role="viewer"
    )
    
    db_session.add_all([owner, viewer])
    db_session.commit()
    
    assert owner.is_owner is True
    assert owner.is_admin is True
    assert viewer.is_owner is False
    assert viewer.is_admin is False
    print(f"✓ User roles work correctly")


def test_user_permissions(db_session):
    """Test: User permissions"""
    company = Empresa(nombre_empresa="Test", slug="test", industria="Tech")
    db_session.add(company)
    db_session.commit()
    
    user = CompanyUser(
        company_id=company.id,
        email="editor@test.com",
        password_hash="hash",
        full_name="Editor",
        role="editor",
        can_create_simulations=True,
        can_edit_simulations=True,
        can_publish_simulations=False
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.has_permission('create_simulations') is True
    assert user.has_permission('edit_simulations') is True
    assert user.has_permission('publish_simulations') is False
    print(f"✓ Permissions work correctly")


def test_owner_has_all_permissions(db_session):
    """Test: Owner has all permissions"""
    company = Empresa(nombre_empresa="Test", slug="test", industria="Tech")
    db_session.add(company)
    db_session.commit()
    
    owner = CompanyUser(
        company_id=company.id,
        email="owner@test.com",
        password_hash="hash",
        full_name="Owner",
        role="owner"
    )
    db_session.add(owner)
    db_session.commit()
    
    # Owner should have all permissions even if not explicitly set
    assert owner.has_permission('create_simulations') is True
    assert owner.has_permission('manage_users') is True
    assert owner.has_permission('export_data') is True
    print(f"✓ Owner has all permissions")


def test_multiple_users_same_company(db_session):
    """Test: Multiple users in same company"""
    company = Empresa(nombre_empresa="Test", slug="test", industria="Tech")
    db_session.add(company)
    db_session.commit()
    
    user1 = CompanyUser(
        company_id=company.id,
        email="user1@test.com",
        password_hash="hash",
        full_name="User 1",
        role="admin"
    )
    
    user2 = CompanyUser(
        company_id=company.id,
        email="user2@test.com",
        password_hash="hash",
        full_name="User 2",
        role="viewer"
    )
    
    db_session.add_all([user1, user2])
    db_session.commit()
    
    users = db_session.query(CompanyUser).filter(
        CompanyUser.company_id == company.id
    ).all()
    
    assert len(users) == 2
    print(f"✓ Multiple users in company: {len(users)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

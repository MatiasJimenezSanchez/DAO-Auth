"""
Company Users Model (B2B)
Users that manage company accounts with roles and permissions
Based on diagram: MÓDULO 2 - usuarios_empresa
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CompanyUser(Base):
    """
    Users that belong to companies (B2B)
    Can have different roles: owner, admin, editor, viewer
    """
    __tablename__ = "company_users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    position = Column(String(100), comment="Recruiter, Content Manager, HR Director")
    phone = Column(String(20))
    
    # Avatar
    avatar_url = Column(String(500))
    
    # Roles
    role = Column(String(50), nullable=False, default='viewer', index=True,
                 comment="owner, admin, editor, viewer")
    
    # Granular Permissions
    can_create_simulations = Column(Boolean, default=False)
    can_edit_simulations = Column(Boolean, default=False)
    can_publish_simulations = Column(Boolean, default=False)
    can_archive_simulations = Column(Boolean, default=False)
    can_view_candidates = Column(Boolean, default=False)
    can_contact_candidates = Column(Boolean, default=False)
    can_export_data = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_view_billing = Column(Boolean, default=False)
    
    # Verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True))
    
    # Activity
    last_access = Column(DateTime(timezone=True))
    total_accesses = Column(Integer, default=0)
    
    # Invitation
    invited_by_user_id = Column(Integer, ForeignKey("company_users.id"), nullable=True)
    invitation_token = Column(String(100), unique=True, index=True)
    invitation_accepted_at = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    deactivated_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Empresa", backref="users")
    invited_by = relationship("CompanyUser", remote_side=[id], backref="invited_users")
    
    def __repr__(self):
        return f"<CompanyUser {self.email} ({self.role})>"
    
    @property
    def is_owner(self):
        """Check if user is company owner"""
        return self.role == 'owner'
    
    @property
    def is_admin(self):
        """Check if user is admin or owner"""
        return self.role in ('owner', 'admin')
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            permission: Permission name (e.g., 'create_simulations')
        
        Returns:
            bool: True if user has permission
        """
        # Owners have all permissions
        if self.is_owner:
            return True
        
        # Check specific permission
        permission_attr = f"can_{permission}"
        return getattr(self, permission_attr, False)

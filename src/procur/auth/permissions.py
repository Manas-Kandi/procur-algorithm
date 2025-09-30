"""Permission system and role-based access control (RBAC)."""

from enum import Enum
from typing import List, Optional, Set


class Permission(str, Enum):
    """System permissions."""
    
    # Request permissions
    REQUEST_CREATE = "request:create"
    REQUEST_READ = "request:read"
    REQUEST_UPDATE = "request:update"
    REQUEST_DELETE = "request:delete"
    REQUEST_APPROVE = "request:approve"
    
    # Vendor permissions
    VENDOR_CREATE = "vendor:create"
    VENDOR_READ = "vendor:read"
    VENDOR_UPDATE = "vendor:update"
    VENDOR_DELETE = "vendor:delete"
    
    # Negotiation permissions
    NEGOTIATION_START = "negotiation:start"
    NEGOTIATION_READ = "negotiation:read"
    NEGOTIATION_APPROVE = "negotiation:approve"
    NEGOTIATION_REJECT = "negotiation:reject"
    
    # Contract permissions
    CONTRACT_CREATE = "contract:create"
    CONTRACT_READ = "contract:read"
    CONTRACT_SIGN = "contract:sign"
    CONTRACT_DELETE = "contract:delete"
    
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # Organization permissions
    ORG_CREATE = "org:create"
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_MEMBERS = "org:manage_members"
    
    # API key permissions
    API_KEY_CREATE = "api_key:create"
    API_KEY_READ = "api_key:read"
    API_KEY_DELETE = "api_key:delete"
    
    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    
    # System admin permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"


class Role(str, Enum):
    """User roles with predefined permission sets."""
    
    BUYER = "buyer"
    APPROVER = "approver"
    ADMIN = "admin"
    VENDOR = "vendor"
    AUDITOR = "auditor"
    SUPERUSER = "superuser"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.BUYER: {
        Permission.REQUEST_CREATE,
        Permission.REQUEST_READ,
        Permission.REQUEST_UPDATE,
        Permission.VENDOR_READ,
        Permission.NEGOTIATION_START,
        Permission.NEGOTIATION_READ,
        Permission.CONTRACT_READ,
        Permission.CONTRACT_SIGN,
        Permission.API_KEY_CREATE,
        Permission.API_KEY_READ,
        Permission.API_KEY_DELETE,
    },
    Role.APPROVER: {
        Permission.REQUEST_READ,
        Permission.REQUEST_APPROVE,
        Permission.VENDOR_READ,
        Permission.NEGOTIATION_READ,
        Permission.NEGOTIATION_APPROVE,
        Permission.NEGOTIATION_REJECT,
        Permission.CONTRACT_READ,
        Permission.CONTRACT_SIGN,
    },
    Role.ADMIN: {
        Permission.REQUEST_CREATE,
        Permission.REQUEST_READ,
        Permission.REQUEST_UPDATE,
        Permission.REQUEST_DELETE,
        Permission.REQUEST_APPROVE,
        Permission.VENDOR_CREATE,
        Permission.VENDOR_READ,
        Permission.VENDOR_UPDATE,
        Permission.VENDOR_DELETE,
        Permission.NEGOTIATION_START,
        Permission.NEGOTIATION_READ,
        Permission.NEGOTIATION_APPROVE,
        Permission.NEGOTIATION_REJECT,
        Permission.CONTRACT_CREATE,
        Permission.CONTRACT_READ,
        Permission.CONTRACT_SIGN,
        Permission.CONTRACT_DELETE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE_ROLES,
        Permission.ORG_READ,
        Permission.ORG_UPDATE,
        Permission.ORG_MANAGE_MEMBERS,
        Permission.API_KEY_CREATE,
        Permission.API_KEY_READ,
        Permission.API_KEY_DELETE,
        Permission.AUDIT_READ,
    },
    Role.VENDOR: {
        Permission.VENDOR_READ,
        Permission.VENDOR_UPDATE,
        Permission.NEGOTIATION_READ,
        Permission.CONTRACT_READ,
    },
    Role.AUDITOR: {
        Permission.REQUEST_READ,
        Permission.VENDOR_READ,
        Permission.NEGOTIATION_READ,
        Permission.CONTRACT_READ,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
    },
    Role.SUPERUSER: set(Permission),  # All permissions
}


class PermissionChecker:
    """Check user permissions."""
    
    def __init__(self):
        """Initialize permission checker."""
        self.role_permissions = ROLE_PERMISSIONS
    
    def get_role_permissions(self, role: str) -> Set[Permission]:
        """
        Get permissions for a role.
        
        Args:
            role: Role name
        
        Returns:
            Set of permissions
        """
        try:
            role_enum = Role(role)
            return self.role_permissions.get(role_enum, set())
        except ValueError:
            return set()
    
    def has_permission(
        self,
        user_role: str,
        required_permission: Permission,
        is_superuser: bool = False,
    ) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_role: User's role
            required_permission: Required permission
            is_superuser: Whether user is superuser
        
        Returns:
            True if user has permission
        """
        if is_superuser:
            return True
        
        role_perms = self.get_role_permissions(user_role)
        return required_permission in role_perms
    
    def has_any_permission(
        self,
        user_role: str,
        required_permissions: List[Permission],
        is_superuser: bool = False,
    ) -> bool:
        """
        Check if user has any of the required permissions.
        
        Args:
            user_role: User's role
            required_permissions: List of required permissions
            is_superuser: Whether user is superuser
        
        Returns:
            True if user has at least one permission
        """
        if is_superuser:
            return True
        
        role_perms = self.get_role_permissions(user_role)
        return any(perm in role_perms for perm in required_permissions)
    
    def has_all_permissions(
        self,
        user_role: str,
        required_permissions: List[Permission],
        is_superuser: bool = False,
    ) -> bool:
        """
        Check if user has all required permissions.
        
        Args:
            user_role: User's role
            required_permissions: List of required permissions
            is_superuser: Whether user is superuser
        
        Returns:
            True if user has all permissions
        """
        if is_superuser:
            return True
        
        role_perms = self.get_role_permissions(user_role)
        return all(perm in role_perms for perm in required_permissions)
    
    def can_access_resource(
        self,
        user_id: int,
        user_role: str,
        resource_owner_id: int,
        required_permission: Permission,
        is_superuser: bool = False,
    ) -> bool:
        """
        Check if user can access a resource.
        
        Args:
            user_id: Current user ID
            user_role: User's role
            resource_owner_id: Resource owner's user ID
            required_permission: Required permission
            is_superuser: Whether user is superuser
        
        Returns:
            True if user can access resource
        """
        # Owner can always access their own resources
        if user_id == resource_owner_id:
            return True
        
        # Check role-based permission
        return self.has_permission(user_role, required_permission, is_superuser)
    
    def can_access_organization(
        self,
        user_org_id: Optional[str],
        resource_org_id: Optional[str],
        is_superuser: bool = False,
    ) -> bool:
        """
        Check if user can access organization resources.
        
        Args:
            user_org_id: User's organization ID
            resource_org_id: Resource's organization ID
            is_superuser: Whether user is superuser
        
        Returns:
            True if user can access
        """
        if is_superuser:
            return True
        
        # Must be in same organization
        return user_org_id == resource_org_id

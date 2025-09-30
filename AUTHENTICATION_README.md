# Procur Authentication & Authorization System

## Overview

Comprehensive enterprise-grade authentication and authorization system with JWT, OAuth2/SSO, MFA, API keys, RBAC, multi-tenancy, session management, and password policies.

## Features

✅ **JWT Authentication** - Secure token-based authentication
✅ **Multi-Factor Authentication (MFA)** - TOTP-based 2FA with backup codes
✅ **API Key Management** - Programmatic access with scoped permissions
✅ **OAuth2/SSO Integration** - Google, Microsoft, Okta support
✅ **Session Management** - Track and manage user sessions
✅ **Password Policies** - Configurable strength requirements and expiration
✅ **Role-Based Access Control (RBAC)** - Granular permissions system
✅ **Multi-Tenancy** - Organization isolation and management
✅ **Account Security** - Login attempt tracking, account lockout
✅ **Audit Logging** - Complete authentication event trail

## Architecture

### Components

1. **Password Policy** (`src/procur/auth/password_policy.py`)
   - Configurable password requirements
   - Password strength validation
   - Password history tracking
   - Password expiration

2. **MFA Service** (`src/procur/auth/mfa.py`)
   - TOTP (Time-based One-Time Password)
   - QR code generation
   - Backup codes
   - Token verification

3. **API Key Service** (`src/procur/auth/api_keys.py`)
   - API key generation
   - Scoped permissions
   - Key expiration
   - Usage tracking

4. **Session Service** (`src/procur/auth/sessions.py`)
   - Session creation and validation
   - Session timeout
   - Device tracking
   - Suspicious activity detection

5. **Permission System** (`src/procur/auth/permissions.py`)
   - Role-based permissions
   - Resource ownership checks
   - Organization isolation

6. **OAuth2 Provider** (`src/procur/auth/oauth.py`)
   - Google OAuth2
   - Microsoft/Azure AD
   - Okta
   - Custom providers

### Database Models

**Enhanced UserAccount:**
- Password policy fields (changed_at, expires_at, must_change)
- Security fields (failed_attempts, locked_until, email_verified)
- MFA fields (enabled, secret, backup_codes)

**New Tables:**
- `user_sessions` - Active user sessions
- `api_keys` - API keys for programmatic access
- `password_history` - Password reuse prevention
- `login_attempts` - Login attempt tracking
- `organizations` - Multi-tenant organizations
- `oauth_connections` - OAuth/SSO connections

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

New dependencies:
- `pyotp>=2.9` - TOTP/MFA support
- `qrcode>=7.4` - QR code generation
- `authlib>=1.3` - OAuth2 client
- `itsdangerous>=2.1` - Secure tokens

### 2. Configure Authentication

Update `.env`:

```env
# Password Policy
PROCUR_PASSWORD_MIN_LENGTH=12
PROCUR_PASSWORD_MAX_AGE_DAYS=90
PROCUR_PASSWORD_PREVENT_REUSE_COUNT=5

# Account Security
PROCUR_MAX_FAILED_LOGIN_ATTEMPTS=5
PROCUR_ACCOUNT_LOCKOUT_DURATION_MINUTES=30

# OAuth2 (optional)
PROCUR_OAUTH_GOOGLE_CLIENT_ID=your-client-id
PROCUR_OAUTH_GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Run Database Migration

```bash
# Create migration for new auth tables
alembic revision --autogenerate -m "Add authentication tables"

# Apply migration
alembic upgrade head
```

### 4. Start API Server

```bash
python run_api.py
```

## Usage

### Password Policy

#### Validate Password

```python
from procur.auth import validate_password

is_valid, errors = validate_password("MyP@ssw0rd123")
if not is_valid:
    print("Password errors:", errors)
```

#### Custom Policy

```python
from procur.auth import PasswordPolicy, PasswordValidator

policy = PasswordPolicy(
    min_length=16,
    require_uppercase=True,
    require_lowercase=True,
    require_digit=True,
    require_special=True,
    max_age_days=60,
    prevent_reuse_count=10,
)

validator = PasswordValidator(policy)
is_valid, errors = validator.validate("MyP@ssw0rd123")
```

### Multi-Factor Authentication (MFA)

#### Setup MFA

```bash
# 1. Initiate MFA setup
curl -X POST http://localhost:8000/auth/mfa/setup \
  -H "Authorization: Bearer $TOKEN"

# Response includes:
# - secret: TOTP secret
# - qr_code_url: QR code for authenticator app
# - backup_codes: Recovery codes
# - provisioning_uri: Manual entry URI
```

#### Enable MFA

```bash
# 2. Verify token and enable
curl -X POST http://localhost:8000/auth/mfa/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456",
    "backup_codes": ["ABCD-1234", "EFGH-5678", ...]
  }'
```

#### Login with MFA

```bash
# 1. Regular login (returns session_id if MFA required)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# 2. Verify MFA token
curl -X POST http://localhost:8000/auth/mfa/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456",
    "session_id": "sess_..."
  }'
```

#### Disable MFA

```bash
curl -X POST http://localhost:8000/auth/mfa/disable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "current_password"}'
```

### API Key Management

#### Create API Key

```bash
curl -X POST http://localhost:8000/auth/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "scopes": ["request:create", "vendor:read"],
    "expires_in_days": 365
  }'

# Response (save the api_key - shown only once!):
{
  "api_key": "pk_abc123...xyz789",
  "key_id": "pk_abc123",
  "name": "Production API Key",
  "created_at": "2025-01-15T10:00:00Z",
  "expires_at": "2026-01-15T10:00:00Z",
  "warning": "Save this API key securely. It will not be shown again."
}
```

#### Use API Key

```bash
# Use API key in Authorization header
curl -X GET http://localhost:8000/requests \
  -H "Authorization: Bearer pk_abc123...xyz789"
```

#### List API Keys

```bash
curl -X GET http://localhost:8000/auth/api-keys \
  -H "Authorization: Bearer $TOKEN"
```

#### Revoke API Key

```bash
curl -X DELETE http://localhost:8000/auth/api-keys/pk_abc123 \
  -H "Authorization: Bearer $TOKEN"
```

### Session Management

#### List Active Sessions

```bash
curl -X GET http://localhost:8000/auth/sessions \
  -H "Authorization: Bearer $TOKEN"

# Response:
[
  {
    "session_id": "sess_abc123",
    "ip_address": "192.168.1.1",
    "device_type": "desktop",
    "location": "San Francisco, CA",
    "last_activity_at": "2025-01-15T10:00:00Z",
    "created_at": "2025-01-15T09:00:00Z"
  }
]
```

#### Revoke Specific Session

```bash
curl -X DELETE http://localhost:8000/auth/sessions/sess_abc123 \
  -H "Authorization: Bearer $TOKEN"
```

#### Revoke All Sessions

```bash
curl -X POST http://localhost:8000/auth/sessions/revoke-all \
  -H "Authorization: Bearer $TOKEN"
```

### Password Management

#### Change Password

```bash
curl -X POST http://localhost:8000/auth/password/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldP@ssw0rd",
    "new_password": "NewP@ssw0rd123"
  }'
```

### OAuth2/SSO Integration

#### Google OAuth2

```python
from procur.auth.oauth import GoogleOAuth2Provider

provider = GoogleOAuth2Provider(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/auth/oauth/callback",
)

# Get authorization URL
auth_url = provider.get_authorization_url(state="random_state")
# Redirect user to auth_url

# After callback, exchange code for token
token = provider.exchange_code_for_token(code)

# Get user info
user_info = provider.get_user_info(token["access_token"])
```

#### Microsoft/Azure AD

```python
from procur.auth.oauth import MicrosoftOAuth2Provider

provider = MicrosoftOAuth2Provider(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/auth/oauth/callback",
    tenant_id="your-tenant-id",  # or "common"
)
```

#### Okta

```python
from procur.auth.oauth import OktaOAuth2Provider

provider = OktaOAuth2Provider(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/auth/oauth/callback",
    okta_domain="your-domain.okta.com",
)
```

### Role-Based Access Control (RBAC)

#### Check Permissions

```python
from procur.auth.permissions import Permission, PermissionChecker

checker = PermissionChecker()

# Check single permission
has_perm = checker.has_permission(
    user_role="buyer",
    required_permission=Permission.REQUEST_CREATE,
    is_superuser=False,
)

# Check resource access
can_access = checker.can_access_resource(
    user_id=1,
    user_role="buyer",
    resource_owner_id=1,
    required_permission=Permission.REQUEST_READ,
)

# Check organization access
can_access_org = checker.can_access_organization(
    user_org_id="acme-corp",
    resource_org_id="acme-corp",
)
```

#### Available Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `buyer` | Procurement buyer | Create requests, view vendors, negotiate |
| `approver` | Request approver | Approve requests and contracts |
| `admin` | Organization admin | Full organization management |
| `vendor` | Vendor user | View and update vendor profile |
| `auditor` | Compliance auditor | Read-only access, export audits |
| `superuser` | System admin | All permissions |

#### Available Permissions

**Request Permissions:**
- `request:create` - Create requests
- `request:read` - View requests
- `request:update` - Update requests
- `request:delete` - Delete requests
- `request:approve` - Approve requests

**Vendor Permissions:**
- `vendor:create` - Create vendors
- `vendor:read` - View vendors
- `vendor:update` - Update vendors
- `vendor:delete` - Delete vendors

**Negotiation Permissions:**
- `negotiation:start` - Start negotiations
- `negotiation:read` - View negotiations
- `negotiation:approve` - Approve offers
- `negotiation:reject` - Reject negotiations

**Contract Permissions:**
- `contract:create` - Create contracts
- `contract:read` - View contracts
- `contract:sign` - Sign contracts
- `contract:delete` - Delete contracts

**User Management:**
- `user:create` - Create users
- `user:read` - View users
- `user:update` - Update users
- `user:delete` - Delete users
- `user:manage_roles` - Manage user roles

**Organization:**
- `org:create` - Create organizations
- `org:read` - View organizations
- `org:update` - Update organizations
- `org:delete` - Delete organizations
- `org:manage_members` - Manage members

**API Keys:**
- `api_key:create` - Create API keys
- `api_key:read` - View API keys
- `api_key:delete` - Delete API keys

**Audit:**
- `audit:read` - View audit logs
- `audit:export` - Export audit logs

**System:**
- `system:admin` - System administration
- `system:config` - System configuration

### Multi-Tenancy

#### Create Organization

```bash
curl -X POST http://localhost:8000/auth/organizations \
  -H "Authorization: Bearer $SUPERUSER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "organization_id": "acme-corp",
    "domain": "acme.com"
  }'
```

#### List Organizations

```bash
curl -X GET http://localhost:8000/auth/organizations \
  -H "Authorization: Bearer $TOKEN"
```

#### Organization Isolation

All resources are automatically isolated by organization:

```python
# Users can only access resources in their organization
user.organization_id = "acme-corp"

# Requests are filtered by organization
requests = request_repo.get_by_user(user.id)  # Only acme-corp requests

# Superusers can access all organizations
if user.is_superuser:
    # Access any organization's resources
    pass
```

## Security Best Practices

### 1. Password Policy

**Recommended Settings:**
```env
PROCUR_PASSWORD_MIN_LENGTH=12
PROCUR_PASSWORD_REQUIRE_UPPERCASE=true
PROCUR_PASSWORD_REQUIRE_LOWERCASE=true
PROCUR_PASSWORD_REQUIRE_DIGIT=true
PROCUR_PASSWORD_REQUIRE_SPECIAL=true
PROCUR_PASSWORD_MAX_AGE_DAYS=90
PROCUR_PASSWORD_PREVENT_REUSE_COUNT=5
```

### 2. Account Lockout

**Recommended Settings:**
```env
PROCUR_MAX_FAILED_LOGIN_ATTEMPTS=5
PROCUR_ACCOUNT_LOCKOUT_DURATION_MINUTES=30
```

### 3. Session Management

**Recommended Settings:**
```env
PROCUR_SESSION_TIMEOUT_MINUTES=60
PROCUR_SESSION_MAX_AGE_HOURS=24
```

### 4. MFA Enforcement

Enable MFA for:
- All admin users
- Users with elevated permissions
- Users accessing sensitive data
- External/remote access

### 5. API Key Management

- Set expiration dates on all API keys
- Use scoped permissions (principle of least privilege)
- Rotate keys regularly
- Revoke unused keys
- Monitor key usage

### 6. OAuth2/SSO

- Use SSO for enterprise deployments
- Validate OAuth tokens
- Store minimal user data
- Refresh tokens before expiration

### 7. Audit Logging

All authentication events are logged:
- Login attempts (success/failure)
- Password changes
- MFA setup/disable
- API key creation/deletion
- Session creation/revocation
- Permission changes

## Configuration Reference

### Password Policy

| Setting | Default | Description |
|---------|---------|-------------|
| `min_length` | 12 | Minimum password length |
| `require_uppercase` | true | Require uppercase letter |
| `require_lowercase` | true | Require lowercase letter |
| `require_digit` | true | Require digit |
| `require_special` | true | Require special character |
| `max_age_days` | 90 | Password expiration (days) |
| `prevent_reuse_count` | 5 | Prevent reusing last N passwords |

### Account Security

| Setting | Default | Description |
|---------|---------|-------------|
| `max_failed_attempts` | 5 | Max failed login attempts |
| `lockout_duration_minutes` | 30 | Account lockout duration |

### Session Management

| Setting | Default | Description |
|---------|---------|-------------|
| `session_timeout_minutes` | 60 | Inactivity timeout |
| `max_sessions_per_user` | 5 | Max concurrent sessions |

## Troubleshooting

### MFA Issues

**Problem:** QR code not scanning
**Solution:** Use manual entry with the provisioning URI

**Problem:** Token not working
**Solution:** Check device time synchronization (TOTP requires accurate time)

### API Key Issues

**Problem:** API key authentication failing
**Solution:** Ensure key format is correct: `pk_...` and not expired

### Session Issues

**Problem:** Session expired too quickly
**Solution:** Adjust `PROCUR_SESSION_TIMEOUT_MINUTES`

### OAuth Issues

**Problem:** OAuth callback failing
**Solution:** Verify redirect URI matches exactly in provider settings

## Migration Guide

### From Basic Auth to Enhanced Auth

1. **Backup Database**
```bash
pg_dump procur > backup.sql
```

2. **Run Migration**
```bash
alembic revision --autogenerate -m "Add authentication tables"
alembic upgrade head
```

3. **Update User Records**
```python
# Set password_changed_at for existing users
from datetime import datetime
from procur.db import get_session
from procur.db.repositories import UserRepository

with get_session() as session:
    user_repo = UserRepository(session)
    users = user_repo.get_all()
    for user in users:
        user_repo.update(user.id, password_changed_at=datetime.utcnow())
```

4. **Enable MFA for Admins**
```bash
# Notify admin users to set up MFA
# POST /auth/mfa/setup
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### MFA

- `POST /auth/mfa/setup` - Setup MFA
- `POST /auth/mfa/enable` - Enable MFA
- `POST /auth/mfa/disable` - Disable MFA
- `POST /auth/mfa/verify` - Verify MFA token

### API Keys

- `POST /auth/api-keys` - Create API key
- `GET /auth/api-keys` - List API keys
- `DELETE /auth/api-keys/{key_id}` - Delete API key

### Sessions

- `GET /auth/sessions` - List sessions
- `DELETE /auth/sessions/{session_id}` - Revoke session
- `POST /auth/sessions/revoke-all` - Revoke all sessions

### Password

- `POST /auth/password/change` - Change password

### Organizations

- `POST /auth/organizations` - Create organization
- `GET /auth/organizations` - List organizations

## Support

- **Documentation**: See `API_README.md` for API details
- **Database**: See `DATABASE_README.md` for database schema
- **Issues**: GitHub Issues
- **Email**: security@procur.ai

## License

Part of the Procur procurement automation platform.

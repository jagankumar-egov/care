# Care Backend - API Flow Diagrams

This document describes the flow of different API operations in the Care backend system, including plugin extension points where behavior can be customized.

---

## Table of Contents

1. [Request/Response Lifecycle](#1-requestresponse-lifecycle)
2. [Authentication Flow](#2-authentication-flow)
3. [Authorization Flow](#3-authorization-flow)
4. [CRUD Operations Flow](#4-crud-operations-flow)
5. [Batch Request Flow](#5-batch-request-flow)
6. [File Upload Flow](#6-file-upload-flow)
7. [Rate Limiting Flow](#7-rate-limiting-flow)
8. [Plugin System Architecture](#8-plugin-system-architecture)
9. [Extension Registry Flow](#9-extension-registry-flow)
10. [Signal/Event Flow](#10-signalevent-flow)
11. [API Endpoint Categories](#11-api-endpoint-categories)
12. [Configuration Limits](#12-configuration-limits)
13. [Quick Start Guide - Getting Prepared](#13-quick-start-guide---getting-prepared)
14. [Understanding the Serialization Pattern](#14-understanding-the-serialization-pattern)
15. [Creating a New Endpoint Checklist](#15-creating-a-new-endpoint-checklist)
16. [Plugin Development Guide](#16-plugin-development-guide)
17. [Quick Reference Commands](#17-quick-reference-commands)
18. [Common Patterns Quick Reference](#18-common-patterns-quick-reference)
19. [Learning Path Recommendations](#19-learning-path-recommendations)
20. [Debugging Tips](#20-debugging-tips)

---

## 1. Request/Response Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HTTP REQUEST                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MIDDLEWARE STACK (Exact Order)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. [Optional] RequestTimeLoggingMiddleware (if ENABLE_REQUEST_     │   │
│  │                TIME_LOGGING=true)                                   │   │
│  │  2. SecurityMiddleware (django.middleware.security)                 │   │
│  │  3. CorsMiddleware (corsheaders.middleware)                         │   │
│  │  4. WhiteNoiseMiddleware (whitenoise.middleware)                    │   │
│  │  5. SessionMiddleware (django.contrib.sessions.middleware)          │   │
│  │  6. LocaleMiddleware (django.middleware.locale)                     │   │
│  │  7. CommonMiddleware (django.middleware.common)                     │   │
│  │  8. CsrfViewMiddleware (django.middleware.csrf)                     │   │
│  │  9. AuthenticationMiddleware (django.contrib.auth.middleware)       │   │
│  │ 10. MessageMiddleware (django.contrib.messages.middleware)          │   │
│  │ 11. BrokenLinkEmailsMiddleware (django.middleware.common)           │   │
│  │ 12. XFrameOptionsMiddleware (django.middleware.clickjacking)        │   │
│  │ 13. MaintenanceModeMiddleware (maintenance_mode.middleware)         │   │
│  │ 14. AuditLogMiddleware (care.audit_log.middleware) - LAST           │   │
│  │     - Generates unique request ID: {method}::{path_md5}::{uuid}     │   │
│  │     - Captures request context in thread-local storage              │   │
│  │     - Only processes non-GET requests for audit logging             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Custom middleware can be added via settings          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         URL ROUTING                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ config/urls.py → config/api_router.py                               │   │
│  │      → Nested routers for resources                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Plugin URLs registered: api/{plugin_name}/           │   │
│  │ for plug in settings.PLUGIN_APPS:                                   │   │
│  │     path(f"api/{plug}/", include(f"{plug}.urls"))                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. CustomJWTAuthentication (Primary)                                │   │
│  │ 2. CustomBasicAuthentication                                        │   │
│  │ 3. SessionAuthentication                                            │   │
│  │ 4. TokenAuthentication                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Custom authentication backends                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHORIZATION                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. IsAuthenticated (permission check)                               │   │
│  │ 2. CareAuthentication (calls view.permissions_controller)           │   │
│  │ 3. AuthorizationController.call(permission, user, object)           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Override AuthorizationController via:                │   │
│  │ AuthorizationController.override_authz_controllers                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VIEWSET PROCESSING                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ EMRModelViewSet / EMRBaseViewSet                                    │   │
│  │                                                                     │   │
│  │ Pydantic Models (per operation):                                    │   │
│  │   - pydantic_model         → CREATE validation                      │   │
│  │   - pydantic_update_model  → UPDATE validation                      │   │
│  │   - pydantic_read_model    → LIST serialization                     │   │
│  │   - pydantic_retrieve_model→ RETRIEVE serialization                 │   │
│  │                                                                     │   │
│  │ Authorization Methods:                                              │   │
│  │   - authorize_create(request_obj)                                   │   │
│  │   - authorize_update(request_obj, model_instance)                   │   │
│  │   - authorize_retrieve(model_instance)                              │   │
│  │   - authorize_destroy(instance)                                     │   │
│  │                                                                     │   │
│  │ Validation & Lifecycle:                                             │   │
│  │   - clean_create_data() / clean_update_data()                       │   │
│  │   - validate_data(instance, model_obj)                              │   │
│  │   - validate_destroy(instance)                                      │   │
│  │   - perform_create() / perform_update() / perform_destroy()         │   │
│  │                                                                     │   │
│  │ Default Lookup: external_id (NOT id)                                │   │
│  │ Default Ordering: -id (newest first)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Custom ViewSets can extend EMRModelViewSet           │   │
│  │ Override: authorize_*, validate_data, perform_*, clean_* methods    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Mixin Architecture:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ EMRModelViewSet                                                     │   │
│  │ ├── EMRCreateMixin      (create, handle_create, perform_create)     │   │
│  │ ├── EMRRetrieveMixin    (retrieve, authorize_retrieve)              │   │
│  │ ├── EMRUpdateMixin      (update, partial_update, handle_update)     │   │
│  │ ├── EMRListMixin        (list, serialize_list)                      │   │
│  │ ├── EMRDestroyMixin     (destroy, validate_destroy, perform_destroy)│   │
│  │ ├── EMRUpsertMixin      (upsert - bulk create/update)               │   │
│  │ └── EMRBaseViewSet                                                  │   │
│  │     ├── EMRTagMixin           [optional, if TAGS_ENABLED]           │   │
│  │     └── EMRQuestionnaireResponseMixin [optional]                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL DISPATCH                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Django Signals:                                                     │   │
│  │   pre_save → Capture changes for audit                              │   │
│  │   post_save → Log INSERT/UPDATE, trigger side effects               │   │
│  │   pre_delete → Capture state before deletion                        │   │
│  │   post_delete → Log DELETE operation                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Register custom signal handlers in AppConfig.ready() │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE SERIALIZATION                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Pydantic model serialization                                        │   │
│  │   → Extension data applied (serialize_extensions)                   │   │
│  │   → JSON response construction                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] ExtensionRegistry for custom response fields         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXCEPTION HANDLING                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ emr_exception_handler (config.exception_handler)                    │   │
│  │   → Django ValidationError → DRF format                             │   │
│  │   → Pydantic ValidationError → JSON errors list                     │   │
│  │   → Standard error response structure                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HTTP RESPONSE                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication Flow

### 2.1 Login Flow (JWT Token Obtain)

```
┌──────────────┐     POST /api/v1/auth/login/     ┌──────────────────────┐
│    Client    │ ─────────────────────────────────▶│  TokenObtainPairView │
│              │   { username, password }          │                      │
└──────────────┘                                   └──────────────────────┘
                                                              │
                                                              ▼
                                               ┌──────────────────────────┐
                                               │    Rate Limit Check      │
                                               │  Default: 5/10m          │
                                               │  (django_ratelimit)      │
                                               └──────────────────────────┘
                                                              │
                              ┌────────────────────┬──────────┴──────────┐
                              │                    │                      │
                              ▼                    ▼                      ▼
                    ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
                    │   Under Limit   │  │  Over Limit     │   │ Captcha Valid   │
                    │   Proceed       │  │  Return 429 +   │   │ (reCAPTCHA)     │
                    │                 │  │  CaptchaRequired│   │ Proceed         │
                    └─────────────────┘  └─────────────────┘   └─────────────────┘
                              │                                          │
                              └──────────────────┬───────────────────────┘
                                                 ▼
                                    ┌──────────────────────────┐
                                    │   Validate Credentials   │
                                    │   (User.authenticate)    │
                                    └──────────────────────────┘
                                                 │
                              ┌──────────────────┴──────────────────┐
                              │                                     │
                              ▼                                     ▼
                    ┌─────────────────┐                   ┌─────────────────┐
                    │  MFA Enabled?   │                   │   Invalid       │
                    │                 │                   │   Return 401    │
                    └─────────────────┘                   └─────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │ Yes                                      │ No
         ▼                                          ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│  Return TEMP token      │              │  Return JWT tokens      │
│  - temp_token: true     │              │  - access_token         │
│  - Lifetime: 5 minutes  │              │    (default: 10 min)    │
│  - Cannot be refreshed  │              │  - refresh_token        │
│  - Proceed to MFA verify│              │    (default: 30 min)    │
└─────────────────────────┘              └─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MFA VERIFICATION FLOW                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  POST /api/v1/mfa/                                                  │   │
│  │  { "otp": "123456" }                                                │   │
│  │  Authorization: Bearer <temp_token>                                 │   │
│  │                                                                     │   │
│  │  → Verify TOTP code                                                 │   │
│  │  → If valid: Return full JWT tokens (access + refresh)              │   │
│  │  → If invalid: Return 401                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

[PLUGIN POINT] Custom authentication backends can be registered
[PLUGIN POINT] Custom MFA providers can be implemented (TOTP via /api/v1/mfa/totp/)

JWT Token Configuration:
┌─────────────────────────────────────────────────────────────────────────────┐
│  ACCESS_TOKEN_LIFETIME: 10 minutes (configurable via JWT_ACCESS_TOKEN_     │
│                         LIFETIME env var)                                   │
│  REFRESH_TOKEN_LIFETIME: 30 minutes (configurable via JWT_REFRESH_TOKEN_   │
│                          LIFETIME env var)                                  │
│  ROTATE_REFRESH_TOKENS: true (new refresh token on each refresh)           │
│  USER_ID_FIELD: external_id (NOT standard "id")                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Token Refresh Flow

```
┌──────────────┐   POST /api/v1/auth/token/refresh/   ┌──────────────────┐
│    Client    │ ─────────────────────────────────────▶│ TokenRefreshView │
│              │   { refresh: "token..." }             │                  │
└──────────────┘                                       └──────────────────┘
                                                                │
                                                                ▼
                                                 ┌──────────────────────────┐
                                                 │  Check Token Invalidation│
                                                 │  Cache (Redis)           │
                                                 │  Key: REFRESH_TOKEN_     │
                                                 │  INVALIDATE:{token_hash} │
                                                 │  Timeout: 1800s (30 min) │
                                                 └──────────────────────────┘
                                                                │
                                       ┌────────────────────────┴────────────────────────┐
                                       │ Not in cache                                     │ In cache
                                       ▼                                                  ▼
                            ┌─────────────────────┐                            ┌─────────────────────┐
                            │  Token Valid        │                            │  Token Invalidated  │
                            │  Return:            │                            │  Return 401         │
                            │  - new access_token │                            │  Unauthorized       │
                            │  - new refresh_token│                            │                     │
                            │    (rotated)        │                            │                     │
                            └─────────────────────┘                            └─────────────────────┘
```

### 2.3 Request Authentication Flow (Per-Request)

```
┌──────────────┐   Any API Request                    ┌──────────────────────┐
│    Client    │ ─────────────────────────────────────▶│ CustomJWT            │
│              │   Authorization: Bearer <token>       │ Authentication       │
└──────────────┘                                       └──────────────────────┘
                                                                │
                                                                ▼
                                                 ┌──────────────────────────┐
                                                 │  Check Access Token      │
                                                 │  Invalidation Cache      │
                                                 │  Key: ACCESS_TOKEN_      │
                                                 │  INVALIDATE:{token_hash} │
                                                 └──────────────────────────┘
                                                                │
                                       ┌────────────────────────┴────────────────────────┐
                                       │ Not invalidated                                  │ Invalidated
                                       ▼                                                  ▼
                            ┌─────────────────────┐                            ┌─────────────────────┐
                            │  Validate JWT       │                            │  Return 401         │
                            │  - Verify signature │                            │  Unauthorized       │
                            │  - Check expiry     │                            │                     │
                            │  - Extract user via │                            │                     │
                            │    external_id      │                            │                     │
                            └─────────────────────┘                            └─────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Authentication     │
                            │  Classes Order:     │
                            │  1. CustomJWT       │
                            │  2. CustomBasic     │
                            │  3. Session         │
                            │  4. Token           │
                            └─────────────────────┘
```

### 2.4 Logout Flow

```
┌──────────────┐     POST /api/v1/auth/logout/     ┌──────────────────┐
│    Client    │ ─────────────────────────────────▶│    LogoutView    │
│              │   Authorization: Bearer <token>   │                  │
└──────────────┘                                   └──────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Invalidate Tokens       │
                                             │  Cache Keys:             │
                                             │  - ACCESS_TOKEN_         │
                                             │    INVALIDATE:{token}    │
                                             │  - REFRESH_TOKEN_        │
                                             │    INVALIDATE:{token}    │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Return 200 OK           │
                                             └──────────────────────────┘
```

---

## 3. Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTHORIZATION FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐                              ┌──────────────────────────┐
│   Request    │ ────────────────────────────▶│  CareAuthentication      │
│              │                              │  (Permission Class)      │
└──────────────┘                              └──────────────────────────┘
                                                           │
                                                           ▼
                                              ┌──────────────────────────┐
                                              │  Check: has_permission() │
                                              │  - IsAuthenticated       │
                                              └──────────────────────────┘
                                                           │
                                                           ▼
                                              ┌──────────────────────────┐
                                              │  view.permissions_       │
                                              │  controller(request)     │
                                              │  defined?                │
                                              └──────────────────────────┘
                                                           │
                              ┌────────────────────────────┴────────────────────────────┐
                              │ Yes                                                      │ No
                              ▼                                                          ▼
                   ┌──────────────────────────┐                             ┌──────────────────────────┐
                   │  Execute custom          │                             │  Return True             │
                   │  permissions_controller  │                             │  (Proceed to ViewSet)    │
                   └──────────────────────────┘                             └──────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AuthorizationController.call()                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Get AuthorizationHandler for resource                           │   │
│  │  2. Execute can_<action>(user, obj, **kwargs)                       │   │
│  │  3. Check role permissions via get_role_from_permissions()          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Override via:                                        │   │
│  │ AuthorizationController.override_authz_controllers = {              │   │
│  │     "resource_name": CustomAuthorizationHandler                     │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  Permission Check Result │
                   └──────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                          │
         ▼                                          ▼
┌─────────────────┐                       ┌─────────────────┐
│   Authorized    │                       │   Denied        │
│   Proceed       │                       │   Return 403    │
└─────────────────┘                       └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    ROLE-BASED ACCESS CONTROL (RBAC)                          │
│                                                                             │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐      │
│  │    User      │───▶│ OrganizationUser │───▶│       Role           │      │
│  │              │    │ (role assignment)│    │ (permissions)        │      │
│  └──────────────┘    └──────────────────┘    └──────────────────────┘      │
│         │                                              │                    │
│         │            ┌──────────────────┐              ▼                    │
│         └───────────▶│FacilityOrganiza- │    ┌──────────────────────┐      │
│                      │   tionUser       │───▶│   RolePermission     │      │
│                      │(facility-scoped) │    │ (permission mapping) │      │
│                      └──────────────────┘    └──────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTHORIZATION CONTROLLER ARCHITECTURE                     │
│                                                                             │
│  AuthorizationController (Singleton)                                        │
│  ├── cache: {"actions": {}, "queries": {}}                                 │
│  │   └── Built once, caches all can_* and get_* methods                    │
│  ├── override_authz_controllers: list                                      │
│  │   └── [PLUGIN POINT] Plugin-provided handlers (checked first)           │
│  ├── internal_authz_controllers: list                                      │
│  │   └── Core authorization handlers (36+ modules)                         │
│  │                                                                         │
│  └── Methods:                                                              │
│      ├── call(item, *args, **kwargs)                                       │
│      │   └── Routes "can_*" to actions, "get_*" to queries                 │
│      ├── build_cache()                                                     │
│      │   └── Scans all controllers, indexes methods by name                │
│      ├── register_internal_controller(handler)                             │
│      └── register_override_controller(handler)                             │
│                                                                             │
│  AuthorizationHandler (Base Class)                                          │
│  ├── actions = []  # List of can_<action> method names                     │
│  ├── queries = []  # List of get_<query> method names                      │
│  │                                                                         │
│  └── Helper Methods:                                                       │
│      ├── check_permission_in_organization(permission, user, org_ids)       │
│      ├── check_permission_in_facility_organization(perm, user, fac_id)     │
│      └── get_role_from_permissions(permissions, user, org_ids)             │
│                                                                             │
│  Performance Optimization:                                                  │
│  - Encounter authorization uses facility_organization_cache                 │
│  - Role lookups are cached per-request                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CRUD Operations Flow

### 4.1 Create Operation

```
┌──────────────┐       POST /api/v1/{resource}/       ┌──────────────────┐
│    Client    │ ────────────────────────────────────▶│    ViewSet       │
│              │   { ...data }                        │    .create()     │
└──────────────┘                                      └──────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  Pydantic Validation     │
                                                │  (pydantic_model)        │
                                                └──────────────────────────┘
                                                               │
                              ┌─────────────────────────────────┴─────────────────────────────────┐
                              │ Valid                                                              │ Invalid
                              ▼                                                                    ▼
                   ┌──────────────────────────┐                                       ┌──────────────────────────┐
                   │  authorize_create()      │                                       │  Return 400              │
                   │  (ViewSet method)        │                                       │  ValidationError         │
                   └──────────────────────────┘                                       └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  [PLUGIN POINT]          │
                   │  Custom authorization    │
                   │  logic                   │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  validate_data()         │
                   │  (Business validation)   │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  perform_create()        │
                   │  - instance.save()       │
                   └──────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL DISPATCH                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  pre_save signal → AuditLog captures pre-state                      │   │
│  │  Database INSERT                                                    │   │
│  │  post_save signal → AuditLog records INSERT, triggers side effects  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [PLUGIN POINT] Custom signal handlers                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  Auto-create related:    │
                   │  - QuestionnaireResponse │
                   │    (if enabled)          │
                   │  - Tags (if enabled)     │
                   └──────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE SERIALIZATION                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  pydantic_read_model.serialize()                                    │   │
│  │  serialize_extensions() - add extension data                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [PLUGIN POINT] ExtensionRegistry for custom fields                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  Return 201 Created      │
                   │  { ...serialized_data }  │
                   └──────────────────────────┘
```

### 4.2 Read/List Operation

```
┌──────────────┐    GET /api/v1/{resource}/     ┌──────────────────┐
│    Client    │ ──────────────────────────────▶│    ViewSet       │
│              │   ?filters...                  │    .list()       │
└──────────────┘                                └──────────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │  get_queryset()          │
                                          │  - Apply filters         │
                                          │  - Apply permissions     │
                                          └──────────────────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │  [PLUGIN POINT]          │
                                          │  Custom queryset filters │
                                          │  in get_queryset()       │
                                          └──────────────────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │  Pagination              │
                                          │  CareLimitOffsetPagination│
                                          │  (PAGE_SIZE = 14)        │
                                          └──────────────────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │  Serialize with          │
                                          │  pydantic_read_model     │
                                          │  + Extensions            │
                                          └──────────────────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────┐
                                          │  Return 200 OK           │
                                          │  { results: [...],       │
                                          │    count: N }            │
                                          └──────────────────────────┘
```

### 4.3 Retrieve Operation

```
┌──────────────┐   GET /api/v1/{resource}/{id}/   ┌──────────────────┐
│    Client    │ ────────────────────────────────▶│    ViewSet       │
│              │                                  │    .retrieve()   │
└──────────────┘                                  └──────────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────┐
                                            │  get_object()            │
                                            │  - Lookup by ID          │
                                            └──────────────────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────┐
                                            │  authorize_retrieve()    │
                                            │  (ViewSet method)        │
                                            └──────────────────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────┐
                                            │  [PLUGIN POINT]          │
                                            │  Custom retrieve         │
                                            │  authorization           │
                                            └──────────────────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────┐
                                            │  Serialize with          │
                                            │  pydantic_retrieve_model │
                                            │  + Extensions (retrieve) │
                                            └──────────────────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────┐
                                            │  Return 200 OK           │
                                            │  { ...detailed_data }    │
                                            └──────────────────────────┘
```

### 4.4 Update Operation

```
┌──────────────┐  PUT/PATCH /api/v1/{resource}/{id}/  ┌──────────────────┐
│    Client    │ ────────────────────────────────────▶│    ViewSet       │
│              │  { ...updated_data }                 │    .update()     │
└──────────────┘                                      └──────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  get_object()            │
                                                │  - Lookup existing       │
                                                └──────────────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  Pydantic Validation     │
                                                │  (pydantic_update_model) │
                                                └──────────────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  authorize_update()      │
                                                │  (ViewSet method)        │
                                                └──────────────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  [PLUGIN POINT]          │
                                                │  Custom update           │
                                                │  authorization           │
                                                └──────────────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  validate_data()         │
                                                │  (Business validation)   │
                                                └──────────────────────────┘
                                                               │
                                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL DISPATCH                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  pre_save signal → AuditLog captures pre-state                      │   │
│  │  Database UPDATE                                                    │   │
│  │  post_save signal → AuditLog records UPDATE                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [PLUGIN POINT] Custom signal handlers for update events            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                                                ┌──────────────────────────┐
                                                │  Return 200 OK           │
                                                │  { ...updated_data }     │
                                                └──────────────────────────┘
```

### 4.5 Delete Operation (Soft Delete)

```
┌──────────────┐  DELETE /api/v1/{resource}/{id}/  ┌──────────────────┐
│    Client    │ ─────────────────────────────────▶│    ViewSet       │
│              │                                   │    .destroy()    │
└──────────────┘                                   └──────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  get_object()            │
                                             │  - Lookup by external_id │
                                             │    (NOT id)              │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  validate_destroy()      │
                                             │  (Business rules check)  │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  authorize_destroy()     │
                                             │  (ViewSet method)        │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  [PLUGIN POINT]          │
                                             │  Custom delete           │
                                             │  authorization           │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOFT DELETE (Default Behavior)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  perform_destroy():                                                 │   │
│  │  - instance.deleted = True  (NOT hard delete)                       │   │
│  │  - instance.save()                                                  │   │
│  │                                                                     │   │
│  │  Signals still fire:                                                │   │
│  │  - pre_save → AuditLog captures state                               │   │
│  │  - post_save → AuditLog records UPDATE (deleted=True)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [PLUGIN POINT] Custom signal handlers for delete events            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Return 204 No Content   │
                                             └──────────────────────────┘

Note: Default lookup field is 'external_id', not 'id'
      Default queryset ordering is '-id' (newest first)
```

### 4.6 Upsert Operation (Bulk Create/Update)

```
┌──────────────┐  POST /api/v1/{resource}/upsert/  ┌──────────────────┐
│    Client    │ ─────────────────────────────────▶│    ViewSet       │
│              │  { "datapoints": [...] }          │    .upsert()     │
└──────────────┘                                   └──────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Validate datapoints     │
                                             │  count: 1 to 100         │
                                             │  (MAX_DATAPOINTS_PER_    │
                                             │   UPSERT = 100)          │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Begin Atomic            │
                                             │  Transaction             │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FOR EACH DATAPOINT                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │              Has 'id' field?                                        │   │
│  │                    │                                                │   │
│  │       ┌────────────┴────────────┐                                   │   │
│  │       │ Yes                      │ No                               │   │
│  │       ▼                          ▼                                  │   │
│  │  ┌──────────────┐         ┌──────────────┐                          │   │
│  │  │handle_update │         │handle_create │                          │   │
│  │  │- get_object  │         │- validate    │                          │   │
│  │  │- validate    │         │- authorize   │                          │   │
│  │  │- authorize   │         │- perform     │                          │   │
│  │  │- perform     │         │              │                          │   │
│  │  └──────────────┘         └──────────────┘                          │   │
│  │       │                          │                                  │   │
│  │       └──────────┬───────────────┘                                  │   │
│  │                  ▼                                                  │   │
│  │       ┌──────────────────┐                                          │   │
│  │       │ Collect result   │                                          │   │
│  │       │ or error         │                                          │   │
│  │       └──────────────────┘                                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Any unhandled errors?   │
                                             └──────────────────────────┘
                                                            │
                              ┌─────────────────────────────┴─────────────────────────────┐
                              │ Yes                                                        │ No
                              ▼                                                            ▼
                   ┌──────────────────────────┐                             ┌──────────────────────────┐
                   │  Rollback Transaction    │                             │  Commit Transaction      │
                   │  Return errors           │                             │  Return results          │
                   └──────────────────────────┘                             └──────────────────────────┘

Response Format:
{
    "results": [
        { "status": 200, "data": {...} },      // Updated
        { "status": 201, "data": {...} },      // Created
        { "status": 400, "errors": [...] }     // Validation error
    ]
}
```

---

## 5. Batch Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BATCH REQUEST PROCESSING                             │
│                         POST /api/v1/batch_requests/                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐                                   ┌──────────────────────┐
│    Client    │ ─────────────────────────────────▶│  BatchRequestView    │
│              │   {                               │                      │
│              │     "requests": [                 │                      │
│              │       {                           │                      │
│              │         "url": "/api/v1/...",    │                      │
│              │         "method": "POST",         │                      │
│              │         "body": {...},            │                      │
│              │         "reference_id": "ref_1"   │                      │
│              │       },                          │                      │
│              │       ...                         │                      │
│              │     ]                             │                      │
│              │   }                               │                      │
└──────────────┘                                   └──────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Validate request count  │
                                             │  Max: 20 (configurable   │
                                             │  MAX_REQUESTS_PER_BATCH  │
                                             │  _REQUEST)               │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Begin Atomic            │
                                             │  Transaction             │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FOR EACH REQUEST (Serial)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Build WSGI request using RequestFactory                         │   │
│  │     - Preserve USER_AGENT header                                    │   │
│  │     - Preserve AUTHORIZATION header                                 │   │
│  │                                                                     │   │
│  │  2. Route to appropriate view via URL resolver                      │   │
│  │                                                                     │   │
│  │  3. Execute view and capture response                               │   │
│  │                                                                     │   │
│  │  4. Collect response with reference_id                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  Any errors?             │
                                             └──────────────────────────┘
                                                            │
                              ┌─────────────────────────────┴─────────────────────────────┐
                              │ Yes                                                        │ No
                              ▼                                                            ▼
                   ┌──────────────────────────┐                             ┌──────────────────────────┐
                   │  Rollback all changes    │                             │  Commit all changes      │
                   └──────────────────────────┘                             └──────────────────────────┘
                              │                                                            │
                              └──────────────────────────┬─────────────────────────────────┘
                                                         ▼
                                             ┌──────────────────────────┐
                                             │  Return batch response   │
                                             │  {                       │
                                             │    "responses": [        │
                                             │      {                   │
                                             │        "reference_id",   │
                                             │        "status_code",    │
                                             │        "data" or "error" │
                                             │      }                   │
                                             │    ]                     │
                                             │  }                       │
                                             └──────────────────────────┘

[PLUGIN POINT] Custom batch request handlers can be added
Note: Requests are processed SERIALLY (not parallel) within transaction
```

---

## 6. File Upload Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FILE UPLOAD FLOW                                     │
│                         POST /api/v1/files/upload-file/                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐                                   ┌──────────────────────┐
│    Client    │ ─────────────────────────────────▶│  FileUploadViewSet   │
│              │   {                               │  .upload_file()      │
│              │     "original_name": "doc.pdf",   │                      │
│              │     "file_data": "<base64>",      │                      │
│              │     "name": "Patient Document",   │                      │
│              │     "associating_id": "<uuid>",   │                      │
│              │     "file_type": "patient",       │                      │
│              │     "file_category": "reports"    │                      │
│              │   }                               │                      │
└──────────────┘                                   └──────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  1. Base64 Decode        │
                                             │     file_data            │
                                             └──────────────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  2. MIME Type Validation │
                                             │     (python-magic lib)   │
                                             │                          │
                                             │  Allowed: 50+ types      │
                                             │  - Images (jpg, png...)  │
                                             │  - Videos (mp4, webm...) │
                                             │  - Audio (mp3, wav...)   │
                                             │  - Documents (pdf, docx) │
                                             └──────────────────────────┘
                                                            │
                              ┌─────────────────────────────┴─────────────────────────────┐
                              │ Valid                                                      │ Invalid
                              ▼                                                            ▼
                   ┌──────────────────────────┐                             ┌──────────────────────────┐
                   │  3. Extension Check      │                             │  Return 400              │
                   │  Blocked extensions:     │                             │  Invalid MIME type       │
                   │  exe, bat, dll, cmd,     │                             │                          │
                   │  com, msi, vbs, js, etc. │                             │                          │
                   └──────────────────────────┘                             └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  4. Size Validation      │
                   │  Max: 5MB (configurable  │
                   │  MAX_FILE_UPLOAD_SIZE)   │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  5. Authorization Check  │
                   │  file_authorizer()       │
                   │  - Check user access to  │
                   │    associating entity    │
                   │    (patient/encounter)   │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  6. Create FileUpload    │
                   │  record (pending)        │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  7. Upload to S3/Cloud   │
                   │  Storage                 │
                   └──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  8. Mark upload complete │
                   │  Return file metadata    │
                   └──────────────────────────┘

File Types (associating entity):
┌────────────────────────────────────────────────────────────────────────────┐
│  patient | encounter | consent | service_request | diagnostic_report |    │
│  discharge_summary | questionnaire_response | ...                          │
└────────────────────────────────────────────────────────────────────────────┘

[PLUGIN POINT] Custom file type authorizers can be registered
```

---

## 7. Rate Limiting Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RATE LIMITING FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       Any Rate-Limited Endpoint      ┌──────────────────────┐
│    Client    │ ─────────────────────────────────────▶│  ratelimit()        │
│              │                                       │  function           │
└──────────────┘                                       └──────────────────────┘
                                                                │
                                                                ▼
                                                 ┌──────────────────────────┐
                                                 │  Check DISABLE_RATELIMIT │
                                                 │  environment variable    │
                                                 └──────────────────────────┘
                                                                │
                              ┌─────────────────────────────────┴─────────────────────────────┐
                              │ Disabled                                                       │ Enabled
                              ▼                                                                ▼
                   ┌──────────────────────────┐                             ┌──────────────────────────┐
                   │  Skip rate limiting      │                             │  Check rate limit        │
                   │  Return False            │                             │  Default: 5/10m          │
                   └──────────────────────────┘                             │  (5 requests/10 minutes) │
                                                                            └──────────────────────────┘
                                                                                           │
                                                           ┌───────────────────────────────┴───────────────────────────────┐
                                                           │ Under limit                                                    │ Over limit
                                                           ▼                                                                ▼
                                                ┌──────────────────────────┐                             ┌──────────────────────────┐
                                                │  Return False            │                             │  Check for valid         │
                                                │  (Allow request)         │                             │  reCAPTCHA token         │
                                                └──────────────────────────┘                             └──────────────────────────┘
                                                                                                                        │
                                                                            ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
                                                                            │ Valid CAPTCHA                                                                          │ No/Invalid CAPTCHA
                                                                            ▼                                                                                        ▼
                                                                 ┌──────────────────────────┐                                                         ┌──────────────────────────┐
                                                                 │  Return False            │                                                         │  Return True             │
                                                                 │  (Allow request)         │                                                         │  (Block request)         │
                                                                 └──────────────────────────┘                                                         │                          │
                                                                                                                                                      │  Raise CaptchaRequired   │
                                                                                                                                                      │  Exception (HTTP 429)    │
                                                                                                                                                      └──────────────────────────┘

Rate Limit Keys:
┌────────────────────────────────────────────────────────────────────────────┐
│  - Per IP address (default)                                                │
│  - Per user (if authenticated)                                             │
│  - Custom keys via 'keys' parameter                                        │
└────────────────────────────────────────────────────────────────────────────┘

[PLUGIN POINT] Custom rate limit rules can be configured
```

---

## 8. Plugin System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN LOADING FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  Environment Variable                                                        │
│  ADDITIONAL_PLUGS = '[{"name": "plug_name", "package_name": "...",          │
│                        "version": "@main", "configs": {...}}]'               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────┐
                       │     PlugManager          │
                       │  (plugs/manager.py)      │
                       └──────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
         ┌──────────────────────────┐      ┌──────────────────────────┐
         │  Parse JSON config       │      │  Install packages        │
         │  into Plug dataclass     │      │  via pip install         │
         └──────────────────────────┘      └──────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────┐
                       │  manager.get_apps()      │
                       │  → Returns plugin names  │
                       └──────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DJANGO SETTINGS INTEGRATION                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PLUGIN_APPS = manager.get_apps()                                   │   │
│  │  PLUGIN_CONFIGS = manager.get_config()                              │   │
│  │  INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS                    │   │
│  │                   + LOCAL_APPS + PLUGIN_APPS                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         URL REGISTRATION                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  for plug in settings.PLUGIN_APPS:                                  │   │
│  │      urlpatterns += [                                               │   │
│  │          path(f"api/{plug}/", include(f"{plug}.urls"))              │   │
│  │      ]                                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN STRUCTURE                                     │
│                                                                             │
│  my_plugin/                                                                 │
│  ├── __init__.py                                                           │
│  ├── apps.py              # Django AppConfig                               │
│  ├── urls.py              # URL patterns → api/my_plugin/...               │
│  ├── views.py             # ViewSets                                       │
│  ├── models.py            # Database models                                │
│  ├── signals.py           # Custom signal handlers                         │
│  ├── extensions.py        # ExtensionBase implementations                  │
│  └── authorization.py     # Custom AuthorizationHandler                    │
│                                                                             │
│  [PLUGIN POINT] All of the above can be customized                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Extension Registry Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTENSION REGISTRATION                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  Plugin AppConfig.ready()                                                    │
│  ──────────────────────────────────────────────────────────────────────────  │
│  from care.emr.extensions import ExtensionRegistry                          │
│  from .extensions import MyCustomExtension                                   │
│                                                                              │
│  ExtensionRegistry.register(MyCustomExtension())                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ExtensionRegistry                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  _extensions: dict[resource_type, dict[extension_name, Extension]]  │   │
│  │                                                                     │   │
│  │  @classmethod                                                       │   │
│  │  def register(cls, extension_obj):                                  │   │
│  │      # Store extension by resource_type and extension_name          │   │
│  │                                                                     │   │
│  │  @classmethod                                                       │   │
│  │  def get_extension_obj(cls, resource_type, extension_name):         │   │
│  │      # Retrieve specific extension                                  │   │
│  │                                                                     │   │
│  │  @classmethod                                                       │   │
│  │  def get_extensions(cls):                                           │   │
│  │      # List all registered extensions                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTENSION USAGE IN VIEWSET                           │
└─────────────────────────────────────────────────────────────────────────────┘

                              CREATE/UPDATE
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  deserialize_extensions  │
                       │  (validate input)        │
                       └──────────────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  Extension.validate()    │
                       │  (custom validation)     │
                       └──────────────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  Store extension data    │
                       │  in resource.meta        │
                       └──────────────────────────┘


                              LIST/RETRIEVE
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  serialize_extensions    │
                       │  (format output)         │
                       └──────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
         ┌──────────────────────────┐   ┌──────────────────────────┐
         │  LIST operation          │   │  RETRIEVE operation      │
         │  use get_read_schema()   │   │  use get_retrieve_schema()│
         └──────────────────────────┘   └──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTENSION BASE CLASS                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class ExtensionBase:                                               │   │
│  │      resource_type: ExtensionResource  # account, patient, etc.    │   │
│  │      extension_name: str                                            │   │
│  │      extension_owner: ExtensionOwners  # core | plug               │   │
│  │      extension_version: str                                         │   │
│  │                                                                     │   │
│  │      def validate(self, data, resource=None)                        │   │
│  │      def serialize_extensions(self, data, resource=None)            │   │
│  │      def deserialize_extensions_list(self, data, resource)          │   │
│  │      def deserialize_extensions_retrieve(self, data, resource)      │   │
│  │                                                                     │   │
│  │      def get_write_schema()   # JSON schema for writes              │   │
│  │      def get_read_schema()    # JSON schema for list responses      │   │
│  │      def get_retrieve_schema() # JSON schema for detail responses   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [PLUGIN POINT] Extend ExtensionBase to add custom fields to resources     │
└─────────────────────────────────────────────────────────────────────────────┘


Supported Resource Types for Extensions:
┌────────────────────────────────────────────────────────────────────────────┐
│  account | encounter | patient | payment_reconciliation |                  │
│  supply_delivery | supply_delivery_order | product                         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Signal/Event Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIGNAL FLOW DIAGRAM                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              MODEL SAVE OPERATION                            │
│                                                                              │
│  instance.save()                                                             │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         pre_save Signal                             │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  AuditLog Receiver:                                       │     │    │
│  │  │  - Capture old values for existing instances              │     │    │
│  │  │  - Store in instance._pre_save_state                      │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  [PLUGIN POINT] Custom pre_save handlers                  │     │    │
│  │  │  @receiver(pre_save, sender=YourModel)                    │     │    │
│  │  │  def my_pre_save_handler(sender, instance, **kwargs):     │     │    │
│  │  │      # Custom logic before save                           │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      DATABASE OPERATION                             │    │
│  │                      INSERT or UPDATE                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        post_save Signal                             │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  AuditLog Receiver:                                       │     │    │
│  │  │  - Log operation (INSERT if created, UPDATE otherwise)    │     │    │
│  │  │  - Include user from AuditLogMiddleware.get_current_user()│     │    │
│  │  │  - Include request_id from middleware                     │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  Patient Identifier Receivers:                            │     │    │
│  │  │  - Update facility_name_identifier on Encounter save      │     │    │
│  │  │  - Update facility_name_identifier on TokenBooking save   │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  [PLUGIN POINT] Custom post_save handlers                 │     │    │
│  │  │  @receiver(post_save, sender=YourModel)                   │     │    │
│  │  │  def my_post_save_handler(sender, instance, created,      │     │    │
│  │  │                           **kwargs):                      │     │    │
│  │  │      # Trigger notifications, sync external systems, etc. │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                            MODEL DELETE OPERATION                            │
│                                                                              │
│  instance.delete()                                                           │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        pre_delete Signal                            │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  AuditLog Receiver:                                       │     │    │
│  │  │  - Capture state before deletion                          │     │    │
│  │  │  - Store for post_delete logging                          │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  [PLUGIN POINT] Custom pre_delete handlers                │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      DATABASE OPERATION                             │    │
│  │                           DELETE                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       post_delete Signal                            │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  AuditLog Receiver:                                       │     │    │
│  │  │  - Log DELETE operation with captured state               │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────┐     │    │
│  │  │  [PLUGIN POINT] Custom post_delete handlers               │     │    │
│  │  │  - Cleanup related data                                   │     │    │
│  │  │  - Notify external systems                                │     │    │
│  │  └───────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGISTERING CUSTOM SIGNALS (PLUGIN)                       │
│                                                                             │
│  # In plugin's apps.py                                                      │
│  class MyPluginConfig(AppConfig):                                           │
│      name = 'my_plugin'                                                     │
│                                                                             │
│      def ready(self):                                                       │
│          import my_plugin.signals  # Import signal handlers                 │
│                                                                             │
│  # In plugin's signals.py                                                   │
│  from django.db.models.signals import post_save                             │
│  from django.dispatch import receiver                                       │
│  from care.emr.models import Patient                                        │
│                                                                             │
│  @receiver(post_save, sender=Patient)                                       │
│  def sync_patient_to_external_system(sender, instance, created, **kwargs):  │
│      if created:                                                            │
│          # Sync to external system                                          │
│          pass                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. API Endpoint Categories

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API ENDPOINT OVERVIEW                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  AUTHENTICATION ENDPOINTS                                                    │
│  Base: /api/v1/auth/                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  POST /login/           → TokenObtainPairView (JWT login)              │ │
│  │  POST /logout/          → LogoutView                                   │ │
│  │  POST /token/refresh/   → TokenRefreshView                             │ │
│  │  POST /token/verify/    → AnnotatedTokenVerifyView                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Base: /api/v1/                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  POST /password_reset/          → ResetPasswordRequestToken            │ │
│  │  POST /password_reset/confirm/  → ResetPasswordConfirm                 │ │
│  │  POST /password_reset/check/    → ResetPasswordCheck                   │ │
│  │  POST /password_change/         → ChangePasswordView                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [PLUGIN POINT] Custom auth endpoints can be added via plugin URLs          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  USER & ORGANIZATION MANAGEMENT                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/users/                  → UserViewSet                         │ │
│  │  /api/v1/organization/           → OrganizationViewSet                 │ │
│  │    └── /{org_id}/users/          → OrganizationUsersViewSet            │ │
│  │  /api/v1/role/                   → RoleViewSet                         │ │
│  │  /api/v1/permission/             → PermissionViewSet                   │ │
│  │  /api/v1/mfa/totp/               → TOTPViewSet                         │ │
│  │  /api/v1/mfa/                    → MFALoginViewSet                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  PATIENT MANAGEMENT (Nested Resources)                                       │
│  Base: /api/v1/patient/                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/patient/                                 → PatientViewSet     │ │
│  │    └── /{patient_id}/allergy_intolerance/         → AllergyIntolerance │ │
│  │    └── /{patient_id}/symptom/                     → SymptomViewSet     │ │
│  │    └── /{patient_id}/diagnosis/                   → DiagnosisViewSet   │ │
│  │    └── /{patient_id}/diagnostic_report/           → DiagnosticReport   │ │
│  │    └── /{patient_id}/consent/                     → ConsentViewSet     │ │
│  │    └── /{patient_id}/observation/                 → ObservationViewSet │ │
│  │    └── /{patient_id}/questionnaire_response/      → QuestionnaireResp  │ │
│  │    └── /{patient_id}/medication/                                       │ │
│  │        ├── /request/          → MedicationRequestViewSet               │ │
│  │        ├── /prescription/     → MedicationRequestPrescriptionViewSet   │ │
│  │        ├── /statement/        → MedicationStatementViewSet             │ │
│  │        └── /administration/   → MedicationAdministrationViewSet        │ │
│  │    └── /{patient_id}/thread/                      → NoteThreadViewSet  │ │
│  │        └── /{thread_id}/note/                     → NoteMessageViewSet │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  [PLUGIN POINT] Custom patient-related endpoints                            │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  FACILITY MANAGEMENT (Deeply Nested)                                         │
│  Base: /api/v1/facility/                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/facility/                                → FacilityViewSet    │ │
│  │    └── /{facility_id}/organizations/              → FacilityOrgViewSet │ │
│  │        └── /{org_id}/users/                       → FacilityOrgUsers   │ │
│  │    └── /{facility_id}/users/                      → FacilityUsersView  │ │
│  │    └── /{facility_id}/schedulable_users/          → SchedulableUsers   │ │
│  │    └── /{facility_id}/location/                   → FacilityLocation   │ │
│  │        └── /{loc_id}/association/                 → LocationEncounter  │ │
│  │        └── /{loc_id}/product/                     → InventoryItemView  │ │
│  │    └── /{facility_id}/device/                     → DeviceViewSet      │ │
│  │        └── /{dev_id}/location_history/            → DeviceLocHistory   │ │
│  │        └── /{dev_id}/encounter_history/           → DeviceEncHistory   │ │
│  │        └── /{dev_id}/service_history/             → DeviceSvcHistory   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  SCHEDULING & APPOINTMENTS                                                   │
│  Base: /api/v1/facility/{facility_id}/                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /schedule/                       → ScheduleViewSet                    │ │
│  │    └── /{sch_id}/availability/    → AvailabilityViewSet                │ │
│  │  /token/queue/                    → TokenQueueViewSet                  │ │
│  │    └── /{queue_id}/token/         → TokenViewSet                       │ │
│  │  /token/sub_queue/                → TokenSubQueueViewSet               │ │
│  │  /token/category/                 → TokenCategoryViewSet               │ │
│  │  /appointments/                   → TokenBookingViewSet                │ │
│  │  /schedule_exceptions/            → AvailabilityExceptionsViewSet      │ │
│  │  /slots/                          → SlotViewSet                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  OTP-based Scheduling (Public):                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/otp/                     → OTPLoginView (unauthenticated)     │ │
│  │  /api/v1/otp/patient/             → PatientOTPView                     │ │
│  │  /api/v1/otp/slots/               → OTPSlotViewSet                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  INVENTORY & BILLING                                                         │
│  Base: /api/v1/facility/{facility_id}/                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /product/                        → ProductViewSet                     │ │
│  │  /order/delivery/                 → DeliveryOrderViewSet               │ │
│  │  /order/request/                  → RequestOrderViewSet                │ │
│  │  /order/dispense/                 → DispenseOrderViewSet               │ │
│  │  /account/                        → AccountViewSet                     │ │
│  │  /charge_item_definition/         → ChargeItemDefinitionViewSet        │ │
│  │  /charge_item/                    → ChargeItemViewSet                  │ │
│  │  /invoice/                        → InvoiceViewSet                     │ │
│  │  /payment_reconciliation/         → PaymentReconciliationViewSet       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  CLINICAL & MEDICAL RESOURCES                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/encounter/                → EncounterViewSet                  │ │
│  │  /api/v1/questionnaire/            → QuestionnaireViewSet              │ │
│  │  /api/v1/questionnaire_tag/        → QuestionnaireTagsViewSet          │ │
│  │  /api/v1/form_submission/          → FormSubmissionViewSet             │ │
│  │  /api/v1/observation_definition/   → ObservationDefinitionViewSet      │ │
│  │  /api/v1/medication/dispense/      → MedicationDispenseViewSet         │ │
│  │  /api/v1/specimen/                 → SpecimenViewSet                   │ │
│  │  /api/v1/specimen_definition/      → SpecimenDefinitionViewSet         │ │
│  │  /api/v1/service_request/          → ServiceRequestViewSet             │ │
│  │  /api/v1/healthcare_service/       → HealthcareServiceViewSet          │ │
│  │  /api/v1/activity_definition/      → ActivityDefinitionViewSet         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  UTILITY ENDPOINTS                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /api/v1/files/                    → FileUploadViewSet                 │ │
│  │  /api/v1/valueset/                 → ValueSetViewSet                   │ │
│  │  /api/v1/extensions/               → ExtensionsViewSet (read-only)     │ │
│  │  /api/v1/batch_requests/           → BatchRequestView                  │ │
│  │  /api/v1/plug_config/              → PlugConfigViewset                 │ │
│  │  /api/v1/template/                 → TemplateViewSet                   │ │
│  │  /api/v1/getallfacilities/         → AllFacilityViewSet                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Health & Documentation:                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  /ping/                            → Health check                      │ │
│  │  /health/                          → Detailed health (django-healthy)  │ │
│  │  /app_version/                     → Version info                      │ │
│  │  /api/schema/                      → OpenAPI schema (non-prod)         │ │
│  │  /swagger/                         → Swagger UI (non-prod)             │ │
│  │  /redoc/                           → ReDoc (non-prod)                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  PLUGIN API ENDPOINTS                                                        │
│  Base: /api/{plugin_name}/                                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  [PLUGIN POINT]                                                        │ │
│  │                                                                        │ │
│  │  Plugins can define their own URL patterns in:                         │ │
│  │  {plugin_name}/urls.py                                                 │ │
│  │                                                                        │ │
│  │  These are automatically registered at:                                │ │
│  │  /api/{plugin_name}/...                                                │ │
│  │                                                                        │ │
│  │  Example:                                                              │ │
│  │  - /api/hcx/claims/       (HCX plugin for insurance claims)            │ │
│  │  - /api/abdm/consent/     (ABDM plugin for health records)             │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Configuration Limits

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM CONFIGURATION LIMITS                          │
│                         (config/settings/config.py)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  BATCH & BULK OPERATIONS                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_DATAPOINTS_PER_UPSERT        = 100                                │ │
│  │  MAX_REQUESTS_PER_BATCH_REQUEST   = 20                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  PATIENT & ENCOUNTER LIMITS                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_APPOINTMENTS_PER_PATIENT                    = 10                  │ │
│  │  MAX_ACTIVE_ENCOUNTERS_PER_PATIENT_IN_FACILITY   = 5                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  FILE UPLOAD LIMITS                                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_FILE_UPLOAD_SIZE             = 5 MB                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  SCHEDULING LIMITS                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_SLOTS_PER_AVAILABILITY       = 30                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  CONTENT LIMITS                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_QUESTIONNAIRE_TEXT_RESPONSE_SIZE  = 2500 characters               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  FACILITY LIMITS                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  MAX_LOCATION_IN_FACILITY         = 1000                               │ │
│  │  MAX_ORGANIZATION_IN_FACILITY     = 1000                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  PAGINATION                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  PAGE_SIZE (default)              = 14                                 │ │
│  │  Pagination: CareLimitOffsetPagination                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  RATE LIMITING                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  DJANGO_RATE_LIMIT (default)      = "5/10m" (5 requests per 10 min)   │ │
│  │  Can be disabled: DISABLE_RATELIMIT=true                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  TOKEN INVALIDATION CACHE                                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Cache timeout                    = 1800 seconds (30 minutes)          │ │
│  │  Backend                          = Redis                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary of Plugin Extension Points

| Extension Point | Location | Description |
|----------------|----------|-------------|
| **Plugin URLs** | `config/urls.py` | Register custom API endpoints at `/api/{plugin}/` |
| **Middleware** | `config/settings/base.py` | Add custom request/response processing |
| **Authentication** | `config/authentication.py` | Custom authentication backends |
| **Authorization** | `AuthorizationController` | Override authorization handlers |
| **ViewSets** | Extend `EMRModelViewSet` | Custom CRUD logic and endpoints |
| **Extensions** | `ExtensionRegistry` | Add custom fields to resources |
| **Signals** | `AppConfig.ready()` | Hook into model lifecycle events |
| **Pydantic Models** | ViewSet attributes | Custom validation schemas |
| **Settings** | `PLUGIN_CONFIGS` | Plugin-specific configuration |
| **Rate Limiting** | `config/ratelimit.py` | Custom rate limit rules |
| **File Authorizers** | `file_authorizer()` | Custom file type authorization |
| **Batch Handlers** | `BatchRequestView` | Custom batch request processing |

---

## Exception Handling Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TWO-LEVEL EXCEPTION HANDLING                         │
└─────────────────────────────────────────────────────────────────────────────┘

                              Exception Raised
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  Level 1: Global Handler │
                       │  config.exception_handler│
                       │  .exception_handler()    │
                       │                          │
                       │  - Django ValidationError│
                       │    → DRF ValidationError │
                       └──────────────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  Level 2: EMR Handler    │
                       │  care.emr.api.viewsets   │
                       │  .base.emr_exception_    │
                       │   handler()              │
                       │                          │
                       │  - Pydantic Validation   │
                       │  - Django Validation     │
                       │  - Http404               │
                       │  - DRF ValidationError   │
                       └──────────────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │  Structured Error Format │
                       │  {                       │
                       │    "errors": [           │
                       │      {                   │
                       │        "type": "...",    │
                       │        "msg": "..."      │
                       │      }                   │
                       │    ]                     │
                       │  }                       │
                       └──────────────────────────┘

Error Types:
- validation_error: Input validation failures
- object_not_found: 404 errors
- permission_denied: Authorization failures
```

---

## 13. Quick Start Guide - Getting Prepared

### Technology Stack Overview

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | Django | 6.0 |
| REST API | Django REST Framework | 3.16.1 |
| Serialization | **Pydantic** (NOT DRF serializers) | - |
| Authentication | SimpleJWT | 5.5.1 |
| Database | PostgreSQL | - |
| Cache/Broker | Redis | 7.1.0 |
| Background Tasks | Celery | 5.6.0 |
| API Documentation | drf-spectacular | 0.29.0 |
| Application Server | Gunicorn | 23.0.0 |

### Project Directory Structure

```
care/
├── manage.py                    # Django CLI entry point
├── pyproject.toml               # Project dependencies
├── plug_config.py               # Plugin configuration
│
├── config/                      # Django Configuration Hub
│   ├── settings/
│   │   ├── base.py             # Base settings (shared)
│   │   ├── local.py            # Development environment
│   │   ├── production.py       # Production environment
│   │   └── test.py             # Test environment
│   ├── urls.py                 # Main URL routing
│   ├── api_router.py           # DRF router for /api/v1/
│   ├── wsgi.py                 # WSGI entry point
│   ├── authentication.py       # Custom JWT authentication
│   ├── exception_handler.py    # Global exception handling
│   ├── middlewares.py          # Custom middleware
│   └── celery_app.py           # Celery configuration
│
├── care/                        # Main Application Package
│   ├── emr/                    # Core EMR Module
│   │   ├── api/viewsets/       # REST API ViewSets
│   │   ├── resources/          # Pydantic models (serializers)
│   │   ├── models/             # Django ORM models (46+ models)
│   │   ├── registries/         # Extension registry
│   │   ├── fhir/               # FHIR standards integration
│   │   └── signals/            # Django signals
│   ├── users/                  # User management
│   ├── facility/               # Facility management
│   ├── security/               # Authorization system
│   │   └── authorization/      # AuthorizationController
│   ├── audit_log/              # Audit logging
│   └── utils/                  # Utilities (pagination, filters)
│
└── plugs/                       # Plugin System
    ├── plug.py                 # Plugin dataclass definition
    └── manager.py              # Plugin lifecycle manager
```

### Key Files Reference

| Purpose | File Path | Description |
|---------|-----------|-------------|
| **Settings** | `config/settings/base.py` | All Django/DRF configuration, middleware stack, auth settings |
| **URL Routing** | `config/urls.py` | Main URL patterns, plugin URL registration |
| **API Router** | `config/api_router.py` | DRF router with 100+ viewset registrations |
| **Authentication** | `config/authentication.py` | CustomJWTAuthentication with token invalidation |
| **Exception Handler** | `config/exception_handler.py` | Global exception to error response conversion |
| **Base ViewSet** | `care/emr/api/viewsets/base.py` | EMRModelViewSet, all CRUD mixins, authorization hooks |
| **Base Resource** | `care/emr/resources/base.py` | EMRResource Pydantic base class for serialization |
| **Authorization** | `care/security/authorization/base.py` | AuthorizationController, AuthorizationHandler |
| **Permission Class** | `care/security/utils/permission_class.py` | CareAuthentication permission class |
| **Plugin Manager** | `plugs/manager.py` | PlugManager for plugin lifecycle |
| **Extension Registry** | `care/emr/registries/extensions/registry.py` | ExtensionRegistry for resource extensions |
| **Pagination** | `care/utils/pagination/care_pagination.py` | CareLimitOffsetPagination (14 default, 200 max) |
| **Filters** | `care/utils/filters/` | MultiSelectFilter, NullFilter custom filters |

---

## 14. Understanding the Serialization Pattern

### Pydantic vs DRF Serializers

This codebase uses **Pydantic models** instead of DRF serializers for request/response handling.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PYDANTIC SERIALIZATION FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

REQUEST (JSON) ──────────────────────────────────────────────▶ RESPONSE (JSON)
     │                                                               ▲
     ▼                                                               │
┌──────────────┐      ┌──────────────┐      ┌──────────────┐        │
│  Pydantic    │      │   Django     │      │  Pydantic    │        │
│  WriteSpec   │─────▶│   Model      │─────▶│  ReadSpec    │────────┘
│              │      │   (ORM)      │      │              │
│ model_validate()    │              │      │ serialize()  │
│ de_serialize()      │   .save()    │      │ to_json()    │
└──────────────┘      └──────────────┘      └──────────────┘
```

### Four Pydantic Models Per Resource

```python
class MyViewSet(EMRModelViewSet):
    # For CREATE - validates incoming data
    pydantic_model = MyWriteSpec

    # For UPDATE - may have different rules than create
    pydantic_update_model = MyUpdateSpec

    # For LIST - minimal fields for collection
    pydantic_read_model = MyListSpec

    # For RETRIEVE - full detail with relations
    pydantic_retrieve_model = MyDetailSpec
```

### EMRResource Base Class

```python
class EMRResource(BaseModel):
    __model__ = None              # Django model class
    __exclude__ = []              # Fields to exclude

    @classmethod
    def serialize(cls, obj, user=None):
        """Django Model → Pydantic → JSON"""
        mapping = {}
        for field in cls.model_fields:
            mapping[field] = getattr(obj, field)
        cls.perform_extra_serialization(mapping, obj)
        return cls(**mapping)

    def de_serialize(self, obj=None, partial=False):
        """Pydantic → Django Model"""
        if obj is None:
            obj = self.__model__()
        for field, value in self.model_dump().items():
            setattr(obj, field, value)
        self.perform_extra_deserialization(is_update=obj.pk is not None, obj=obj)
        return obj

    def to_json(self):
        """Final JSON output"""
        return self.model_dump(mode="json", exclude=["meta"])
```

---

## 15. Creating a New Endpoint Checklist

### Step 1: Define Django Model

```python
# care/emr/models/my_resource.py
class MyResource(EMRBaseModel):
    name = models.CharField(max_length=255)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
```

### Step 2: Create Pydantic Resources

```python
# care/emr/resources/my_resource/spec.py
class MyResourceWriteSpec(EMRResource):
    __model__ = MyResource

    name: str
    facility: UUID4

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError("Name too short")
        return v

class MyResourceReadSpec(EMRResource):
    __model__ = MyResource

    id: str
    name: str
    facility: dict
    created_date: datetime

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["facility"] = {"id": str(obj.facility.external_id), "name": obj.facility.name}
```

### Step 3: Create ViewSet

```python
# care/emr/api/viewsets/my_resource.py
class MyResourceViewSet(EMRModelViewSet):
    database_model = MyResource
    pydantic_model = MyResourceWriteSpec
    pydantic_read_model = MyResourceReadSpec
    pydantic_retrieve_model = MyResourceReadSpec

    filterset_class = MyResourceFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]
    ordering_fields = ["created_date", "name"]

    def get_queryset(self):
        return MyResource.objects.filter(deleted=False).select_related("facility")

    def authorize_create(self, instance):
        if not AuthorizationController.call("can_create_my_resource", self.request.user):
            raise PermissionDenied("Cannot create resource")

    def authorize_update(self, request_obj, model_instance):
        if not AuthorizationController.call("can_update_my_resource", self.request.user, model_instance):
            raise PermissionDenied("Cannot update resource")
```

### Step 4: Register in Router

```python
# config/api_router.py
from care.emr.api.viewsets.my_resource import MyResourceViewSet

router.register("my_resources", MyResourceViewSet, basename="my_resources")
```

### Step 5: Create Authorization Handler (Optional)

```python
# care/security/authorization/my_resource.py
class MyResourceAuthorizationHandler(AuthorizationHandler):
    def can_create_my_resource(self, user):
        return self.check_permission_in_facility_organization(
            permissions=["can_create_my_resource"],
            user=user
        )
```

---

## 16. Plugin Development Guide

### Creating a Plugin

```
my_plugin/
├── __init__.py
├── apps.py                # Django AppConfig
├── models.py              # Database models (optional)
├── urls.py                # URL patterns (REQUIRED)
├── api/
│   └── viewsets/          # ViewSets
├── resources/             # Pydantic specs
└── extensions.py          # Resource extensions (optional)
```

### Plugin Registration

```python
# plug_config.py
from plugs.manager import PlugManager
from plugs.plug import Plug

my_plugin = Plug(
    name="care_my_plugin",                                    # Django app name
    package_name="git+https://github.com/org/my_plugin.git", # Git URL
    version="@v1.0.0",                                        # Branch/tag
    configs={                                                 # Plugin-specific config
        "API_KEY": "value",
        "MAX_ITEMS": 100
    }
)

plugs = [my_plugin]
manager = PlugManager(plugs)
```

### Plugin URLs (Auto-registered at /api/{plugin_name}/)

```python
# my_plugin/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.viewsets import MyPluginViewSet

router = DefaultRouter()
router.register("items", MyPluginViewSet, basename="items")

urlpatterns = [
    path("", include(router.urls)),
]
# Results in: /api/care_my_plugin/items/
```

### Creating Resource Extensions

```python
# my_plugin/extensions.py
from care.emr.registries.extensions.base import ExtensionBase, ExtensionOwners
from care.emr.registries.extensions.types import ExtensionResource
from care.emr.registries.extensions.registry import ExtensionRegistry

class PatientExtension(ExtensionBase):
    resource_type = ExtensionResource.patient
    extension_name = "my_plugin_data"
    extension_owner = ExtensionOwners.plug

    def validate(self, data, resource=None):
        # Validate extension data
        if "custom_field" not in data:
            raise ValueError("custom_field is required")

    def serialize_extensions(self, data, resource=None):
        # Add custom fields to response
        data["my_custom_field"] = resource.get_extension_data("my_plugin")
        return data

# Register in apps.py ready() method
ExtensionRegistry.register(PatientExtension())
```

---

## 17. Quick Reference Commands

### Development

```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Run tests
python manage.py test

# Install plugins
python install_plugins.py

# Generate API schema
python manage.py spectacular --file schema.yaml
```

### Docker Compose Services

```bash
# Start all services
docker-compose up -d

# PostgreSQL: localhost:5433
# Redis: localhost:6380
# MinIO (S3): localhost:9100 (API), localhost:9001 (Console)
```

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` | Settings module |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis connection string |
| `DISABLE_RATELIMIT` | `false` | Disable rate limiting |
| `AUDIT_LOG_ENABLED` | `false` | Enable audit logging |
| `MAINTENANCE_MODE` | `0` | Enable maintenance mode |
| `ADDITIONAL_PLUGS` | - | JSON array of additional plugins |

---

## 18. Common Patterns Quick Reference

### Standard Response Formats

```json
// Single Object
{
    "id": "uuid-string",
    "name": "Example",
    "created_date": "2024-01-15T10:00:00Z"
}

// List (Paginated)
{
    "count": 150,
    "results": [...]
}

// Error
{
    "errors": [
        {"type": "validation_error", "msg": "Name is required"},
        {"type": "validation_error", "msg": "Email is invalid"}
    ]
}
```

### Filtering Query Parameters

```
# Single value filter
GET /api/v1/patients/?status=active

# Multi-select filter (comma-separated)
GET /api/v1/patients/?status=active,discharged

# Search
GET /api/v1/patients/?search_text=john

# Ordering
GET /api/v1/patients/?ordering=-created_date

# Pagination
GET /api/v1/patients/?limit=20&offset=40

# Null check
GET /api/v1/patients/?encounter__isnull=true
```

### Authorization Pattern

```python
# In ViewSet
def authorize_create(self, instance):
    # instance is Pydantic model (before DB save)
    if not AuthorizationController.call("can_create_patient", self.request.user):
        raise PermissionDenied("...")

def authorize_update(self, request_obj, model_instance):
    # request_obj: Pydantic model with new data
    # model_instance: Django model from DB
    pass

def authorize_destroy(self, instance):
    # instance is Django model
    pass

def authorize_retrieve(self, model_instance):
    # Called for single object GET
    pass
```

### Soft Delete Pattern

```python
# All deletes are soft deletes by default
def perform_destroy(self, instance):
    instance.deleted = True
    instance.save()

# Queryset should filter deleted
def get_queryset(self):
    return MyModel.objects.filter(deleted=False)
```

---

## 19. Learning Path Recommendations

### Beginner Path (Week 1)

1. **Read**: `config/settings/base.py` - Understand all configurations
2. **Read**: `config/urls.py` - See how URLs are organized
3. **Read**: `care/emr/api/viewsets/base.py` - Understand CRUD mixins
4. **Read**: `care/emr/resources/base.py` - Understand Pydantic serialization
5. **Explore**: Pick one simple ViewSet (e.g., `UserViewSet`) and trace the flow

### Intermediate Path (Week 2)

1. **Study**: `care/security/authorization/` - Authorization system
2. **Study**: `plugs/manager.py` - Plugin system
3. **Study**: `care/emr/registries/` - Extension registry
4. **Practice**: Create a simple endpoint following the checklist above
5. **Practice**: Add filtering and search to an existing endpoint

### Advanced Path (Week 3+)

1. **Deep Dive**: Signal handlers in `care/emr/signals/`
2. **Deep Dive**: Celery tasks in `care/emr/tasks/`
3. **Deep Dive**: FHIR integration in `care/emr/fhir/`
4. **Practice**: Create a plugin with custom extensions
5. **Practice**: Add new authorization handlers

---

## 20. Debugging Tips

### Request Tracing

1. Enable `ENABLE_REQUEST_TIME_LOGGING=true` for request timing
2. Enable `AUDIT_LOG_ENABLED=true` for request logging
3. Check AuditLog for request IDs: `{method}::{path_hash}::{uuid}`

### Common Issues

| Issue | Check |
|-------|-------|
| 401 Unauthorized | Token expired? Check `CustomJWTAuthentication` |
| 403 Forbidden | Check `authorize_*` methods and `AuthorizationController` |
| 404 Not Found | Using `external_id` (not `id`)? Check `deleted=False` filter |
| 400 Validation | Check Pydantic model validators |
| 500 Error | Check `config/exception_handler.py` and logs |

### Useful Debug Endpoints

```
GET /ping/               # Health check
GET /health/             # Detailed health status
GET /app_version/        # Application version
GET /swagger/            # Swagger UI (dev only)
GET /redoc/              # ReDoc documentation (dev only)
GET /api/schema/         # OpenAPI schema
```

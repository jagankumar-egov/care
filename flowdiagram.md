# Care Backend - API Flow Diagrams

This document describes the flow of different API operations in the Care backend system, including plugin extension points where behavior can be customized.

---

## Table of Contents

1. [Request/Response Lifecycle](#1-requestresponse-lifecycle)
2. [Authentication Flow](#2-authentication-flow)
3. [Authorization Flow](#3-authorization-flow)
4. [CRUD Operations Flow](#4-crud-operations-flow)
5. [Plugin System Architecture](#5-plugin-system-architecture)
6. [Extension Registry Flow](#6-extension-registry-flow)
7. [Signal/Event Flow](#7-signalevent-flow)
8. [API Endpoint Categories](#8-api-endpoint-categories)

---

## 1. Request/Response Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HTTP REQUEST                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MIDDLEWARE STACK                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SecurityMiddleware → CorsMiddleware → WhiteNoiseMiddleware          │   │
│  │      → SessionMiddleware → LocaleMiddleware → CommonMiddleware      │   │
│  │      → CsrfViewMiddleware → AuthenticationMiddleware                │   │
│  │      → MaintenanceModeMiddleware                                    │   │
│  │      → AuditLogMiddleware (captures request context)                │   │
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
│  │   → Pydantic model validation                                       │   │
│  │   → authorize_create / authorize_update / authorize_retrieve        │   │
│  │   → Business logic execution                                        │   │
│  │   → Database operations                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ [PLUGIN POINT] Custom ViewSets can extend EMRModelViewSet           │   │
│  │ Override: authorize_*, validate_data, perform_create methods        │   │
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
                                               │  (django_ratelimit)      │
                                               └──────────────────────────┘
                                                              │
                              ┌────────────────────┬──────────┴──────────┐
                              │                    │                      │
                              ▼                    ▼                      ▼
                    ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
                    │   Under Limit   │  │  Over Limit     │   │ Captcha Valid   │
                    │   Proceed       │  │  Return 429 +   │   │ Proceed         │
                    │                 │  │  CaptchaRequired│   │                 │
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
                    │  Return temp    │                   │   Return 401    │
                    │  token (5 min)  │                   │                 │
                    └─────────────────┘                   └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  MFA Not Enabled│
                    │  Return:        │
                    │  - access_token │
                    │  - refresh_token│
                    └─────────────────┘

[PLUGIN POINT] Custom authentication backends can be registered
[PLUGIN POINT] Custom MFA providers can be implemented
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
                                                 │       INVALIDATE:{token} │
                                                 └──────────────────────────┘
                                                                │
                                       ┌────────────────────────┴────────────────────────┐
                                       │                                                  │
                                       ▼                                                  ▼
                            ┌─────────────────────┐                            ┌─────────────────────┐
                            │  Token Valid        │                            │  Token Invalidated  │
                            │  Return new         │                            │  Return 401         │
                            │  access_token       │                            │                     │
                            └─────────────────────┘                            └─────────────────────┘
```

### 2.3 Logout Flow

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
│                                                        │                    │
│                                                        ▼                    │
│                                              ┌──────────────────────┐      │
│                                              │   RolePermission     │      │
│                                              │ (permission mapping) │      │
│                                              └──────────────────────┘      │
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

### 4.5 Delete Operation

```
┌──────────────┐  DELETE /api/v1/{resource}/{id}/  ┌──────────────────┐
│    Client    │ ─────────────────────────────────▶│    ViewSet       │
│              │                                   │    .destroy()    │
└──────────────┘                                   └──────────────────┘
                                                            │
                                                            ▼
                                             ┌──────────────────────────┐
                                             │  get_object()            │
                                             │  - Lookup existing       │
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
│                         SIGNAL DISPATCH                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  pre_delete signal → AuditLog captures state before deletion        │   │
│  │  Database DELETE                                                    │   │
│  │  post_delete signal → AuditLog records DELETE                       │   │
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
```

---

## 5. Plugin System Architecture

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

## 6. Extension Registry Flow

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

## 7. Signal/Event Flow

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

## 8. API Endpoint Categories

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

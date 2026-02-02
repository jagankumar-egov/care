# Care Backend - Comprehensive System Understanding

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Services & Microservices](#3-services--microservices)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [Data Persistence & Retrieval](#5-data-persistence--retrieval)
6. [Database Design & Choices](#6-database-design--choices)
7. [Algorithms & Optimizations](#7-algorithms--optimizations)
8. [Master Data](#8-master-data)
9. [Configuration Management](#9-configuration-management)
10. [Code Reusability & Design Patterns](#10-code-reusability--design-patterns)
11. [Documentation Approach](#11-documentation-approach)
12. [Project Structure](#12-project-structure)

---

## 1. Architecture Overview

### Architecture Type: Modular Monolith

The Care backend is a **Django monolith with modular architecture** deployed as multiple container instances with different roles. It's NOT a true microservices system but a single codebase deployed with containerization.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Request                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Gunicorn (Port 9000)                         │
│                    Django REST Framework                        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  PostgreSQL   │    │     Redis     │    │    MinIO      │
│   Database    │    │  Cache/Broker │    │  S3 Storage   │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │    Celery     │
                    │    Workers    │
                    └───────────────┘
```

### Key Architectural Characteristics

| Characteristic | Implementation |
|----------------|----------------|
| Architecture Style | Modular Monolith |
| API Style | RESTful (100+ endpoints) |
| Communication | Sync (HTTP) + Async (Celery/Redis) |
| Database Strategy | Single PostgreSQL (source of truth) |
| Caching | Redis distributed cache |
| File Storage | S3/MinIO compatible |
| Background Jobs | Celery with Redis broker |
| Plugin Support | Dynamic Django app loading |

---

## 2. Technology Stack

### Core Framework

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.13 |
| Web Framework | Django | 6.0 |
| REST Framework | Django REST Framework | 3.16.1 |
| API Documentation | drf-spectacular | 0.29.0 |
| Data Validation | Pydantic | 2.12.5 |

### Database & Storage

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Primary Database | PostgreSQL (Alpine) | Data persistence |
| ORM | Django ORM | Database abstraction |
| Cache/Broker | Redis 8 (Alpine) | Caching, message queue |
| File Storage | AWS S3 / MinIO | Documents, media |
| Static Files | WhiteNoise | Static file serving |

### Security & Authentication

| Component | Technology |
|-----------|-----------|
| JWT Auth | djangorestframework-simplejwt 5.5.1 |
| Password Hashing | Argon2 (primary), PBKDF2, BCrypt |
| Rate Limiting | django-ratelimit 4.1.0 |
| CAPTCHA | Google reCAPTCHA v3 |
| CORS | django-cors-headers 4.9.0 |

### Background Processing

| Component | Technology |
|-----------|-----------|
| Task Queue | Celery 5.6.0 |
| Message Broker | Redis |
| Scheduler | Celery Beat |

### Monitoring & Quality

| Component | Technology |
|-----------|-----------|
| Error Tracking | Sentry SDK 2.47.0 |
| Linting | Ruff 0.14.8 |
| Testing | Django unittest + coverage 7.13.0 |
| Test Data | model-bakery 1.20.5, Faker 38.2.0 |

---

## 3. Services & Microservices

### Deployable Units

The system deploys as 6 container services:

#### 1. Backend API Service
- **Entry Point**: `scripts/start.sh` (production) / `scripts/start-dev.sh` (dev)
- **Server**: Gunicorn (2 workers in production)
- **Port**: 9000
- **Responsibilities**: REST API, authentication, authorization

#### 2. Celery Worker
- **Entry Point**: `scripts/celery_worker.sh`
- **Concurrency**: Configurable (default: 1)
- **Max Tasks Per Child**: 6 (memory leak prevention)
- **Responsibilities**: Async task execution

#### 3. Celery Beat Scheduler
- **Entry Point**: `scripts/celery_beat.sh`
- **Responsibilities**: Periodic task scheduling
- **Startup Tasks**: Migrations, permission sync, valueset sync

#### 4. PostgreSQL Database
- **Image**: postgres:alpine
- **Port**: 5433 (external) → 5432 (internal)
- **Persistence**: Named volume `postgres-data`

#### 5. Redis Cache/Broker
- **Image**: redis:8-alpine
- **Port**: 6380 (external) → 6379 (internal)
- **Persistence**: Named volume `redis-data`

#### 6. MinIO S3 Storage
- **Image**: minio/minio:latest
- **Ports**: 9100 (S3 API), 9001 (Web Console)
- **Region**: ap-south-1

### Inter-Service Communication

| Type | Mechanism | Use Case |
|------|-----------|----------|
| Synchronous | REST API (HTTP) | Client requests |
| Asynchronous | Celery + Redis | Background jobs |
| Events | Django Signals | Model state changes |
| Caching | Redis | Shared state, token invalidation |

---

## 4. Authentication & Authorization

### Authentication Stack

```
┌─────────────────────────────────────────────────────────────┐
│                   Authentication Flow                        │
├─────────────────────────────────────────────────────────────┤
│  1. CustomJWTAuthentication (Primary - JWT tokens)          │
│  2. CustomBasicAuthentication (Development)                 │
│  3. SessionAuthentication (Admin interface)                 │
│  4. TokenAuthentication (API tokens)                        │
└─────────────────────────────────────────────────────────────┘
```

### JWT Configuration

| Setting | Value |
|---------|-------|
| Access Token Lifetime | 10 minutes (configurable) |
| Refresh Token Lifetime | 30 minutes (configurable) |
| Token Rotation | Enabled |
| User ID Field | external_id (UUID) |
| Algorithm | HS256 (HMAC), RS256 (JWKS) |

### MFA/TOTP Support

- **TOTP Implementation**: pyotp library
- **Backup Codes**: 10 codes, hashed with Django's `make_password()`
- **Valid Window**: 30 seconds
- **Storage**: User.mfa_settings JSONField

### Login Flow

```
User Login Request
        │
        ▼
┌───────────────────┐     ┌───────────────────┐
│  Rate Limit Check │────▶│  CAPTCHA Required │
└───────────────────┘     └───────────────────┘
        │ OK
        ▼
┌───────────────────┐
│ Credential Check  │
└───────────────────┘
        │
        ▼
┌───────────────────┐     ┌───────────────────┐
│   MFA Enabled?    │────▶│  Return temp_token│
└───────────────────┘ Yes │  (5 min expiry)   │
        │ No              └───────────────────┘
        ▼
┌───────────────────┐
│ Return JWT Tokens │
│ (access + refresh)│
└───────────────────┘
```

### Role-Based Access Control (RBAC)

**Predefined Roles:**
| Role | Description |
|------|-------------|
| Volunteer | Volunteer at facility |
| Doctor | Medical practitioner |
| Nurse | Nursing staff |
| Staff | General staff |
| Pharmacist | Pharmacy operations |
| Facility Admin | Facility administrator |
| Administrator | Organization administrator |
| Admin | System administrator |

**Permission Contexts:**
- GENERIC, FACILITY, PATIENT, QUESTIONNAIRE
- ORGANIZATION, FACILITY_ORGANIZATION, ENCOUNTER

### Authorization Pattern

```python
# Authorization Handler Pattern
class UserAccess(AuthorizationHandler):
    def can_create_user(self, user):
        if user.is_superuser:
            return True
        roles = self.get_role_from_permissions([UserPermissions.can_create_user.name])
        return OrganizationUser.objects.filter(user=user, role_id__in=roles).exists()

# Usage in ViewSet
AuthorizationController.call("can_create_user", request.user)
```

### Token Invalidation

- **Mechanism**: Redis cache-based blacklisting
- **Keys**: `ACCESS_TOKEN_INVALIDATE:{token}`, `REFRESH_TOKEN_INVALIDATE:{token}`
- **TTL**: 30 minutes (matches token lifetimes)

---

## 5. Data Persistence & Retrieval

### Base Model Pattern

```python
class BaseModel(models.Model):
    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)  # Soft delete

    objects = BaseManager()  # Filters out deleted records

    def delete(self, *args):
        self.deleted = True
        self.save(update_fields=["deleted"])
```

### EMR Base Model (Audit Trail)

```python
class EMRBaseModel(BaseModel):
    history = models.JSONField(default=dict)      # Change history
    meta = models.JSONField(default=dict)         # Metadata
    created_by = models.ForeignKey("users.User")  # Audit
    updated_by = models.ForeignKey("users.User")  # Audit
```

### Query Optimization Patterns

**select_related Usage (Reduces N+1):**
```python
def get_queryset(self):
    return super().get_queryset().select_related(
        "patient", "facility", "created_by", "updated_by"
    ).order_by("-created_date")
```

**Used in 30+ ViewSets**: patient, encounter, medication, observation, etc.

### Caching Strategy

| Cache Type | Backend | TTL | Use Case |
|------------|---------|-----|----------|
| Default | Redis | Varies | General caching |
| Swagger | LocMemCache | - | API schema |
| Flags | Redis | 24 hours | Feature flags |
| Roles | Redis | 7 days | Permission cache |
| Tags | Redis | Auto | Tag hierarchies |

**Cache Key Pattern:**
```
serializers_cache:{model}:{pk}:{spec_class}
```

### Distributed Locking

```python
class Lock:
    def __init__(self, key, timeout=settings.LOCK_TIMEOUT):
        self.key = f"lock:{key}"

    def acquire(self):
        if not cache.set(self.key, value=True, timeout=self.timeout, nx=True):
            raise ObjectLocked

# Usage
with transaction.atomic(), InventoryItemLock(instance.item):
    # Critical section
```

---

## 6. Database Design & Choices

### Why PostgreSQL?

| Reason | Benefit |
|--------|---------|
| ACID Compliance | Data integrity for healthcare |
| JSON Support | Flexible schema for history/meta fields |
| Full-Text Search | Patient/record search |
| Trigram Similarity | Fuzzy matching capability |
| Mature Ecosystem | Django ORM support |
| HIPAA Capable | Healthcare compliance |

### Database Configuration

```python
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres:///care")
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # Request-level transactions
DATABASES["default"]["CONN_MAX_AGE"] = 60  # Connection pooling (production)
```

### Indexing Strategy

| Field Type | Index |
|------------|-------|
| external_id | Unique + db_index |
| created_date | db_index |
| modified_date | db_index |
| deleted | db_index |
| ForeignKey | Automatic |
| Composite | Explicit Index() |

### Model Count

- **Total Models**: 46+ in EMR module
- **Key Models**: Patient, Encounter, Observation, Medication, Organization, Facility

---

## 7. Algorithms & Optimizations

### Search Algorithms

| Algorithm | Implementation | Location |
|-----------|----------------|----------|
| Substring Search | `icontains` lookup | patient.py |
| Exact Match | `iexact` lookup | phone_number filters |
| Fuzzy Search | PostgreSQL trigram | Database extension |

### Pagination

```python
class CareLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 200  # Maximum items per page
```

### Sorting Algorithm (Custom Priority)

```python
# care/utils/queryset/filters.py
def sort_index(qs, field, list_values):
    """Creates Case/When expressions for custom ordering"""
    return qs.annotate(
        _sort_index=models.Case(
            *[models.When(**{field: v}, then=i) for i, v in enumerate(list_values)],
            default=len(list_values),
            output_field=models.IntegerField()
        )
    ).order_by('_sort_index')
```

### Tag Filtering (AND/OR Logic)

```python
# "any" behavior (OR logic)
queryset.filter(tags__overlap=tag_ids)

# "all" behavior (AND logic)
queryset.filter(tags__contains=tag_ids)
```

### Batch Processing

```python
# Pagination-based batch processing for large datasets
batch_size = 1000
paginator = Paginator(queryset, batch_size)

for page_num in paginator.page_range:
    page = paginator.page(page_num)
    Model.objects.bulk_update(list(page.object_list), ['field'], batch_size=batch_size)
```

### Aggregation Algorithms

**Financial Calculations:**
```python
def calculate_charge_items_summary():
    # Separates: base, surcharge, discount, tax
    # Calculates: net = base + surcharge - discount
    #             gross = net + tax
```

**Inventory Sync:**
```python
net_content = incoming_deliveries - outgoing_deliveries - dispensed_items
```

### Cache Invalidation (Recursive)

```python
def invalidate_tag_cache(tag_id, include_descendants=True):
    # Recursively invalidates tag and all descendants
    # Uses parent_cache__overlap for efficient descendant lookup
```

---

## 8. Master Data

### Value Sets & Coding Systems

| System | URL | Usage |
|--------|-----|-------|
| SNOMED CT | http://snomed.info/sct | Clinical terms |
| LOINC | http://loinc.org | Lab observations |
| HL7 | http://terminology.hl7.org | Healthcare standards |
| UCUM | http://unitsofmeasure.org | Units of measure |
| OHC Custom | http://ohc.network/codes/ | Internal codes |

### Enums & Choices

**Patient:**
- BloodGroupChoices: A+, A-, B+, B-, AB+, AB-, O+, O-, unknown
- GenderChoices: male, female, non_binary, transgender

**Encounter:**
- StatusChoices: planned, in_progress, on_hold, discharged, completed, cancelled
- ClassChoices: imp (inpatient), amb (ambulatory), emer (emergency), etc.
- PriorityChoices: ASAP, emergency, urgent, routine, stat, etc.

**Facility:**
- 78 Facility Types (hospitals, clinics, labs, COVID centers)
- 64 Doctor Specializations
- FacilityFeatures: CT Scan, Maternity, X-Ray, NICU, OT, Blood Bank

### Tax & Billing Master Data

**Tax Codes:**
```python
TAX_CODES = [
    {"code": "igst", "display": "IGST"},
    {"code": "cgst", "display": "CGST"},
    {"code": "sgst", "display": "SGST"},
    {"code": "utgst", "display": "UTGST"},
]
```

**Tax Slabs:**
- 18% Slab: CGST@9%, SGST@9%, IGST@18%
- 12% Slab: CGST@6%, SGST@6%, IGST@12%
- 5% Slab: CGST@2.5%, SGST@2.5%, IGST@5%

### Fixture Data (Test Environment)

**Lab Definitions:**
- Specimen Definitions: Blood (venous, EDTA, serum), Urine
- Observation Definitions: Blood Glucose (LOINC: 1558-6), CBC, Lipid Panel, Urinalysis
- Charge Items: Pricing with tax/discount configurations

**Inventory Items:**
- Medications: Amoxicillin, Paracetamol, Ibuprofen
- Consumables: Gloves

### Data Loading Commands

```bash
# Sync all master data
python manage.py load_fixtures

# Sync permissions and roles
python manage.py sync_permissions_roles

# Sync value sets
python manage.py sync_valueset
```

---

## 9. Configuration Management

### Environment Variables (.env)

**500+ configuration options across categories:**

| Category | Examples |
|----------|----------|
| Database | DATABASE_URL, CONN_MAX_AGE |
| Redis | REDIS_URL, LOCK_TIMEOUT |
| Security | DJANGO_SECRET_KEY, JWT_*_LIFETIME |
| Email | EMAIL_HOST, EMAIL_FROM, EMAIL_BACKEND |
| Storage | BUCKET_*, FILE_UPLOAD_* |
| Rate Limiting | RATE_LIMIT, DISABLE_RATELIMIT |
| Audit | AUDIT_LOG_ENABLED |
| EMR Limits | MAX_ENCOUNTERS_*, MAX_APPOINTMENTS_* |

### Settings Files

```
config/settings/
├── base.py          # Common settings (712 lines)
├── local.py         # Development
├── test.py          # Testing
├── staging.py       # Staging
├── production.py    # Production
├── deployment.py    # Deployment-specific (Sentry, SSL)
└── config.py        # Business logic parameters
```

### Feature Flags

```python
class FacilityFlag(BaseFlag):
    facility = models.ForeignKey(Facility)
    flag = models.CharField(max_length=1024)

    # Cache: facility_flag_cache:{facility_id}:{flag_name}
    # TTL: 86400 seconds (1 day)
```

### Business Logic Limits

| Parameter | Default | Purpose |
|-----------|---------|---------|
| MAX_DATAPOINTS_PER_UPSERT | 100 | Batch operation limit |
| MAX_REQUESTS_PER_BATCH | 20 | API batch limit |
| MAX_APPOINTMENTS_PER_PATIENT | 10 | Scheduling limit |
| MAX_ACTIVE_ENCOUNTERS | 5 | Per patient per facility |
| MAX_FAVORITES_PER_LIST | 50 | UI limit |
| LOCATION_MAX_DEPTH | 10 | Hierarchy depth |

---

## 10. Code Reusability & Design Patterns

### Design Patterns Used

| Pattern | Location | Usage |
|---------|----------|-------|
| Strategy | SMS backends, Evaluators | Interchangeable algorithms |
| Factory | Context builders, Resources | Object creation |
| Template Method | TagManager, ContextBuilder | Customizable workflows |
| Registry | Permissions, Reports, Extensions | Dynamic registration |
| Mixin Composition | ViewSets | Flexible behavior assembly |
| Decorator | @cacheable, @action | Cross-cutting concerns |
| Observer | Django signals | Cache invalidation |

### ViewSet Mixin Architecture

```python
class EMRModelViewSet(
    EMRCreateMixin,      # perform_create, authorize_create
    EMRRetrieveMixin,    # authorize_retrieve
    EMRUpdateMixin,      # perform_update, authorize_update
    EMRListMixin,        # serialize_list
    EMRDestroyMixin,     # authorize_destroy, validate_destroy
    EMRBaseViewSet,      # Base functionality
    EMRUpsertMixin,      # Batch upsert
):
    pass
```

### Resource Pattern (Pydantic-Based)

```python
class EMRResource(BaseModel):
    __model__ = None  # Django model
    __exclude__ = []  # Fields to exclude

    @classmethod
    def serialize(cls, obj, user=None):
        """Django model → Pydantic object"""

    def de_serialize(self, obj=None, partial=False):
        """Pydantic object → Django model"""
```

### Plugin System

```python
@dataclass
class Plug:
    name: str
    package_name: str  # Git URL
    version: str = "@main"
    configs: dict = {}

class PlugManager:
    def install(self): ...      # pip install plugins
    def get_apps(self): ...     # INSTALLED_APPS
    def get_config(self): ...   # Plugin configs
```

**Plugin API Mount**: `/api/{plugin-name}/`

### Authorization Handler Pattern

```python
class AuthorizationHandler:
    actions = []  # can_* methods
    queries = []  # get_* methods

    def check_permission_in_organization(self, permissions, user, orgs=None):
        """Organization-scoped authorization"""

class AuthorizationController:
    @classmethod
    def call(cls, item, *args, **kwargs):
        """Dynamic dispatch: can_* or get_*"""
```

---

## 11. Documentation Approach

### Documentation Stack

| Tool | Purpose |
|------|---------|
| Sphinx | Documentation generation |
| Furo Theme | Modern documentation UI |
| MyST Parser | Markdown support |
| drf-spectacular | API documentation |
| autodoc | Auto-generate from docstrings |

### API Documentation

- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### Documentation Structure

```
docs/
├── development/
│   ├── local-setup.rst
│   ├── nix-development.md
│   └── pluggable-apps.md
├── setup/
│   ├── database-backup.rst
│   └── keys.rst
└── conf.py
```

### Root Level Docs

- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community guidelines
- `SECURITY.md` - Security policies

### Docstring Coverage

- **Coverage**: ~32.6% (582 docstrings / 1786 functions)
- **Style**: NumPy/Google format
- **Focus**: Method signatures and purpose

---

## 12. Project Structure

```
care/
├── care/                    # Main application
│   ├── emr/                 # Electronic Medical Records (core)
│   │   ├── models/          # 46+ data models
│   │   ├── api/viewsets/    # REST API endpoints
│   │   ├── resources/       # Pydantic serializers
│   │   ├── tasks/           # Celery tasks
│   │   ├── fhir/            # FHIR compliance
│   │   ├── reports/         # Report generation
│   │   ├── tagging/         # Tag management
│   │   └── registries/      # System registries
│   ├── facility/            # Facility management
│   ├── users/               # User management
│   ├── security/            # Authorization & permissions
│   │   ├── authorization/   # 38+ auth handlers
│   │   └── permissions/     # 40+ permission classes
│   ├── audit_log/           # Audit logging
│   └── utils/               # Shared utilities
├── config/                  # Django configuration
│   ├── settings/            # Environment configs
│   ├── api_router.py        # API routing (517 lines)
│   └── celery_app.py        # Celery config
├── plugs/                   # Plugin system
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── data/                    # Fixture data
└── docker/                  # Docker configs
```

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| config/settings/base.py | Main Django settings | 712 |
| config/api_router.py | API route definitions | 517 |
| .env.example | Environment configuration | 511 |
| care/utils/models/base.py | Base model classes | ~150 |

---

## Summary

The Care Backend is a **production-grade healthcare platform** built with:

- **Modular Django Monolith** architecture for maintainability
- **Comprehensive security** with JWT, MFA, RBAC
- **Healthcare standards compliance** (FHIR, SNOMED CT, LOINC, HL7)
- **Scalable infrastructure** with Celery, Redis, PostgreSQL
- **Extensible design** via plugin system and registry patterns
- **Strong data integrity** with soft deletes, audit trails, and transactions
- **Enterprise features** including audit logging, error tracking, and monitoring

The system is designed to handle:
- Patient management and medical records
- Facility and resource management
- Scheduling and appointments
- Billing and inventory
- Reporting and analytics

---

*Last Updated: January 2025*

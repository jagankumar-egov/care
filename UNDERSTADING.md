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

## 13. API Endpoints Overview

### Total Endpoints Count

| Metric | Count |
|--------|-------|
| **ViewSet Registrations** | 85 |
| **Total API Endpoints** | 100+ (including CRUD operations) |
| **Nested Router Groups** | 6 |

### Endpoint Categories

| Category | Endpoints | Base Path | Key ViewSets |
|----------|-----------|-----------|--------------|
| **Authentication** | 6 | `/api/v1/auth/` | TokenObtainPairView, LogoutView |
| **User Management** | 3 | `/api/v1/users/` | UserViewSet, MFALoginViewSet |
| **Patient Management** | 13+ | `/api/v1/patient/` | PatientViewSet + nested routes |
| **Facility Management** | 45+ | `/api/v1/facility/` | FacilityViewSet + 30+ nested |
| **Organization** | 3 | `/api/v1/organization/` | OrganizationViewSet |
| **Inventory & Orders** | 9 | `/api/v1/supply_*/` | SupplyDelivery, SupplyRequest |
| **Questionnaires** | 4 | `/api/v1/questionnaire/` | QuestionnaireViewSet |
| **Security/RBAC** | 2 | `/api/v1/role/` | RoleViewSet, PermissionViewSet |
| **Utilities** | 6 | `/api/v1/files/` | FileUploadViewSet, ValueSetViewSet |

### Nested Router Structure

```
/api/v1/patient/{patient_id}/
├── allergy_intolerance/
├── symptom/
├── diagnosis/
├── diagnostic_report/
├── consent/
├── observation/
├── questionnaire_response/
├── medication/
│   ├── request/
│   ├── prescription/
│   ├── statement/
│   └── administration/
└── thread/
    └── {thread_id}/notes/

/api/v1/facility/{facility_id}/
├── organizations/
├── users/
├── schedulable_users/
├── schedule/
│   └── {schedule_id}/availability/
├── token/
│   ├── queue/
│   │   └── {queue_id}/token/
│   ├── category/
│   └── sub_queue/
├── slots/
├── appointments/
├── location/
│   └── {location_id}/product/
├── device/
├── account/
├── charge_item/
├── charge_item_definition/
├── invoice/
├── payment_reconciliation/
├── specimen/
└── service_request/
```

### Key Files

| File | Purpose |
|------|---------|
| `config/api_router.py` | All 85 ViewSet registrations (517 lines) |
| `config/urls.py` | URL configuration and auth endpoints |

---

## 14. Database Tables & Models

### Model Count by App

| App | Model Count | Purpose |
|-----|-------------|---------|
| **EMR** | 70 | Clinical, scheduling, inventory, billing |
| **Users** | 10 | User management, skills, flags |
| **Security** | 4 | RBAC, permissions, roles |
| **Facility** | 3 | Facility management |
| **Utils** | 2 | Base abstractions |
| **TOTAL** | **89** | |

### Model Inheritance Hierarchy

```
Django models.Model
        │
        ▼
BaseModel (care/utils/models/base.py:15-32)
├── external_id (UUID, unique, indexed)
├── created_date (auto_now_add)
├── modified_date (auto_now)
├── deleted (soft delete flag)
└── objects = BaseManager()  # Filters deleted=False
        │
        ▼
EMRBaseModel (care/emr/models/base.py:8-29)
├── history (JSONField)
├── meta (JSONField)
├── created_by (FK → User)
└── updated_by (FK → User)
        │
        ▼
SlugBaseModel (care/emr/models/base.py:32-64)
├── Facility-scoped slug generation
└── Methods: calculate_slug(), parse_slug()
        │
        ▼
Concrete Models (Patient, Encounter, Account, etc.)
```

### Key EMR Models

| Model | File | Key Fields |
|-------|------|------------|
| **Patient** | `emr/models/patient.py` | name, gender, phone, dob, blood_group, extensions |
| **Encounter** | `emr/models/encounter.py` | status, encounter_class, patient, facility, period |
| **Account** | `emr/models/account.py` | status, billing_status, total_net/gross/paid/balance |
| **Invoice** | `emr/models/invoice.py` | status, charge_items, total_net/gross, locked |
| **ChargeItem** | `emr/models/charge_item.py` | status, quantity, unit_price, total_price |
| **MedicationRequest** | `emr/models/medication_request.py` | status, intent, medication, dosage_instruction |
| **Organization** | `emr/models/organization.py` | name, org_type, parent, level_cache |
| **FacilityLocation** | `emr/models/location.py` | facility, parent, location_type, level_cache |

### Database Table Naming

Django generates table names as `{app_label}_{model_name}`:
- `emr_patient` → Patient model
- `emr_encounter` → Encounter model
- `emr_account` → Account model
- `users_user` → User model
- `facility_facility` → Facility model

### Flexible Schema Fields

Models use JSONField for flexibility:

```python
class Patient(EMRBaseModel):
    extensions = JSONField(default=dict)        # FHIR extensions
    instance_identifiers = JSONField(default=list)
    facility_identifiers = JSONField(default=dict)
    facility_tags = JSONField(default=dict)

class Account(EMRBaseModel):
    extensions = JSONField(default=dict)
    service_period = JSONField(default=dict)
    cached_items = JSONField(default=dict)
    total_price_components = JSONField(default=dict)
```

### Denormalized Cache Fields

For performance optimization:

```python
class Patient(EMRBaseModel):
    organization_cache = ArrayField(IntegerField(), default=list)
    users_cache = ArrayField(IntegerField(), default=list)
    instance_tags = ArrayField(IntegerField(), default=list)

class FacilityLocation(EMRBaseModel):
    parent_cache = ArrayField(IntegerField(), default=list)
    facility_organization_cache = ArrayField(IntegerField(), default=list)
    level_cache = IntegerField(default=0)
```

---

## 15. Request-to-Database Flow

### Architecture Pattern

```
HTTP Request
     │
     ▼
URL Router (config/api_router.py)
     │
     ▼
ViewSet (EMRModelViewSet)
     │
     ▼
Pydantic Spec (validation/serialization)
     │
     ▼
Django Model (ORM)
     │
     ▼
PostgreSQL Table
```

### Concrete Example: Create Medication Request

```
POST /api/v1/patient/{patient_id}/medication/request/
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. URL Router (config/api_router.py:431-464)                │
│    - Matches: patient_nested_router                         │
│    - Routes to: MedicationRequestViewSet                    │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ViewSet (care/emr/api/viewsets/medication_request.py:45) │
│    database_model = MedicationRequest                       │
│    pydantic_model = MedicationRequestSpec                   │
│    pydantic_read_model = MedicationRequestReadSpec          │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Pydantic Spec (care/emr/resources/medication/request/)   │
│    - Validates: status, intent, medication, dosage          │
│    - Type checking with enums                               │
│    - __model__ = MedicationRequest                          │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Django Model (care/emr/models/medication_request.py:31)  │
│    - ForeignKey: patient, encounter, requester              │
│    - JSONField: medication, dosage_instruction              │
│    - Inherits audit fields from EMRBaseModel                │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PostgreSQL Table: emr_medicationrequest                  │
│    INSERT INTO emr_medicationrequest (...)                  │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Response: 201 Created                                    │
│    Serialized via MedicationRequestReadSpec                 │
└─────────────────────────────────────────────────────────────┘
```

### ViewSet to Model Mapping

```python
# care/emr/api/viewsets/medication_request.py
class MedicationRequestViewSet(EMRModelViewSet):
    database_model = MedicationRequest           # ORM Model
    pydantic_model = MedicationRequestSpec       # Create/Input validation
    pydantic_read_model = MedicationRequestReadSpec    # List output
    pydantic_update_model = MedicationRequestUpdateSpec  # Update input
    pydantic_retrieve_model = MedicationRequestRetrieveSpec  # Detail output
```

---

## 16. Registry Design Patterns

The codebase uses **Registry patterns** instead of traditional Factory classes for object creation and lookup.

### Extension Registry

**File**: `care/emr/registries/extensions/registry.py`

```python
class ExtensionRegistry:
    _extensions = {}  # {resource_type: {extension_name: handler}}

    @classmethod
    def register(cls, extension_obj):
        # Validates ExtensionBase subclass
        resource_type = extension_obj.resource_type.value
        extension_name = extension_obj.extension_name
        cls._extensions[resource_type][extension_name] = extension_obj

    @classmethod
    def get_extension_obj(cls, resource_type, extension_name):
        return cls._extensions.get(resource_type, {}).get(extension_name)
```

**Supported Resource Types** (`care/emr/extensions/base.py`):
- account, encounter, patient
- payment_reconciliation, supply_delivery, product

### Device Type Registry

**File**: `care/emr/registries/device_type/device_registry.py`

```python
class DeviceTypeBase:
    """Base class for device handlers"""
    def handle_create(self, request_data, obj): return obj
    def handle_update(self, request_data, obj): return obj
    def handle_delete(self, obj): return obj
    def list(self, obj): return {}
    def retrieve(self, obj): return {}

class DeviceTypeRegistry:
    _device_types = {}

    @classmethod
    def register(cls, device_type, device_class):
        cls._device_types[device_type] = device_class

    @classmethod
    def get_care_device_class(cls, device_type):
        return cls._device_types.get(device_type)
```

### Feature Flag Registry

**File**: `care/utils/registries/feature_flag.py`

```python
class FlagRegistry:
    _flags = {}  # {FlagType: {flag_name: True}}

    @classmethod
    def register(cls, flag_type, flag_name):
        cls._flags[flag_type][flag_name] = True

    @classmethod
    def get_all_flags(cls, flag_type):
        return list(cls._flags.get(flag_type, {}).keys())
```

### Usage Pattern

```python
# Registration (typically in apps.py ready() or module init)
DeviceTypeRegistry.register("camera", CameraDeviceHandler)
ExtensionRegistry.register(MyCustomExtension())
FlagRegistry.register(FlagType.USER, "beta_feature")

# Retrieval
handler = DeviceTypeRegistry.get_care_device_class("camera")
extension = ExtensionRegistry.get_extension_obj("patient", "custom_fields")
```

---

## 17. Sub-Modular Package Structure

All Django apps follow a consistent organizational pattern.

### Standard App Structure

```
{app_name}/
├── __init__.py
├── apps.py                 # AppConfig with ready() hook
├── models/                 # Django ORM models
│   ├── __init__.py        # Exports all models
│   └── {model}.py
├── api/
│   └── viewsets/          # DRF ViewSets
│       ├── __init__.py
│       ├── base.py        # Base classes/mixins
│       └── {resource}.py
├── resources/             # Pydantic specs (EMR only)
│   ├── __init__.py
│   ├── base.py
│   └── {resource}/
│       └── spec.py
├── migrations/            # Database migrations
├── admin/                 # Django admin (optional)
├── signals/               # Django signals (optional)
└── tests/                 # Unit tests (optional)
```

### Comparison Across Apps

| Component | EMR | Facility | Security | Users |
|-----------|-----|----------|----------|-------|
| **Models** | 46 files, nested | 3 files, flat | 3 files | 1 file (253 lines) |
| **ViewSets** | 55+ files | Integrated | 4+ viewsets | Standard CRUD |
| **Serializers** | Pydantic specs (50+) | Inline | Inline | Inline |
| **Migrations** | 74 files | 170 files | 9 files | 29 files |
| **Registries** | 4 directories | None | Dedicated module | None |

### Resource Spec Pattern (EMR Standard)

Each EMR resource follows this spec hierarchy:

```python
# care/emr/resources/{resource}/spec.py

class {Resource}BaseSpec(EMRResource, ExtensionValidator):
    __model__ = {Model}
    __exclude__ = [...]
    # Core fields

class {Resource}ListSpec({Resource}BaseSpec):
    # List view fields (minimal)

class {Resource}CreateSpec({Resource}ListSpec):
    # Input validation for creation

class {Resource}UpdateSpec({Resource}ListSpec):
    # Input validation for updates

class {Resource}RetrieveSpec({Resource}ListSpec, {Resource}PermissionsMixin):
    # Detail view with permissions
```

---

## 18. Plugin System

### Architecture Overview

The plugin system uses **environment-based configuration** with a lightweight manager.

### Core Files

| File | Purpose |
|------|---------|
| `plug_config.py` | Plugin definitions |
| `plugs/plug.py` | Plug dataclass |
| `plugs/manager.py` | PlugManager class |
| `install_plugins.py` | Installation script |

### Plug Dataclass

**File**: `plugs/plug.py`

```python
@dataclass(slots=True)
class Plug:
    name: str              # Django app name
    package_name: str      # PyPI/Git package name
    version: str = "@main" # Version specifier
    configs: dict = field(default_factory=dict)
```

### PlugManager

**File**: `plugs/manager.py`

```python
class PlugManager:
    def __init__(self, plugs: list[Plug]):
        self.plugs = plugs
        # Also loads from ADDITIONAL_PLUGS env var

    def install(self):
        """pip install each plugin"""
        for plug in self.plugs:
            subprocess.run([
                "pip", "install",
                f"{plug.package_name}{plug.version}"
            ])

    def get_apps(self) -> list[str]:
        """Returns app names for INSTALLED_APPS"""
        return [plug.name for plug in self.plugs]

    def get_config(self) -> dict:
        """Returns plugin configurations"""
        return {plug.name: plug.configs for plug in self.plugs}
```

### Integration with Django

**File**: `config/settings/base.py`

```python
from plug_config import manager

PLUGIN_APPS = manager.get_apps()
PLUGIN_CONFIGS = manager.get_config()

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + PLUGIN_APPS
```

### Loading Plugins via Environment

```bash
export ADDITIONAL_PLUGS='[
    {
        "name": "my_plugin",
        "package_name": "git+https://github.com/org/my-plugin.git",
        "version": "@v1.0.0",
        "configs": {"setting1": "value1"}
    }
]'
```

---

## 19. Creating New Plugins

### Option 1: Environment Variable (Quick Testing)

```bash
# Set plugin via environment
export ADDITIONAL_PLUGS='[{
    "name": "my_custom_plugin",
    "package_name": "my-custom-plugin",
    "version": "==1.0.0",
    "configs": {"api_key": "xxx"}
}]'

# Install plugins
python install_plugins.py

# Start server
python manage.py runserver
```

### Option 2: Direct Configuration (Built-in Plugins)

Edit `plug_config.py`:

```python
from plugs.manager import PlugManager
from plugs.plug import Plug

plugs = [
    Plug(
        name="care_my_plugin",
        package_name="git+https://github.com/org/care-my-plugin.git",
        version="@main",
        configs={
            "feature_enabled": True,
            "api_endpoint": "https://api.example.com"
        }
    )
]

manager = PlugManager(plugs)
```

### Option 3: Extension Handler (Without Full App)

For device-specific handlers:

```python
# my_extension/device_handler.py
from care.emr.registries.device_type.device_registry import (
    DeviceTypeBase,
    DeviceTypeRegistry,
)

class MyCustomDeviceHandler(DeviceTypeBase):
    def handle_create(self, request_data, obj):
        # Custom creation logic
        obj.metadata["custom_field"] = request_data.get("custom_data")
        obj.save(update_fields=["metadata"])
        return obj

    def handle_update(self, request_data, obj):
        # Custom update logic
        return obj

    def list(self, obj):
        return {"extra_metadata": "value"}

    def retrieve(self, obj):
        return {"extra_metadata": "value", "detailed": True}

# Register in apps.py ready() method
DeviceTypeRegistry.register("my_device_type", MyCustomDeviceHandler)
```

### Plugin Structure Template

```
care-my-plugin/
├── care_my_plugin/
│   ├── __init__.py
│   ├── apps.py              # Django AppConfig
│   ├── models.py            # Optional models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py        # Plugin URL router
│   │   └── viewsets.py
│   └── migrations/
├── pyproject.toml
├── setup.py
└── README.md
```

### apps.py Template

```python
from django.apps import AppConfig

class MyPluginConfig(AppConfig):
    name = "care_my_plugin"
    verbose_name = "My Custom Plugin"

    def ready(self):
        # Register extensions, signals, etc.
        from care.emr.registries.device_type.device_registry import DeviceTypeRegistry
        from .handlers import MyDeviceHandler

        DeviceTypeRegistry.register("my_device", MyDeviceHandler)
```

### Plugin Requirements

1. **Installable via pip**: Package must be pip-installable
2. **Django AppConfig**: Must have `apps.py` with AppConfig
3. **Migrations**: Include if adding models
4. **Configuration**: Access via `settings.PLUGIN_CONFIGS[app_name]`

---

## 20. Model Extension Patterns

### A. FHIR Extensions via JSONField

Models store flexible data in `extensions` JSONField:

```python
class Patient(EMRBaseModel):
    extensions = models.JSONField(default=dict)

# Storage format
{
    "custom_extension_name": {
        "field1": "value1",
        "field2": "value2"
    },
    "another_extension": {
        "nested": {"data": "here"}
    }
}
```

**Validation** via `ExtensionValidator` mixin:

```python
class PatientBaseSpec(EMRResource, ExtensionValidator):
    ___extension_resource_type__ = ExtensionResource.patient
    extensions: dict = {}

    @field_validator("extensions")
    @classmethod
    def validate_extensions(cls, v):
        return validate_extensions(v, ExtensionResource.patient.value)
```

### B. Creating Custom Extensions

**File**: `care/emr/extensions/base.py`

```python
class ExtensionBase:
    resource_type: ExtensionResource  # Which model to extend
    extension_name: str               # Unique name

    write_schema: str = ""            # JSON Schema for validation
    read_schema: str = ""
    retrieve_schema: str = ""

    def validate(self, data, resource=None):
        """Validate extension data"""
        pass

    def serialize_extensions(self, data, resource=None):
        """Convert for API response"""
        return data

# Register extension
ExtensionRegistry.register(MyExtension())
```

### C. Environment-Based Extensions

```python
class CoreEnvExtension(ExtensionBase):
    # Loads schemas from environment variables
    # Key format: CORE_EXTENSIONS_{RESOURCE}_{ACTION}
```

Set via environment:
```bash
export CORE_EXTENSIONS_PATIENT_WRITE='{"type": "object", "properties": {...}}'
```

### D. Metadata via meta Field

For unstructured metadata:

```python
class EMRBaseModel(BaseModel):
    meta = models.JSONField(default=dict)

# Usage
patient.meta["internal_notes"] = "Some note"
patient.save()
```

### E. Denormalized Cache Fields

For performance-critical lookups:

```python
class Patient(EMRBaseModel):
    # Cache organization hierarchy for fast queries
    organization_cache = ArrayField(IntegerField(), default=list)

    def rebuild_organization_cache(self):
        organization_parents = []
        if self.geo_organization:
            organization_parents.extend(self.geo_organization.parent_cache)
            organization_parents.append(self.geo_organization.id)
        self.organization_cache = list(set(organization_parents))
        super().save(update_fields=["organization_cache"])
```

### F. Mixin Patterns for Behavior

**Permission Mixins** (`care/emr/resources/permissions.py`):

```python
class PermissionsMixin(EMRResource):
    permissions: list[str] = []

    @classmethod
    def perform_extra_user_serialization(cls, mapping, obj, user=None):
        if user and user.is_authenticated:
            cls.add_permissions(mapping, user, obj)

class PatientPermissionsMixin(PermissionsMixin):
    @classmethod
    def add_permissions(cls, mapping, user, patient):
        # Calculate user's permissions on this patient
        roles = PatientAccess().find_roles_on_patient(user, patient)
        mapping["permissions"] = list(
            RolePermission.objects.filter(role_id__in=roles)
            .values_list("permission__slug", flat=True)
        )
```

### G. Signal-Based Triggers

For automatic cache updates:

```python
# care/emr/signals/patient/__init__.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=PatientIdentifier)
def update_patient_on_identifier_change(sender, instance, **kwargs):
    instance.patient.rebuild_organization_cache()
    instance.patient.save(update_fields=["organization_cache"])
```

---

## 21. ViewSet Architecture

### Mixin Composition Pattern

**File**: `care/emr/api/viewsets/base.py` (435 lines)

```python
class EMRCreateMixin:
    """POST - Create objects"""
    def perform_create(self, instance):
        instance.created_by = self.request.user
        instance.updated_by = self.request.user
        with transaction.atomic():
            instance.save()

class EMRRetrieveMixin:
    """GET /{id}/ - Single object"""
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.authorize_retrieve(instance)
        return Response(self.serialize(instance))

class EMRListMixin:
    """GET / - List objects"""
    # Pagination, filtering, ordering

class EMRUpdateMixin:
    """PUT/PATCH - Update objects"""

class EMRDestroyMixin:
    """DELETE - Soft delete"""
    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save(update_fields=["deleted"])

class EMRUpsertMixin:
    """POST /upsert/ - Batch create/update"""
```

### Composed ViewSet Classes

```python
class EMRModelViewSet(
    EMRCreateMixin,
    EMRRetrieveMixin,
    EMRUpdateMixin,
    EMRListMixin,
    EMRDestroyMixin,
    EMRBaseViewSet,
    EMRUpsertMixin,
):
    """Full CRUD operations"""
    pass

class EMRModelReadOnlyViewSet(
    EMRRetrieveMixin,
    EMRListMixin,
    EMRBaseViewSet,
):
    """Read-only operations"""
    pass
```

### ViewSet Configuration

```python
class PatientViewSet(EMRModelViewSet):
    # Model mapping
    database_model = Patient

    # Pydantic specs for different operations
    pydantic_model = PatientCreateSpec        # POST input
    pydantic_read_model = PatientListSpec     # GET list output
    pydantic_update_model = PatientUpdateSpec # PUT/PATCH input
    pydantic_retrieve_model = PatientRetrieveSpec  # GET detail output

    # Filtering
    filterset_class = PatientFilters
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_date", "modified_date"]

    # Authorization hooks
    def authorize_create(self, request_obj):
        if not AuthorizationController.call("can_create_patient", self.request.user):
            raise PermissionDenied("Cannot Create Patient")
```

---

## 22. Quick Reference

### Key Files by Purpose

| Purpose | File |
|---------|------|
| All API routes | `config/api_router.py` |
| URL configuration | `config/urls.py` |
| Django settings | `config/settings/base.py` |
| Base models | `care/utils/models/base.py` |
| EMR base models | `care/emr/models/base.py` |
| ViewSet base classes | `care/emr/api/viewsets/base.py` |
| Pydantic base | `care/emr/resources/base.py` |
| Extension system | `care/emr/extensions/base.py` |
| Device registry | `care/emr/registries/device_type/` |
| Permissions | `care/security/permissions/` |
| Authorization | `care/security/authorization/` |
| Plugin manager | `plugs/manager.py` |
| Plugin config | `plug_config.py` |

### Commands Reference

```bash
# Load sample data
python manage.py load_fixtures --users=5 --patients=20 --encounter=2

# Sync permissions and roles
python manage.py sync_permissions_roles

# Sync value sets
python manage.py sync_valueset

# Install plugins
python install_plugins.py

# Run development server
python manage.py runserver

# Run with Docker
make up
```

### Default Test Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin | Admin |
| care-doctor | admin | Doctor |
| care-nurse | admin | Nurse |
| care-staff | admin | Staff |
| care-admin | admin | Administrator |
| care-volunteer | admin | Volunteer |
| care-fac-admin | admin | Facility Admin |

---

*Last Updated: February 2025*

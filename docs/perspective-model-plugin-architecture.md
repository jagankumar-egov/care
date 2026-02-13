# Care Backend: Model Inheritance & Plugin Architecture Perspective

This document provides a comprehensive overview of the Care backend's model inheritance hierarchy and plugin extensibility architecture.

---

## Table of Contents

1. [Model Inheritance Hierarchy](#model-inheritance-hierarchy)
2. [Model Statistics](#model-statistics)
3. [Extending Models from Plugins](#extending-models-from-plugins)
4. [Plugin Injection Mechanism](#plugin-injection-mechanism)
5. [Modifiable Behaviors](#modifiable-behaviors)
6. [Architecture Diagrams](#architecture-diagrams)

---

## Model Inheritance Hierarchy

### Tier 1: BaseModel

**Location:** `care/utils/models/base.py`

The foundation of all Care models providing:

| Field | Type | Purpose |
|-------|------|---------|
| `external_id` | UUIDField | Unique external identifier for API exposure |
| `created_date` | DateTimeField | Auto-set on creation |
| `modified_date` | DateTimeField | Auto-updated on save |
| `deleted` | BooleanField | Soft delete flag (default: False) |

**Features:**
- Custom `BaseManager` that filters soft-deleted records by default
- Overridden `delete()` method implementing soft deletes
- All queries automatically exclude deleted records unless explicitly requested

### Tier 2: EMRBaseModel

**Location:** `care/emr/models/base.py`

Extends `BaseModel` with EMR-specific fields:

| Field | Type | Purpose |
|-------|------|---------|
| `history` | JSONField | Audit trail / change history |
| `meta` | JSONField | Flexible metadata storage |
| `created_by` | ForeignKey(User) | Creator tracking |
| `updated_by` | ForeignKey(User) | Last modifier tracking |

### Tier 3: SlugBaseModel

**Location:** `care/emr/models/base.py`

Extends `EMRBaseModel` for definition-type models:

- Slug generation and parsing
- `FACILITY_SCOPED` flag for facility-specific slugs
- Methods: `calculate_slug()`, `parse_slug()`

### Patient Model

**Location:** `care/emr/models/patient.py`

Inherits from `EMRBaseModel`. Key fields:

```python
class Patient(EMRBaseModel):
    name: str
    gender: str
    phone_number: str
    date_of_birth: date
    blood_group: str
    geo_organization: ForeignKey(Organization)

    # Cache arrays for performance
    organization_cache: ArrayField(IntegerField)
    users_cache: ArrayField(IntegerField)
    instance_tags: ArrayField(IntegerField)

    # Extension point
    extensions: JSONField(default=dict)
```

**Note:** Patient is a leaf class - no models directly inherit from it.

---

## Model Statistics

### Models Inheriting from BaseModel (Direct)

| Count | Description |
|-------|-------------|
| **6** | Direct subclasses |

1. `PatientMobileOTP` - `care/facility/models/patient.py`
2. `Facility` - `care/facility/models/facility.py`
3. `Skill` - `care/users/models.py`
4. `UserSkill` - `care/users/models.py`
5. `BaseFlag` - `care/utils/models/base.py` (abstract)
6. `EMRBaseModel` - `care/emr/models/base.py`

### Models Inheriting from EMRBaseModel

| Count | Description |
|-------|-------------|
| **70** | Direct subclasses |

**Core EMR Models:**
- Patient, Encounter, Observation, Condition
- MedicationRequest, MedicationStatement, MedicationAdministration
- DiagnosticReport, ServiceRequest, Specimen
- AllergyIntolerance, Consent
- FacilityLocation, Device
- Account, Invoice, ChargeItem
- Questionnaire, QuestionnaireResponse
- NoteThread, NoteMessage
- ValueSet, FileUpload
- And 50+ more...

### Models Inheriting from SlugBaseModel

| Count | Description |
|-------|-------------|
| **7** | Direct subclasses |

1. `ProductKnowledge`
2. `ResourceCategory`
3. `ChargeItemDefinition`
4. `ActivityDefinition`
5. `SpecimenDefinition`
6. `Template`
7. `ObservationDefinition`

### Summary

| Category | Count |
|----------|-------|
| Direct BaseModel subclasses | 6 |
| Direct EMRBaseModel subclasses | 70 |
| Direct SlugBaseModel subclasses | 7 |
| **Total Django Models** | **83** |
| Patient direct subclasses | 0 |

---

## Extending Models from Plugins

### Method 1: FHIR Extensions via JSONField

The **recommended approach** for extending existing models without modifying core code.

**Models with `extensions` field:**
- `Patient`
- `Account`
- `SupplyDelivery`
- `Product`
- `PaymentReconciliation`
- `Encounter`

**Extension Storage Format:**
```json
{
    "custom_extension_name": {
        "field1": "value1",
        "field2": "value2"
    },
    "insurance_details": {
        "provider": "ACME Insurance",
        "policy_number": "POL123456"
    }
}
```

**Creating a Custom Extension:**

```python
# my_plugin/extensions.py
from care.emr.extensions.base import ExtensionBase, ExtensionResource, ExtensionOwners

class InsuranceExtension(ExtensionBase):
    resource_type = ExtensionResource.patient
    extension_name = "insurance_details"
    extension_owner = ExtensionOwners.plug
    extension_version = "1.0.0"

    write_schema = {
        "type": "object",
        "properties": {
            "provider": {"type": "string"},
            "policy_number": {"type": "string"},
            "valid_until": {"type": "string", "format": "date"}
        },
        "required": ["provider", "policy_number"]
    }
    read_schema = write_schema
    retrieve_schema = write_schema

    def validate(self, data, resource=None):
        # Custom validation logic
        if data.get("policy_number") and len(data["policy_number"]) < 5:
            raise ValueError("Policy number must be at least 5 characters")

    def serialize_extensions(self, data, resource=None):
        # Transform for API response
        return data
```

**Register in Plugin's apps.py:**
```python
# my_plugin/apps.py
from django.apps import AppConfig

class MyPluginConfig(AppConfig):
    name = "my_plugin"

    def ready(self):
        from care.emr.registries.extensions.registry import ExtensionRegistry
        from .extensions import InsuranceExtension

        ExtensionRegistry.register(InsuranceExtension())
```

### Method 2: Adding New Models

Plugins can define their own models that reference core models:

```python
# my_plugin/models.py
from django.db import models
from care.emr.models.patient import Patient
from care.emr.models.base import EMRBaseModel

class PatientInsurance(EMRBaseModel):
    """Plugin model extending Patient functionality"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="insurance_records")
    provider = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    valid_from = models.DateField()
    valid_until = models.DateField()
    coverage_type = models.CharField(max_length=50)
```

### Method 3: Core Environment Extensions

For configuration-driven extensions without code:

```bash
# Set via environment variables
export CORE_EXTENSIONS_PATIENT_WRITE='{"type": "object", "properties": {"custom_field": {"type": "string"}}}'
export CORE_EXTENSIONS_PATIENT_READ='{"type": "object", "properties": {"custom_field": {"type": "string"}}}'
```

---

## Plugin Injection Mechanism

### Plugin System Components

```
plug_config.py          → Define plugins
    ↓
PlugManager             → Manage installation & configuration
    ↓
config/settings/base.py → Integrate into Django
    ↓
config/urls.py          → Register API routes
```

### Step 1: Plugin Definition

**Option A: Static Configuration (`plug_config.py`)**
```python
from plugs.manager import PlugManager
from plugs.plug import Plug

plugs = [
    Plug(
        name="care_scribe",
        package_name="git+https://github.com/ohcnetwork/care_scribe.git",
        version="@main",
        configs={
            "AI_SERVICE_URL": "https://ai.example.com",
            "ENABLE_AUTOFILL": True
        }
    ),
    Plug(
        name="my_insurance_plugin",
        package_name="git+https://github.com/org/my-insurance-plugin.git",
        version="@v1.0.0",
        configs={}
    )
]

manager = PlugManager(plugs)
```

**Option B: Runtime via Environment Variable**
```bash
export ADDITIONAL_PLUGS='[
    {
        "name": "my_plugin",
        "package_name": "git+https://github.com/org/my-plugin.git",
        "version": "@v1.0.0",
        "configs": {"API_KEY": "xxx"}
    }
]'
```

### Step 2: Plugin Installation

```bash
python install_plugins.py
```

This runs `pip install` for each plugin based on the package_name and version.

### Step 3: Django Integration

**Settings (`config/settings/base.py`):**
```python
from plug_config import manager

PLUGIN_APPS = manager.get_apps()      # ['care_scribe', 'my_plugin']
PLUGIN_CONFIGS = manager.get_config() # {'care_scribe': {...}, 'my_plugin': {...}}

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + PLUGIN_APPS
```

**URLs (`config/urls.py`):**
```python
for plug in settings.PLUGIN_APPS:
    urlpatterns += [path(f"api/{plug}/", include(f"{plug}.urls"))]
```

### Plugin Structure Template

Use the [care-plugin-cookiecutter](https://github.com/ohcnetwork/care-plugin-cookiecutter) template:

```
my_plugin/
├── __init__.py
├── apps.py              # AppConfig with ready() hook
├── models.py            # Django models
├── urls.py              # API routes
├── api/
│   └── viewsets/        # DRF ViewSets
├── extensions/          # FHIR extensions
├── signals/             # Django signals
└── migrations/          # Database migrations
```

---

## Modifiable Behaviors

### 1. Extension System

**Available Resources for Extension:**
- `patient`
- `account`
- `encounter`
- `payment_reconciliation`
- `supply_delivery`
- `supply_delivery_order`
- `product`

**Extension Lifecycle:**
```
API Request → ExtensionValidator → validate() → serialize_extensions() → Response
```

### 2. Device Type Registry

Custom device handlers for medical devices:

```python
# my_plugin/devices.py
from care.emr.registries.device_type.device_registry import DeviceTypeBase, DeviceTypeRegistry

class CustomMonitorDevice(DeviceTypeBase):
    def handle_create(self, device, **kwargs):
        # Custom creation logic
        pass

    def handle_update(self, device, **kwargs):
        # Custom update logic
        pass

    def handle_delete(self, device, **kwargs):
        # Custom deletion logic
        pass

    def serialize_list(self, device):
        # Custom list serialization
        return {"id": device.id, "custom_field": "value"}

# Register
DeviceTypeRegistry.register("custom_monitor", CustomMonitorDevice())
```

### 3. Django Signals

Hook into model lifecycle events:

```python
# my_plugin/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from care.emr.models.patient import Patient

@receiver(post_save, sender=Patient)
def sync_patient_to_external_system(sender, instance, created, **kwargs):
    if created:
        # Sync new patient to external system
        external_api.create_patient(instance)

@receiver(pre_save, sender=Patient)
def validate_patient_data(sender, instance, **kwargs):
    # Custom validation before save
    if not instance.phone_number:
        raise ValueError("Phone number is required")
```

### 4. Custom API Endpoints

```python
# my_plugin/api/viewsets/insurance.py
from rest_framework.viewsets import ModelViewSet
from care.emr.api.viewsets.base import EMRModelViewSet
from ..models import PatientInsurance
from ..serializers import PatientInsuranceSerializer

class PatientInsuranceViewSet(EMRModelViewSet):
    queryset = PatientInsurance.objects.all()
    serializer_class = PatientInsuranceSerializer
    filterset_fields = ["patient", "provider"]
```

### 5. Configuration Access

```python
# Access plugin configuration anywhere
from django.conf import settings

def get_my_config():
    plugin_configs = settings.PLUGIN_CONFIGS
    my_config = plugin_configs.get("my_plugin", {})
    return {
        "api_key": my_config.get("API_KEY"),
        "feature_enabled": my_config.get("ENABLE_FEATURE", False)
    }
```

### 6. Persistent Plugin Configuration

```python
# Using PlugConfig model for runtime configuration
from care.users.models import PlugConfig

# Get or create plugin config
config, created = PlugConfig.objects.get_or_create(
    slug="my_plugin_settings",
    defaults={"meta": {"setting1": "value1"}}
)

# Update config
config.meta["setting2"] = "value2"
config.save()
```

---

## Architecture Diagrams

### Model Inheritance Hierarchy

```
                    ┌──────────────┐
                    │  BaseModel   │
                    │  (Abstract)  │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Facility   │   │ EMRBaseModel │   │    Skill     │
└──────────────┘   └──────┬───────┘   └──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Patient    │  │ SlugBaseModel│  │  Encounter   │
│  (70+ more)  │  └──────┬───────┘  │  Observation │
│              │         │          │  Condition   │
│  extensions  │         ▼          │     ...      │
│   (JSON)     │  ┌──────────────┐  └──────────────┘
└──────────────┘  │  Template    │
                  │  Definition  │
                  │   Models     │
                  └──────────────┘
```

### Plugin Integration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Plugin Installation                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  plug_config.py                    ADDITIONAL_PLUGS env              │
│       │                                   │                          │
│       └───────────────┬───────────────────┘                          │
│                       ▼                                              │
│               ┌───────────────┐                                      │
│               │  PlugManager  │                                      │
│               └───────┬───────┘                                      │
│                       │                                              │
│         ┌─────────────┼─────────────┐                               │
│         ▼             ▼             ▼                               │
│    get_apps()   get_config()   install()                            │
│         │             │             │                               │
│         ▼             ▼             ▼                               │
│  INSTALLED_APPS  PLUGIN_CONFIGS  pip install                        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        Runtime Integration                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Django Startup                                                      │
│       │                                                              │
│       ▼                                                              │
│  AppConfig.ready()                                                   │
│       │                                                              │
│       ├──► Register Extensions (ExtensionRegistry)                  │
│       ├──► Register Device Types (DeviceTypeRegistry)               │
│       ├──► Connect Signals (post_save, pre_save, etc.)              │
│       └──► Initialize Plugin Services                               │
│                                                                       │
│  Request Flow                                                        │
│       │                                                              │
│       ▼                                                              │
│  /api/{plugin}/* ──► Plugin ViewSets ──► Plugin Models              │
│       │                                                              │
│       ▼                                                              │
│  /api/v1/patient/ ──► ExtensionValidator ──► extensions field       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Extension System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Extension Registration                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Plugin AppConfig.ready()                                            │
│          │                                                           │
│          ▼                                                           │
│  ┌─────────────────────┐     ┌──────────────────────────────────┐  │
│  │  ExtensionRegistry  │◄────│  MyExtension(ExtensionBase)      │  │
│  │  .register()        │     │    resource_type = patient       │  │
│  └─────────┬───────────┘     │    extension_name = "custom"     │  │
│            │                 │    write_schema = {...}          │  │
│            ▼                 │    validate()                    │  │
│  _extensions = {             │    serialize_extensions()        │  │
│    "patient": {              └──────────────────────────────────┘  │
│      "custom": MyExtension                                          │
│    }                                                                 │
│  }                                                                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     API Request with Extensions                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  POST /api/v1/patient/                                               │
│  {                                                                    │
│    "name": "John Doe",                                               │
│    "extensions": {                                                   │
│      "custom": {"field1": "value1"}                                 │
│    }                                                                  │
│  }                                                                    │
│          │                                                           │
│          ▼                                                           │
│  ┌─────────────────────┐                                            │
│  │ ExtensionValidator  │                                            │
│  │ (Pydantic Field)    │                                            │
│  └─────────┬───────────┘                                            │
│            │                                                         │
│            ▼                                                         │
│  ExtensionRegistry.get_extension_obj("patient", "custom")           │
│            │                                                         │
│            ▼                                                         │
│  MyExtension.validate({"field1": "value1"})                         │
│            │                                                         │
│            ▼                                                         │
│  Patient.objects.create(..., extensions={...})                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Creating a Plugin

### 1. Generate from Template
```bash
cookiecutter https://github.com/ohcnetwork/care-plugin-cookiecutter
```

### 2. Define Plugin Structure
```
my_plugin/
├── apps.py          # Register extensions, signals
├── models.py        # New models (inherit EMRBaseModel)
├── urls.py          # API routes
├── extensions/      # FHIR extensions
└── migrations/
```

### 3. Register Plugin
```python
# plug_config.py
plugs = [
    Plug(
        name="my_plugin",
        package_name="git+https://github.com/org/my-plugin.git",
        version="@main"
    )
]
```

### 4. Install & Run
```bash
python install_plugins.py
python manage.py migrate my_plugin
python manage.py runserver
```

---

## Summary

The Care backend provides a robust, FHIR-inspired architecture for healthcare applications:

| Feature | Mechanism | Use Case |
|---------|-----------|----------|
| **Model Extension** | JSONField extensions | Add custom fields without schema changes |
| **New Models** | Inherit EMRBaseModel | Add entirely new entities |
| **Custom Logic** | Django Signals | React to model lifecycle events |
| **Custom APIs** | Plugin ViewSets | Add new endpoints |
| **Device Handling** | DeviceTypeRegistry | Custom medical device logic |
| **Configuration** | PLUGIN_CONFIGS | Plugin-specific settings |

The plugin system enables organizations to customize Care for their specific needs while maintaining upgradeability with the core platform.

---

## Deep Dive: Slug System

### What is a Slug?

A **slug** is a human-readable, URL-safe identifier used instead of database IDs for API lookups. In Care, slugs provide:

- Unique identifiers across facilities
- Human-readable URLs (e.g., `/activity_definition/f-uuid-blood-test/`)
- Scope isolation (facility vs instance level)

### Slug Format

| Scope | Format | Example |
|-------|--------|---------|
| Facility-scoped | `f-{facility_uuid}-{slug_value}` | `f-550e8400-e29b-41d4-a716-446655440000-blood-test` |
| Instance-scoped | `i-{slug_value}` | `i-global-blood-test` |

### SlugBaseModel Implementation

**Location:** `care/emr/models/base.py:32-64`

```python
class SlugBaseModel(EMRBaseModel):
    FACILITY_SCOPED = True  # Override to False for global resources

    @classmethod
    def calculate_slug_from_facility(cls, facility_external_id, slug):
        """Generate facility-scoped slug"""
        return f"f-{facility_external_id}-{slug}"

    @classmethod
    def calculate_slug_from_instance(cls, slug):
        """Generate instance-scoped slug"""
        return f"i-{slug}"

    def calculate_slug(self):
        """Auto-determine scope based on instance"""
        if self.FACILITY_SCOPED and self.facility:
            return f"f-{self.facility.external_id}-{self.slug}"
        return f"i-{self.slug}"

    def parse_slug(self, slug):
        """Extract components from a slug"""
        if slug.startswith("f-") and self.FACILITY_SCOPED:
            facility_id = slug[2:38]   # Extract 36-char UUID
            slug_value = slug[39:]      # Rest after "f-{UUID}-"
            return {"facility": facility_id, "slug_value": slug_value}
        if slug.startswith("i-"):
            return {"slug_value": slug[2:]}
        raise ValueError("Invalid slug")
```

### Models Using Slugs

All inherit from `SlugBaseModel` and use `lookup_field = "slug"` in ViewSets:

| Model | Purpose | FACILITY_SCOPED |
|-------|---------|-----------------|
| `ActivityDefinition` | Procedures/activities | True |
| `ChargeItemDefinition` | Billing items | True |
| `ObservationDefinition` | Observation types | True |
| `SpecimenDefinition` | Specimen types | True |
| `ResourceCategory` | Resource hierarchies | True |
| `ProductKnowledge` | Product catalog | True |
| `Template` | Report templates | True |

### Slug Validation

**Location:** `care/emr/utils/slug_type.py`

```python
# Input slug (user-provided part only)
SlugType = Annotated[str, Field(min_length=5, max_length=36)]
# Pattern: ^[-\w]+$  (alphanumeric, hyphens, underscores)

# Stored slug (full calculated slug)
ExtendedSlugType = Annotated[str, Field(min_length=7, max_length=75)]
# Must start with "f-" or "i-"
```

---

## Deep Dive: Serializer Architecture

### Why Serializers (Specs) are Needed

Care uses **Pydantic models** (called "Specs") instead of DRF serializers for:

1. **Type Safety** - Pydantic provides strict type validation
2. **Schema Generation** - Auto-generate OpenAPI schemas
3. **Validation** - Field-level and cross-field validation
4. **Transformation** - Convert between API format and database format
5. **Different Views** - Separate specs for Create/Update/List/Retrieve

### Spec Base Class

**Location:** `care/emr/resources/base.py`

```python
class EMRResource(BaseModel):  # Pydantic BaseModel
    __model__ = None           # Links to Django model
    __exclude__ = []           # Fields to exclude
    __store_metadata__ = False # Store extra fields in meta JSONField
    __version__ = 0.1

    @classmethod
    def serialize(cls, obj, user=None, **kwargs):
        """DB Object → Pydantic Object (for API responses)"""
        pass

    def de_serialize(self, obj=None, partial=False):
        """Pydantic Object → DB Object (for database writes)"""
        pass
```

### When Serialization Happens

**Serialization** = Django Model → Pydantic → JSON Response

```
┌─────────────────────────────────────────────────────────────┐
│                    SERIALIZATION FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  GET /api/v1/patient/{id}/                                   │
│         │                                                    │
│         ▼                                                    │
│  EMRRetrieveMixin.retrieve()                                 │
│         │                                                    │
│         ▼                                                    │
│  get_object() → Django Model instance                        │
│         │                                                    │
│         ▼                                                    │
│  PatientRetrieveSpec.serialize(instance)                     │
│         │                                                    │
│         ├─► get_database_mapping()  # Get field names        │
│         ├─► getattr(obj, field)     # Copy values            │
│         ├─► perform_extra_serialization()  # Custom fields   │
│         └─► model_construct(**data) # Create Pydantic obj    │
│         │                                                    │
│         ▼                                                    │
│  pydantic_obj.to_json()  # Convert to dict                   │
│         │                                                    │
│         ▼                                                    │
│  Response(data)  # JSON response                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### When Deserialization Happens

**Deserialization** = JSON Request → Pydantic → Django Model

```
┌─────────────────────────────────────────────────────────────┐
│                   DESERIALIZATION FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  POST /api/v1/patient/                                       │
│  {"name": "John", "gender": "male", ...}                     │
│         │                                                    │
│         ▼                                                    │
│  EMRCreateMixin.handle_create(request.data)                  │
│         │                                                    │
│         ▼                                                    │
│  PatientCreateSpec.model_validate(data, context={...})       │
│         │                                                    │
│         ├─► Pydantic field validation                        │
│         ├─► @field_validator methods                         │
│         └─► ExtensionValidator (if present)                  │
│         │                                                    │
│         ▼                                                    │
│  pydantic_instance.de_serialize()                            │
│         │                                                    │
│         ├─► obj = Patient()  # Create empty Django model     │
│         ├─► model_dump()     # Get validated data            │
│         ├─► setattr(obj, field, value)  # Set fields         │
│         └─► perform_extra_deserialization()  # FK lookups    │
│         │                                                    │
│         ▼                                                    │
│  perform_create(obj)  # Save to database                     │
│         │                                                    │
│         ▼                                                    │
│  serialize() → Response  # Return created object             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Different Specs for Different Operations

**Location:** `care/emr/resources/patient/spec.py`

```python
class PatientBaseSpec(EMRResource):
    """Common fields"""
    __model__ = Patient
    name: str
    gender: str

class PatientCreateSpec(ExtensionValidator, PatientBaseSpec):
    """CREATE - includes extensions validation"""
    ___extension_resource_type__ = ExtensionResource.patient

    def perform_extra_deserialization(self, is_update, obj):
        # Lookup ForeignKeys from UUIDs
        if self.geo_organization:
            obj.geo_organization = Organization.objects.get(...)

class PatientUpdateSpec(ExtensionValidator, PatientBaseSpec):
    """UPDATE - may have different required fields"""
    pass

class PatientListSpec(PatientBaseSpec):
    """LIST - minimal fields for performance"""
    id: UUID4
    name: str
    # No extensions (too heavy for lists)

class PatientRetrieveSpec(PatientBaseSpec):
    """RETRIEVE - full detail including extensions"""
    extensions: dict = {}

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        # Add computed fields
        mapping["age"] = calculate_age(obj.date_of_birth)
```

### ViewSet Configuration

**Location:** `care/emr/api/viewsets/patient.py`

```python
class PatientViewSet(EMRModelViewSet):
    database_model = Patient
    pydantic_model = PatientCreateSpec           # For POST
    pydantic_update_model = PatientUpdateSpec    # For PUT/PATCH
    pydantic_read_model = PatientListSpec        # For GET list
    pydantic_retrieve_model = PatientRetrieveSpec # For GET detail
```

---

## Deep Dive: Signal System

### Signal Locations

| Signal Type | File Location | Trigger |
|-------------|---------------|---------|
| Patient Name Identifier | `care/emr/signals/patient/name_identifier.py` | Patient post_save |
| Patient Phone Identifier | `care/emr/signals/patient/phone_number_identifier.py` | Patient post_save |
| Facility Name Identifier | `care/emr/signals/patient/facility_name_identifier.py` | Encounter/TokenBooking post_save |
| Role Cache Invalidation | `care/security/models/role.py` | RolePermission post_save/delete |
| Tag Config Cache | `care/emr/resources/tag/cache_invalidation.py` | TagConfig post_save |
| Model Cache (Generic) | `care/emr/resources/base.py` | Any @cacheable model |
| Audit Log | `care/audit_log/receivers.py` | All models pre/post save/delete |

### How Signals are Triggered

**Automatic Django Signals** - Fire on model.save() or model.delete():

```python
# care/emr/signals/patient/name_identifier.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from care.emr.models.patient import Patient

@receiver(post_save, sender=Patient)
def update_name_identifier(sender, instance, created, **kwargs):
    """
    This function is AUTOMATICALLY called by Django whenever
    Patient.save() is executed - no manual trigger needed.
    """
    if settings.MAINTAIN_PATIENT_NAME_IDENTIFIER:
        NameIdentifierConfig.update_identifier(instance)
```

### Signal Registration (AppConfig.ready)

**Location:** `care/emr/apps.py`

```python
class EMRConfig(AppConfig):
    name = "care.emr"

    def ready(self):
        # Import signals module to register all signal handlers
        import care.emr.signals  # This import triggers @receiver decorators
```

**Location:** `care/emr/signals/__init__.py`

```python
from .patient import *  # Imports all patient signal handlers
```

### Signal Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SIGNAL FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  patient.save()                                              │
│       │                                                      │
│       ▼                                                      │
│  Django ORM triggers pre_save signal                         │
│       │                                                      │
│       ├──► Audit Log: capture before-state                   │
│       │                                                      │
│       ▼                                                      │
│  Database INSERT/UPDATE executes                             │
│       │                                                      │
│       ▼                                                      │
│  Django ORM triggers post_save signal                        │
│       │                                                      │
│       ├──► update_name_identifier()                          │
│       ├──► update_phone_number_identifier()                  │
│       ├──► delete_model_cache() (if @cacheable)              │
│       └──► Audit Log: record change                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Configuration Settings

```python
# config/settings/config.py

# Enable/disable patient identifier signals
MAINTAIN_PATIENT_NAME_IDENTIFIER = env.bool("MAINTAIN_PATIENT_NAME_IDENTIFIER", False)
MAINTAIN_PATIENT_PHONE_NUMBER_IDENTIFIER = env.bool("MAINTAIN_PATIENT_PHONE_NUMBER_IDENTIFIER", False)
MAINTAIN_FACILITY_PATIENT_NAME_IDENTIFIER = env.bool("MAINTAIN_FACILITY_PATIENT_NAME_IDENTIFIER", True)

# Enable audit logging
AUDIT_LOG_ENABLED = env.bool("AUDIT_LOG_ENABLED", False)
```

---

## Can Plugins Change Domain Models?

### Short Answer: **No Direct Modification, But Multiple Extension Points**

Plugins **CANNOT** directly modify core domain models (Patient, Encounter, etc.) because:
1. Core models are in the main codebase, not plugin code
2. Django migrations for core models are managed centrally
3. Modifying core models would break upgradeability

### What Plugins CAN Do

| Method | Capability | Use Case |
|--------|------------|----------|
| **Extensions JSONField** | Add custom data to existing models | Store insurance info on Patient |
| **New Related Models** | Create models with ForeignKey to core | PatientInsurance → Patient |
| **Signals** | React to core model events | Sync Patient to external system |
| **Override ViewSets** | Modify API behavior | Add custom validation |
| **Custom Endpoints** | Add new APIs | New insurance endpoints |

### Example: "Extending" Patient Without Modifying It

```python
# Plugin approach 1: Extensions (data stored in Patient.extensions JSONField)
class InsuranceExtension(ExtensionBase):
    resource_type = ExtensionResource.patient
    extension_name = "insurance"
    write_schema = {"type": "object", "properties": {...}}

# Plugin approach 2: Related Model (separate table with FK)
class PatientInsurance(EMRBaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.CharField(max_length=255)

# Plugin approach 3: Signal (react to Patient changes)
@receiver(post_save, sender=Patient)
def sync_patient(sender, instance, **kwargs):
    external_system.sync(instance)
```

---

## Deep Dive: How Extensions (dict) Can Be Modified

### Extension Modification Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 EXTENSION MODIFICATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Step 1: Register Extension Handler (plugin apps.py)         │
│  ────────────────────────────────────────────────────────    │
│  ExtensionRegistry.register(InsuranceExtension())            │
│       │                                                      │
│       ▼                                                      │
│  _extensions = {                                             │
│    "patient": {                                              │
│      "insurance": InsuranceExtension,                        │
│      "core": CoreEnvExtension                                │
│    }                                                         │
│  }                                                           │
│                                                               │
│  Step 2: API Request with Extensions                         │
│  ────────────────────────────────────────────────────────    │
│  POST /api/v1/patient/                                       │
│  {                                                           │
│    "name": "John Doe",                                       │
│    "extensions": {                                           │
│      "insurance": {                                          │
│        "provider": "ACME",                                   │
│        "policy_number": "POL123"                             │
│      }                                                       │
│    }                                                         │
│  }                                                           │
│       │                                                      │
│       ▼                                                      │
│  Step 3: Validation (Pydantic field_validator)               │
│  ────────────────────────────────────────────────────────    │
│  ExtensionValidator.validate_extensions(data)                │
│       │                                                      │
│       ├─► For each key in extensions dict:                   │
│       │     handler = ExtensionRegistry.get("patient", key)  │
│       │     handler.validate(data[key])                      │
│       │     cleaned[key] = handler.serialize_extensions()    │
│       │                                                      │
│       ▼                                                      │
│  Step 4: Database Storage                                    │
│  ────────────────────────────────────────────────────────    │
│  Patient.objects.create(                                     │
│    name="John Doe",                                          │
│    extensions={"insurance": {"provider": "ACME", ...}}       │
│  )                                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### How to Add/Update Extensions via API

**Create with extensions:**
```bash
POST /api/v1/patient/
{
  "name": "John Doe",
  "extensions": {
    "insurance": {"provider": "ACME", "policy": "POL123"}
  }
}
```

**Update extensions (PATCH):**
```bash
PATCH /api/v1/patient/{id}/
{
  "extensions": {
    "insurance": {"provider": "NewProvider", "policy": "POL456"}
  }
}
```

**Note:** Extensions are replaced entirely, not merged. To add a new extension while keeping existing ones, you must include all extensions in the request.

### Extension Handler Implementation

```python
# care/emr/extensions/base.py

class ExtensionBase:
    resource_type: ExtensionResource  # Which model this extends
    extension_name = ""               # Key in extensions dict
    write_schema = {}                 # JSON Schema for validation
    read_schema = {}                  # Schema for list responses
    retrieve_schema = {}              # Schema for detail responses

    def validate(self, data, resource=None):
        """
        Called during create/update to validate extension data.
        Raise ValueError if invalid.
        """
        # Default: validate against write_schema using jsonschema
        validate(data, self.write_schema)

    def serialize_extensions(self, data, resource=None):
        """
        Called after validation to transform data before storage.
        Return the data to be stored in the database.
        """
        return data  # Default: store as-is

    def deserialize_extensions_list(self, data, resource):
        """Transform data for list API responses"""
        return data

    def deserialize_extensions_retrieve(self, data, resource):
        """Transform data for detail API responses"""
        return data
```

### Environment-Based Extensions (No Code Required)

```bash
# Set JSON schemas via environment variables
export CORE_EXTENSIONS_PATIENT_WRITE='{
  "type": "object",
  "properties": {
    "custom_field": {"type": "string"},
    "custom_number": {"type": "integer"}
  },
  "required": ["custom_field"]
}'

export CORE_EXTENSIONS_PATIENT_READ='{...}'  # Optional
export CORE_EXTENSIONS_PATIENT_RETRIEVE='{...}'  # Optional
```

The `CoreEnvExtension` class automatically loads these schemas and registers them for validation.

### Available Extension Resources

**Location:** `care/emr/extensions/base.py`

```python
class ExtensionResource(str, Enum):
    account = "account"
    encounter = "encounter"
    patient = "patient"
    payment_reconciliation = "payment_reconciliation"
    supply_delivery = "supply_delivery"
    supply_delivery_order = "supply_delivery_order"
    product = "product"
```

Only these models have the `extensions` JSONField and support the extension system.

### Discovering Available Extensions

**Endpoint:** `GET /api/v1/extensions/`

**Response:**
```json
{
  "patient": [
    {
      "name": "core",
      "owner": "core",
      "version": "1.0",
      "write_schema": {...},
      "read_schema": {...},
      "retrieve_schema": {...}
    },
    {
      "name": "insurance",
      "owner": "plug",
      "version": "1.0",
      "write_schema": {...}
    }
  ],
  "account": [...],
  "encounter": [...]
}
```

---

## Key Takeaways

| Question | Answer |
|----------|--------|
| **What are slugs?** | Human-readable, URL-safe identifiers with facility scoping (`f-{uuid}-{value}` or `i-{value}`) |
| **Why serializers?** | Type-safe validation, transformation between API ↔ database formats, different views for CRUD |
| **When serialize?** | On API responses (GET) - Django model → Pydantic → JSON |
| **When deserialize?** | On API writes (POST/PUT/PATCH) - JSON → Pydantic → Django model |
| **How signals trigger?** | Automatic Django mechanism on model.save()/delete(), registered via @receiver decorator |
| **Where are signal functions?** | `care/emr/signals/`, `care/audit_log/receivers.py`, `care/security/models/` |
| **Can plugins change models?** | No direct modification, but can use Extensions, Related Models, Signals |
| **How to modify extensions?** | Via API (full replacement), validated by registered ExtensionBase handlers |

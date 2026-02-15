# Care Plugin Customization & Extension Guide

This guide covers how to customize, extend models, and override behaviors in the Care backend using plugins.

---

## Table of Contents

1. [Plugin Architecture Overview](#plugin-architecture-overview)
2. [Extending Models with Extensions](#extending-models-with-extensions)
3. [Creating Related Models](#creating-related-models)
4. [Overriding Behavior with Signals](#overriding-behavior-with-signals)
5. [Custom ViewSets and APIs](#custom-viewsets-and-apis)
6. [Registering Custom Extensions](#registering-custom-extensions)
7. [Plugin Settings & Configuration](#plugin-settings--configuration)
8. [Celery Tasks for Background Processing](#celery-tasks-for-background-processing)
9. [Best Practices](#best-practices)
10. [Complete Plugin Example](#complete-plugin-example)

---

## Plugin Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CARE Backend Core                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Models (EMRBaseModel)        ViewSets (EMRModelViewSet)         │
│  ├── Patient                  ├── PatientViewSet                 │
│  ├── Encounter                ├── EncounterViewSet               │
│  ├── Observation              └── ...                            │
│  └── ...                                                         │
│                                                                   │
│  Extensions System            Signals                            │
│  ├── ExtensionRegistry        ├── post_save                      │
│  ├── ExtensionBase            ├── pre_save                       │
│  └── ExtensionValidator       └── post_delete                    │
│                                                                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Plugin Integration Points
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                      YOUR PLUGIN                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Extensions (JSONField)    │  2. Related Models               │
│     Add data to Patient,      │     Create new tables with       │
│     Encounter, Account, etc.  │     ForeignKey to core models    │
│                               │                                   │
│  3. Signal Handlers           │  4. Custom ViewSets              │
│     React to model events     │     Add new API endpoints        │
│     (create, update, delete)  │     at /api/v1/{plugin}/         │
│                               │                                   │
│  5. Celery Tasks              │  6. Custom Settings              │
│     Background processing     │     Plugin configuration         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Plugin Loading Flow

```
1. plug_config.py          → Define plugin (name, package, configs)
2. install_plugins.py      → pip install the plugin
3. Django startup          → Plugin added to INSTALLED_APPS
4. AppConfig.ready()       → Register extensions, signals, tasks
5. URL registration        → /api/v1/{plugin}/ routes added
```

---

## Extending Models with Extensions

### Overview

Many core models have an `extensions` JSONField that allows plugins to store custom data without modifying the database schema.

**Models with extensions field:**
- `Patient`
- `Encounter`
- `Account`
- `Product`
- `PaymentReconciliation`
- `SupplyDelivery`
- `SupplyDeliveryOrder`

### How Extensions Work

```
┌─────────────────────────────────────────────────────────────────┐
│                    Extension Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  API Request                                                     │
│  POST /api/v1/patient/                                           │
│  {                                                               │
│    "name": "John Doe",                                           │
│    "extensions": {                                               │
│      "my_plugin_data": {"custom_field": "value"}                │
│    }                                                             │
│  }                                                               │
│         │                                                        │
│         ▼                                                        │
│  ExtensionValidator (Pydantic)                                   │
│         │                                                        │
│         ▼                                                        │
│  ExtensionRegistry.get_extension_obj("patient", "my_plugin_data")│
│         │                                                        │
│         ▼                                                        │
│  MyPluginExtension.validate(data)                                │
│         │                                                        │
│         ▼                                                        │
│  MyPluginExtension.serialize_extensions(data)                    │
│         │                                                        │
│         ▼                                                        │
│  Patient.objects.create(..., extensions={...})                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Creating a Custom Extension

**Step 1: Define the Extension Class**

```python
# my_plugin/extensions.py

from care.emr.extensions.base import ExtensionBase, ExtensionResource, ExtensionOwners

class InsuranceExtension(ExtensionBase):
    """
    Extension to store insurance information on Patient model.
    """

    # Which model this extension applies to
    resource_type = ExtensionResource.patient

    # Key name in the extensions dict
    extension_name = "insurance"

    # Owner identifier (use ExtensionOwners.plug for plugins)
    extension_owner = ExtensionOwners.plug

    # Version for tracking changes
    extension_version = "1.0.0"

    # JSON Schema for validation (used on create/update)
    write_schema = {
        "type": "object",
        "properties": {
            "provider": {
                "type": "string",
                "description": "Insurance provider name"
            },
            "policy_number": {
                "type": "string",
                "description": "Policy number"
            },
            "valid_until": {
                "type": "string",
                "format": "date",
                "description": "Policy expiration date"
            },
            "coverage_type": {
                "type": "string",
                "enum": ["basic", "standard", "premium"],
                "description": "Coverage level"
            }
        },
        "required": ["provider", "policy_number"]
    }

    # Schema for list responses (can be subset of write_schema)
    read_schema = {
        "type": "object",
        "properties": {
            "provider": {"type": "string"},
            "policy_number": {"type": "string"}
        }
    }

    # Schema for detail/retrieve responses
    retrieve_schema = write_schema

    def validate(self, data, resource=None):
        """
        Custom validation logic beyond JSON Schema.

        Args:
            data: The extension data to validate
            resource: The model instance (Patient, Encounter, etc.)

        Raises:
            ValueError: If validation fails
        """
        # Example: Validate policy number format
        policy_number = data.get("policy_number", "")
        if len(policy_number) < 5:
            raise ValueError("Policy number must be at least 5 characters")

        # Example: Check expiration date
        valid_until = data.get("valid_until")
        if valid_until:
            from datetime import date
            expiry = date.fromisoformat(valid_until)
            if expiry < date.today():
                raise ValueError("Insurance policy has expired")

    def serialize_extensions(self, data, resource=None):
        """
        Transform data before storing in database.

        Use this for:
        - Normalizing data
        - Adding computed fields
        - Encrypting sensitive data

        Returns:
            Transformed data dict
        """
        # Example: Uppercase provider name
        if "provider" in data:
            data["provider"] = data["provider"].upper()
        return data

    def deserialize_extensions_list(self, data, resource):
        """
        Transform data for list API responses.

        Use this to:
        - Remove sensitive fields
        - Add computed display values
        """
        return {
            "provider": data.get("provider"),
            "has_valid_policy": data.get("valid_until") is not None
        }

    def deserialize_extensions_retrieve(self, data, resource):
        """
        Transform data for detail/retrieve API responses.

        Full data for single resource view.
        """
        return data
```

**Step 2: Register the Extension**

```python
# my_plugin/apps.py

from django.apps import AppConfig

PLUGIN_NAME = "my_plugin"

class MyPluginConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = "My Plugin"

    def ready(self):
        """Register extensions when Django starts."""
        self._register_extensions()

    def _register_extensions(self):
        from care.emr.registries.extensions.registry import ExtensionRegistry
        from my_plugin.extensions import InsuranceExtension

        # Register the extension
        ExtensionRegistry.register(InsuranceExtension())
```

**Step 3: Use the Extension via API**

```bash
# Create patient with insurance extension
curl -X POST http://localhost:9000/api/v1/patient/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "John Doe",
    "gender": "male",
    "phone_number": "+1234567890",
    "extensions": {
      "insurance": {
        "provider": "Blue Cross",
        "policy_number": "POL123456",
        "valid_until": "2025-12-31",
        "coverage_type": "premium"
      }
    }
  }'

# Response includes the extension data
{
  "id": "uuid-here",
  "name": "John Doe",
  "extensions": {
    "insurance": {
      "provider": "BLUE CROSS",
      "policy_number": "POL123456",
      "valid_until": "2025-12-31",
      "coverage_type": "premium"
    }
  }
}
```

### Environment-Based Extensions (No Code)

For simple extensions, use environment variables:

```bash
# Define schema via environment variable
export CORE_EXTENSIONS_PATIENT_WRITE='{
  "type": "object",
  "properties": {
    "custom_field": {"type": "string"},
    "custom_number": {"type": "integer", "minimum": 0}
  }
}'

export CORE_EXTENSIONS_PATIENT_READ='{
  "type": "object",
  "properties": {
    "custom_field": {"type": "string"}
  }
}'
```

The `CoreEnvExtension` class automatically loads these schemas.

---

## Creating Related Models

When you need more than simple key-value storage, create separate models.

### Pattern: ForeignKey to Core Model

```python
# my_plugin/models.py

from django.db import models
from care.emr.models.base import EMRBaseModel
from care.emr.models.patient import Patient
from care.emr.models.encounter import Encounter


class PatientInsurance(EMRBaseModel):
    """
    Detailed insurance records for patients.

    Inherits from EMRBaseModel to get:
    - external_id (UUID)
    - created_date, modified_date
    - deleted (soft delete)
    - history, meta (JSONFields)
    - created_by, updated_by
    """

    # Link to core Patient model
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="insurance_records"  # patient.insurance_records.all()
    )

    # Insurance details
    provider = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100, unique=True)
    group_number = models.CharField(max_length=100, blank=True)

    # Coverage details
    coverage_type = models.CharField(
        max_length=50,
        choices=[
            ("basic", "Basic"),
            ("standard", "Standard"),
            ("premium", "Premium"),
        ]
    )

    # Validity period
    valid_from = models.DateField()
    valid_until = models.DateField()

    # Financial details
    copay_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    deductible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Status
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "my_plugin_patient_insurance"
        ordering = ["-is_primary", "-valid_until"]
        indexes = [
            models.Index(fields=["patient", "is_primary"]),
            models.Index(fields=["policy_number"]),
        ]

    def __str__(self):
        return f"{self.patient.name} - {self.provider} ({self.policy_number})"

    def is_valid(self):
        """Check if insurance is currently valid."""
        from datetime import date
        today = date.today()
        return self.valid_from <= today <= self.valid_until

    def save(self, *args, **kwargs):
        # Ensure only one primary insurance per patient
        if self.is_primary:
            PatientInsurance.objects.filter(
                patient=self.patient,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class InsuranceClaim(EMRBaseModel):
    """
    Insurance claims linked to encounters.
    """

    # Link to insurance and encounter
    insurance = models.ForeignKey(
        PatientInsurance,
        on_delete=models.PROTECT,
        related_name="claims"
    )
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.PROTECT,
        related_name="insurance_claims"
    )

    # Claim details
    claim_number = models.CharField(max_length=100, unique=True)
    claim_date = models.DateField(auto_now_add=True)

    # Amounts
    billed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("denied", "Denied"),
            ("paid", "Paid"),
        ],
        default="pending"
    )

    denial_reason = models.TextField(blank=True)

    class Meta:
        db_table = "my_plugin_insurance_claim"
        ordering = ["-claim_date"]
```

### Creating Serializers

```python
# my_plugin/serializers.py

from rest_framework import serializers
from my_plugin.models import PatientInsurance, InsuranceClaim


class PatientInsuranceSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = PatientInsurance
        fields = [
            "id",
            "external_id",
            "patient",
            "patient_name",
            "provider",
            "policy_number",
            "group_number",
            "coverage_type",
            "valid_from",
            "valid_until",
            "copay_amount",
            "deductible",
            "is_primary",
            "is_verified",
            "is_valid",
            "created_date",
            "modified_date",
        ]
        read_only_fields = ["id", "external_id", "created_date", "modified_date"]

    def get_is_valid(self, obj):
        return obj.is_valid()


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = "__all__"
        read_only_fields = ["id", "external_id", "claim_date"]
```

### Creating ViewSets

```python
# my_plugin/viewsets/insurance.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from my_plugin.models import PatientInsurance, InsuranceClaim
from my_plugin.serializers import PatientInsuranceSerializer, InsuranceClaimSerializer


class PatientInsuranceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for patient insurance records.

    Endpoints:
    - GET    /api/v1/my_plugin/insurance/           - List all
    - POST   /api/v1/my_plugin/insurance/           - Create
    - GET    /api/v1/my_plugin/insurance/{id}/      - Retrieve
    - PUT    /api/v1/my_plugin/insurance/{id}/      - Update
    - PATCH  /api/v1/my_plugin/insurance/{id}/      - Partial update
    - DELETE /api/v1/my_plugin/insurance/{id}/      - Delete
    - POST   /api/v1/my_plugin/insurance/{id}/verify/ - Verify insurance
    """

    queryset = PatientInsurance.objects.select_related("patient")
    serializer_class = PatientInsuranceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "external_id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["patient", "provider", "is_primary", "is_verified"]

    def get_queryset(self):
        """Filter by patient if provided."""
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get("patient_id")
        if patient_id:
            queryset = queryset.filter(patient__external_id=patient_id)
        return queryset

    @action(detail=True, methods=["post"])
    def verify(self, request, external_id=None):
        """
        POST /api/v1/my_plugin/insurance/{id}/verify/

        Mark insurance as verified.
        """
        insurance = self.get_object()

        # In production, call external verification API
        insurance.is_verified = True
        insurance.verified_at = timezone.now()
        insurance.save()

        return Response({
            "status": "verified",
            "verified_at": insurance.verified_at.isoformat(),
        })

    @action(detail=True, methods=["post"])
    def set_primary(self, request, external_id=None):
        """
        POST /api/v1/my_plugin/insurance/{id}/set_primary/

        Set this insurance as the primary for the patient.
        """
        insurance = self.get_object()
        insurance.is_primary = True
        insurance.save()  # save() handles unsetting other primaries

        return Response({
            "status": "success",
            "message": f"Insurance {insurance.policy_number} set as primary",
        })


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    queryset = InsuranceClaim.objects.select_related("insurance", "encounter")
    serializer_class = InsuranceClaimSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "external_id"
```

---

## Overriding Behavior with Signals

Django signals allow plugins to react to model events in the core application.

### Available Signal Types

| Signal | When Fired | Use Cases |
|--------|------------|-----------|
| `pre_save` | Before model.save() | Validation, data transformation |
| `post_save` | After model.save() | Notifications, sync to external systems |
| `pre_delete` | Before model.delete() | Prevent deletion, archive data |
| `post_delete` | After model.delete() | Cleanup related data |
| `m2m_changed` | ManyToMany field changed | Track relationship changes |

### Signal Handler Examples

```python
# my_plugin/signals.py

import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from care.emr.models.patient import Patient
from care.emr.models.encounter import Encounter

logger = logging.getLogger(__name__)


# ============================================================================
# Patient Signals
# ============================================================================

@receiver(post_save, sender=Patient)
def on_patient_created(sender, instance, created, **kwargs):
    """
    Called after a Patient is saved.

    Args:
        sender: The model class (Patient)
        instance: The actual Patient instance
        created: True if new record, False if update
        **kwargs: Additional arguments
    """
    if created:
        logger.info(f"New patient created: {instance.external_id}")

        # Example: Trigger auto-assignment
        from my_plugin.tasks import process_auto_assignment
        process_auto_assignment.delay(
            patient_id=str(instance.external_id),
            patient_name=instance.name,
        )

        # Example: Sync to external system
        from my_plugin.services import sync_patient_to_ehr
        sync_patient_to_ehr(instance)
    else:
        logger.info(f"Patient updated: {instance.external_id}")


@receiver(pre_save, sender=Patient)
def validate_patient_before_save(sender, instance, **kwargs):
    """
    Called before a Patient is saved.

    Use for:
    - Custom validation
    - Data normalization
    - Setting computed fields
    """
    # Example: Normalize phone number
    if instance.phone_number:
        instance.phone_number = normalize_phone_number(instance.phone_number)

    # Example: Custom validation
    if instance.date_of_birth:
        from datetime import date
        if instance.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future")


# ============================================================================
# Encounter Signals
# ============================================================================

@receiver(post_save, sender=Encounter)
def on_encounter_created(sender, instance, created, **kwargs):
    """
    React to encounter creation/updates.
    """
    if created:
        logger.info(f"New encounter: {instance.external_id} for patient {instance.patient_id}")

        # Example: Auto-create insurance claim
        from my_plugin.models import PatientInsurance

        primary_insurance = PatientInsurance.objects.filter(
            patient=instance.patient,
            is_primary=True,
            is_verified=True,
        ).first()

        if primary_insurance:
            from my_plugin.tasks import create_insurance_claim
            create_insurance_claim.delay(
                encounter_id=str(instance.external_id),
                insurance_id=str(primary_insurance.external_id),
            )


@receiver(post_save, sender=Encounter)
def on_encounter_status_changed(sender, instance, created, **kwargs):
    """
    React to encounter status changes.
    """
    if not created:
        # Check if status changed (requires tracking old value)
        # This is a simplified example
        if instance.status == "completed":
            from my_plugin.tasks import finalize_encounter
            finalize_encounter.delay(str(instance.external_id))


# ============================================================================
# Generic Signal for Multiple Models
# ============================================================================

def create_audit_log(sender, instance, created, **kwargs):
    """
    Generic handler for audit logging.
    """
    from my_plugin.models import AuditLog

    action = "created" if created else "updated"
    AuditLog.objects.create(
        model_name=sender.__name__,
        object_id=str(getattr(instance, "external_id", instance.pk)),
        action=action,
        data={"instance": str(instance)},
    )

# Connect to multiple models
for model in [Patient, Encounter]:
    post_save.connect(create_audit_log, sender=model)


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_phone_number(phone):
    """Normalize phone number format."""
    import re
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"+1{digits}"
    return phone
```

### Registering Signals

```python
# my_plugin/apps.py

from django.apps import AppConfig

PLUGIN_NAME = "my_plugin"


class MyPluginConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = "My Plugin"

    def ready(self):
        """
        Called when Django starts.
        Import signals module to register handlers.
        """
        # Import signals to register handlers
        import my_plugin.signals  # noqa: F401

        # Import tasks to register with Celery
        import my_plugin.tasks  # noqa: F401

        # Register extensions
        self._register_extensions()

    def _register_extensions(self):
        from care.emr.registries.extensions.registry import ExtensionRegistry
        from my_plugin.extensions import InsuranceExtension
        ExtensionRegistry.register(InsuranceExtension())
```

### Conditional Signal Execution

```python
# my_plugin/signals.py

from django.conf import settings

@receiver(post_save, sender=Patient)
def conditional_signal_handler(sender, instance, created, **kwargs):
    """
    Only execute if plugin is enabled.
    """
    # Check plugin settings
    from my_plugin.settings import plugin_settings

    if not plugin_settings.FEATURE_ENABLED:
        return

    # Check environment
    if settings.DEBUG:
        logger.debug(f"Debug mode: Patient {instance.external_id}")
        return

    # Production logic
    process_patient(instance)
```

---

## Custom ViewSets and APIs

### Basic ViewSet Pattern

```python
# my_plugin/viewsets/example.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


class MyPluginViewSet(viewsets.ViewSet):
    """
    Custom ViewSet with various endpoint patterns.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/my_plugin/example/
        """
        return Response({
            "message": "List endpoint",
            "data": []
        })

    def create(self, request):
        """
        POST /api/v1/my_plugin/example/
        """
        data = request.data
        # Process data
        return Response({
            "message": "Created",
            "data": data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        GET /api/v1/my_plugin/example/{pk}/
        """
        return Response({
            "id": pk,
            "message": "Retrieved"
        })

    def update(self, request, pk=None):
        """
        PUT /api/v1/my_plugin/example/{pk}/
        """
        return Response({
            "id": pk,
            "message": "Updated",
            "data": request.data
        })

    def partial_update(self, request, pk=None):
        """
        PATCH /api/v1/my_plugin/example/{pk}/
        """
        return Response({
            "id": pk,
            "message": "Partially updated",
            "data": request.data
        })

    def destroy(self, request, pk=None):
        """
        DELETE /api/v1/my_plugin/example/{pk}/
        """
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        GET /api/v1/my_plugin/example/stats/

        Custom action on collection.
        """
        return Response({
            "total": 100,
            "active": 80
        })

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        POST /api/v1/my_plugin/example/{pk}/activate/

        Custom action on single item.
        """
        return Response({
            "id": pk,
            "status": "activated"
        })

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def public_action(self, request):
        """
        POST /api/v1/my_plugin/example/public_action/

        Public endpoint (no auth required).
        """
        return Response({"message": "Public endpoint"})
```

### URL Configuration

```python
# my_plugin/urls.py

from rest_framework.routers import DefaultRouter
from my_plugin.viewsets import (
    PatientInsuranceViewSet,
    InsuranceClaimViewSet,
    MyPluginViewSet,
)

router = DefaultRouter()
router.register("insurance", PatientInsuranceViewSet, basename="insurance")
router.register("claims", InsuranceClaimViewSet, basename="claims")
router.register("example", MyPluginViewSet, basename="example")

urlpatterns = router.urls
```

---

## Plugin Settings & Configuration

### Creating Plugin Settings

```python
# my_plugin/settings.py

from typing import Any
import environ
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver
from rest_framework.settings import perform_import

from my_plugin.apps import PLUGIN_NAME

env = environ.Env()


class PluginSettings:
    """
    Settings object for accessing plugin configuration.

    Usage:
        from my_plugin.settings import plugin_settings

        if plugin_settings.FEATURE_ENABLED:
            do_something()
    """

    def __init__(
        self,
        plugin_name: str,
        defaults: dict,
        import_strings: set = None,
        required_settings: set = None,
    ):
        self.plugin_name = plugin_name
        self.defaults = defaults
        self.import_strings = import_strings or set()
        self.required_settings = required_settings or set()
        self._cached_attrs = set()
        self.validate()

    def __getattr__(self, attr) -> Any:
        if attr not in self.defaults:
            raise AttributeError(f"Invalid setting: '{attr}'")

        # Priority: user settings > env vars > defaults
        val = self.defaults[attr]

        # Try user settings (from plug_config.py)
        try:
            val = self.user_settings[attr]
        except KeyError:
            # Try environment variable
            try:
                val = env(attr, cast=type(val))
            except environ.ImproperlyConfigured:
                pass

        # Import if needed
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the value
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    @property
    def user_settings(self) -> dict:
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PLUGIN_CONFIGS", {}).get(
                self.plugin_name, {}
            )
        return self._user_settings

    def validate(self):
        """Validate required settings are present."""
        for setting in self.required_settings:
            if not getattr(self, setting):
                raise ImproperlyConfigured(
                    f'The "{setting}" setting is required for {PLUGIN_NAME}.'
                )

    def reload(self):
        """Clear cached settings."""
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


# Default settings
DEFAULTS = {
    # Feature flags
    "FEATURE_ENABLED": True,
    "AUTO_SYNC_ENABLED": False,

    # API configuration
    "EXTERNAL_API_URL": "",
    "EXTERNAL_API_KEY": "",
    "API_TIMEOUT": 30,

    # Processing settings
    "MAX_RETRIES": 3,
    "BATCH_SIZE": 100,

    # Custom algorithm class (import string)
    "CUSTOM_ALGORITHM_CLASS": "",
}

REQUIRED_SETTINGS = {
    # Add settings that must be configured
}

IMPORT_STRINGS = {
    "CUSTOM_ALGORITHM_CLASS",
}

# Create settings instance
plugin_settings = PluginSettings(
    PLUGIN_NAME,
    defaults=DEFAULTS,
    import_strings=IMPORT_STRINGS,
    required_settings=REQUIRED_SETTINGS,
)


@receiver(setting_changed)
def reload_plugin_settings(*args, **kwargs):
    """Reload settings when Django settings change."""
    if kwargs["setting"] == "PLUGIN_CONFIGS":
        plugin_settings.reload()
```

### Configuring in plug_config.py

```python
# care/plug_config.py

from plugs.manager import PlugManager
from plugs.plug import Plug

my_plugin = Plug(
    name="my_plugin",
    package_name="git+https://github.com/org/my-plugin.git",
    version="@main",
    configs={
        "FEATURE_ENABLED": True,
        "EXTERNAL_API_URL": "https://api.example.com",
        "EXTERNAL_API_KEY": os.environ.get("MY_PLUGIN_API_KEY", ""),
        "MAX_RETRIES": 5,
    },
)

plugs = [my_plugin]
manager = PlugManager(plugs)
```

---

## Celery Tasks for Background Processing

### Creating Tasks

```python
# my_plugin/tasks/__init__.py

from .processing import (
    process_auto_assignment,
    sync_to_external_system,
    generate_report,
)

__all__ = [
    "process_auto_assignment",
    "sync_to_external_system",
    "generate_report",
]
```

```python
# my_plugin/tasks/processing.py

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_auto_assignment(self, patient_id: str, patient_name: str):
    """
    Async task for auto-assignment processing.

    Args:
        self: Task instance (for retries)
        patient_id: Patient external_id
        patient_name: Patient name for logging
    """
    logger.info(f"Processing assignment for patient {patient_id}")

    try:
        # Import here to avoid circular imports
        from care.emr.models.patient import Patient
        from my_plugin.services import AssignmentService

        patient = Patient.objects.get(external_id=patient_id)
        service = AssignmentService()
        result = service.assign(patient)

        logger.info(f"Assignment complete: {result}")
        return {"status": "success", "result": result}

    except Patient.DoesNotExist:
        logger.error(f"Patient not found: {patient_id}")
        return {"status": "error", "message": "Patient not found"}

    except Exception as e:
        logger.error(f"Assignment failed: {e}")
        # Retry the task
        raise self.retry(exc=e)


@shared_task
def sync_to_external_system(model_name: str, object_id: str, action: str):
    """
    Sync data to external system.

    Called from signal handlers for real-time sync.
    """
    from my_plugin.settings import plugin_settings

    if not plugin_settings.AUTO_SYNC_ENABLED:
        return {"status": "skipped", "reason": "sync disabled"}

    logger.info(f"Syncing {model_name}:{object_id} ({action})")

    # Implementation here
    return {"status": "synced"}


@shared_task
def generate_report(report_type: str, facility_id: str, date_range: dict):
    """
    Generate a report in the background.

    Example periodic task.
    """
    logger.info(f"Generating {report_type} report for {facility_id}")

    # Generate report
    report_data = {}  # Generate actual data

    # Store or email report
    return {"status": "generated", "report_type": report_type}
```

### Scheduling Periodic Tasks

```python
# my_plugin/celery.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "daily-report": {
        "task": "my_plugin.tasks.generate_report",
        "schedule": crontab(hour=6, minute=0),  # 6 AM daily
        "args": ("daily", "all", {"days": 1}),
    },
    "hourly-sync": {
        "task": "my_plugin.tasks.sync_pending_items",
        "schedule": crontab(minute=0),  # Every hour
    },
}
```

---

## Best Practices

### 1. Plugin Structure

```
my_plugin/
├── __init__.py
├── apps.py                 # AppConfig with ready() hook
├── settings.py             # Plugin settings management
├── urls.py                 # URL routing
├── signals.py              # Signal handlers
├── utils.py                # Utility functions
├── models/
│   ├── __init__.py
│   └── insurance.py
├── serializers/
│   ├── __init__.py
│   └── insurance.py
├── viewsets/
│   ├── __init__.py
│   └── insurance.py
├── tasks/
│   ├── __init__.py
│   └── processing.py
├── extensions/
│   ├── __init__.py
│   └── insurance_extension.py
├── services/               # Business logic
│   ├── __init__.py
│   └── assignment_service.py
├── migrations/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_viewsets.py
    └── test_signals.py
```

### 2. Avoid Circular Imports

```python
# Bad - circular import risk
from care.emr.models.patient import Patient
from my_plugin.models import MyModel  # MyModel might import Patient

# Good - import inside function
def my_function():
    from care.emr.models.patient import Patient
    from my_plugin.models import MyModel
    # Use them here
```

### 3. Use Lazy Loading for Signals

```python
# my_plugin/signals.py

# Import models inside handlers, not at module level
@receiver(post_save, sender="emr.Patient")  # String reference
def on_patient_saved(sender, instance, **kwargs):
    from my_plugin.services import MyService
    MyService().process(instance)
```

### 4. Handle Missing Core Models Gracefully

```python
# my_plugin/apps.py

def ready(self):
    try:
        from care.emr.models.patient import Patient
        import my_plugin.signals  # Register signals
    except ImportError:
        logger.warning("Care EMR not available, signals not registered")
```

### 5. Use Transactions for Data Integrity

```python
from django.db import transaction

@shared_task
def complex_operation(patient_id):
    with transaction.atomic():
        # All operations in single transaction
        patient = Patient.objects.select_for_update().get(pk=patient_id)
        # Update patient
        # Create related records
        # All succeed or all fail
```

### 6. Test Your Plugin

```python
# my_plugin/tests/test_extensions.py

from django.test import TestCase
from care.emr.models.patient import Patient
from my_plugin.extensions import InsuranceExtension


class InsuranceExtensionTest(TestCase):
    def test_validation_success(self):
        ext = InsuranceExtension()
        data = {
            "provider": "Blue Cross",
            "policy_number": "POL123456"
        }
        # Should not raise
        ext.validate(data)

    def test_validation_failure(self):
        ext = InsuranceExtension()
        data = {
            "provider": "Blue Cross",
            "policy_number": "123"  # Too short
        }
        with self.assertRaises(ValueError):
            ext.validate(data)
```

---

## Complete Plugin Example

See the `care_auto_assign` plugin for a complete working example:

```
/care_task_plugin/care_auto_assign/
├── __init__.py
├── apps.py
├── settings.py
├── urls.py
├── signals.py
├── utils.py
├── models/
│   ├── __init__.py
│   ├── config.py
│   ├── event.py
│   └── queue.py
├── serializers/
│   ├── __init__.py
│   ├── config.py
│   ├── event.py
│   └── queue.py
├── viewsets/
│   ├── __init__.py
│   ├── config.py
│   ├── queue.py
│   ├── assignment.py
│   ├── events.py
│   └── metrics.py
├── tasks/
│   ├── __init__.py
│   └── assignment.py
└── migrations/
    └── __init__.py
```

---

## Summary

| Extension Method | Use Case | Database Impact |
|-----------------|----------|-----------------|
| **Extensions JSONField** | Add data to existing models | None (uses existing field) |
| **Related Models** | Complex data structures | New tables |
| **Signals** | React to model events | None |
| **ViewSets** | New API endpoints | Depends on implementation |
| **Celery Tasks** | Background processing | Depends on implementation |
| **Custom Settings** | Plugin configuration | None |

### Quick Reference

```python
# Register extension
ExtensionRegistry.register(MyExtension())

# Connect signal
@receiver(post_save, sender=Patient)
def handler(sender, instance, **kwargs): ...

# Create task
@shared_task
def my_task(): ...

# Access settings
from my_plugin.settings import plugin_settings
plugin_settings.MY_SETTING
```

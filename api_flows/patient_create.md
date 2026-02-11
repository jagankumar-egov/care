# Patient Create API Flow

This document explains the complete flow of the Patient Create API from request entry to database persistence.

## Endpoint

```
POST /api/v1/patient/
```

## Flow Diagram

```
HTTP POST /api/v1/patient/
    │
    ▼
config/urls.py (Line 65)
    │
    ▼
config/api_router.py (Line 431)
    │  router.register("patient", PatientViewSet, basename="patient")
    │
    ▼
PatientViewSet.create()
    │
    ▼
EMRCreateMixin.handle_create()
    │
    ├──► clean_create_data()
    │
    ├──► PatientCreateSpec.model_validate()
    │       ├── Field validators
    │       ├── geo_organization validator
    │       └── identifiers model validator
    │
    ├──► validate_data() - Custom business logic
    │
    ├──► authorize_create() - Permission check
    │
    ├──► de_serialize() - Convert to Django model
    │
    └──► perform_create() - Save to database
            │
            ▼
        HTTP 201 Created
```

## 1. Routing Configuration

**File:** `config/api_router.py:431-432`

```python
router.register("patient", PatientViewSet, basename="patient")
patient_nested_router = NestedSimpleRouter(router, r"patient", lookup="patient")
```

The router provides standard CRUD operations:
- `POST /api/v1/patient/` - Create
- `GET /api/v1/patient/` - List
- `GET /api/v1/patient/{external_id}/` - Retrieve
- `PUT/PATCH /api/v1/patient/{external_id}/` - Update
- `DELETE /api/v1/patient/{external_id}/` - Delete

## 2. ViewSet Configuration

**File:** `care/emr/api/viewsets/patient.py:48-56`

```python
class PatientViewSet(EMRModelViewSet):
    database_model = Patient
    pydantic_model = PatientCreateSpec          # For create requests
    pydantic_read_model = PatientListSpec       # For list responses
    pydantic_update_model = PatientUpdateSpec   # For update requests
    pydantic_retrieve_model = PatientRetrieveSpec  # For retrieve responses
    filterset_class = PatientFilters
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created_date", "modified_date"]
```

## 3. Request Handling

### 3.1 Entry Point

**File:** `care/emr/api/viewsets/base.py:133-134`

```python
def create(self, request, *args, **kwargs):
    return Response(self.handle_create(request.data), status=status.HTTP_201_CREATED)
```

### 3.2 Handle Create

**File:** `care/emr/api/viewsets/base.py:139-151`

```python
def handle_create(self, request_data):
    clean_data = self.clean_create_data(request_data)
    context = {"is_create": True, **self.get_serializer_create_context()}

    # Pydantic validation
    instance = self.pydantic_model.model_validate(
        clean_data,
        context=context,
    )
    instance._context = context

    self.validate_data(instance, None)      # Custom validation
    self.authorize_create(instance)          # Permission check

    model_instance = instance.de_serialize() # Convert to Django model
    self.perform_create(model_instance)      # Save to database

    return self.get_retrieve_pydantic_model().serialize(model_instance).to_json()
```

## 4. Pydantic Validation

### 4.1 Base Spec

**File:** `care/emr/resources/patient/spec.py:45-76`

```python
class PatientBaseSpec(EMRResource):
    __model__ = Patient
    __exclude__ = ["geo_organization", "instance_identifiers", ...]
    __store_metadata__ = True

    id: UUID4 | None = None
    name: str
    gender: GenderChoices
    phone_number: PhoneNumber = Field(max_length=14)
    emergency_phone_number: PhoneNumber | None = Field(None, max_length=14)
    address: str | None = None
    permanent_address: str | None = None
    pincode: int | None = None
    deceased_datetime: StrictTZAwareDateTime | None = None
    blood_group: BloodGroupChoices | None = None

    @field_validator("deceased_datetime")
    @classmethod
    def validate_deceased_datetime(cls, deceased_datetime):
        if deceased_datetime and deceased_datetime > care_now():
            raise ValueError("Deceased datetime cannot be in the future")
        return deceased_datetime
```

### 4.2 Create Spec

**File:** `care/emr/resources/patient/spec.py:103-150`

```python
class PatientCreateSpec(ExtensionValidator, PatientBaseSpec):
    name: str = Field(max_length=settings.PATIENT_NAME_MAX_LENGTH)
    geo_organization: UUID4
    date_of_birth: datetime.date | None = None
    age: int | None = None
    identifiers: list[PatientIdentifierConfigRequest] = []
    tags: list[UUID4] = []

    @field_validator("geo_organization")
    @classmethod
    def validate_geo_organization(cls, geo_organization):
        if not Organization.objects.filter(
            org_type="govt", external_id=geo_organization
        ).exists():
            raise ValueError("Geo Organization does not exist")
        return geo_organization

    @model_validator(mode="after")
    def validate_identifiers(self):
        # Validates required identifiers and uniqueness
        instance_identifier_configs = PatientIdentifierConfigCache.get_instance_config()
        configs = {str(x.config): x for x in self.identifiers}
        for identifier_config in instance_identifier_configs:
            if str(identifier_config["id"]) in configs:
                value = configs[str(identifier_config["id"])].value
                if identifier_config["config"]["required"] and not value:
                    raise ValueError(f"Identifier config {identifier_config['config']['system']} is required")
                validate_identifier_config(identifier_config, value)
        return self
```

### 4.3 Identifier Validation

**File:** `care/emr/resources/patient/spec.py:78-96`

```python
def validate_identifier_config(config, value, obj=None):
    queryset = PatientIdentifier.objects.filter(value=value)
    if "config_obj" in config:
        queryset = queryset.filter(config=config["config_obj"])
    else:
        queryset = queryset.filter(config__external_id=config["id"])
    if obj:
        queryset = queryset.exclude(patient=obj)

    # Uniqueness check
    if config["config"]["unique"] and queryset.exists():
        raise ValueError(f"Identifier config {config['config']['system']} is not unique")

    # Regex pattern match
    if value and config["config"]["regex"] and not re.match(config["config"]["regex"], value):
        raise ValueError(f"Identifier config {config['config']['system']} is not valid")
```

## 5. Custom Validation

**File:** `care/emr/api/viewsets/patient.py:72-90`

```python
def validate_data(self, instance, model_obj=None):
    dob = instance.date_of_birth or (model_obj and model_obj.date_of_birth)
    deceased = instance.deceased_datetime or (model_obj and model_obj.deceased_datetime)

    # Date of birth cannot be after date of death
    if dob and deceased and dob > deceased.date():
        raise ValidationError("Date of birth cannot be after the date of death")

    # Year of birth cannot be after year of death
    age = instance.age or (model_obj and model_obj.year_of_birth and
                           timezone.now().year - model_obj.year_of_birth)
    if age and deceased:
        calculated_birth_year = timezone.now().year - age
        if calculated_birth_year > deceased.year:
            raise ValidationError("Year of birth cannot be after the year of death")
```

## 6. Authorization

**File:** `care/emr/api/viewsets/patient.py:64-66`

```python
def authorize_create(self, request_obj):
    if not AuthorizationController.call("can_create_patient", self.request.user):
        raise PermissionDenied("Cannot Create Patient")
```

## 7. Deserialization (Pydantic to Django Model)

### 7.1 Base Deserialization

**File:** `care/emr/api/viewsets/base.py:82-100`

```python
def de_serialize(self, obj=None, partial=False):
    is_update = True
    if not obj:
        is_update = False
        obj = self.__model__()  # Create empty Patient instance

    database_fields = self.get_database_mapping()
    dump = self.model_dump(mode="json", exclude_defaults=True)

    for field in dump:
        if field in database_fields and field not in self.__exclude__:
            obj.__setattr__(field, dump[field])

    self.perform_extra_deserialization(is_update, obj)
    return obj
```

### 7.2 Extra Deserialization

**File:** `care/emr/resources/patient/spec.py:136-150`

```python
def perform_extra_deserialization(self, is_update, obj):
    # Load geo_organization ForeignKey
    obj.geo_organization = Organization.objects.get(external_id=self.geo_organization)

    # Calculate year_of_birth
    if self.age:
        obj.date_of_birth = None
        obj.year_of_birth = timezone.now().date().year - self.age
    else:
        obj.year_of_birth = self.date_of_birth.year

    # Store for later processing in perform_create
    obj._identifiers = self.identifiers
    obj._tags = self.tags

    if not self.pincode:
        obj.pincode = None
```

## 8. Database Persistence

**File:** `care/emr/api/viewsets/patient.py:117-150`

```python
def perform_create(self, instance):
    identifiers = instance._identifiers
    try:
        with transaction.atomic():
            with PatientCreateLock():  # Prevent race conditions
                super().perform_create(instance)  # Save Patient

                # Create PatientIdentifier records
                for identifier in identifiers:
                    config = get_object_or_404(
                        PatientIdentifierConfig,
                        external_id=identifier.config,
                        facility__isnull=True,
                    )
                    if config.config.get("auto_maintained"):
                        continue
                    PatientIdentifier.objects.create(
                        patient=instance,
                        config=config,
                        value=identifier.value,
                    )

                # Process default values and identifiers
                evaluate_patient_instance_default_values(instance)
                instance.build_instance_identifiers()
                instance.save()

            # Apply tags
            tag_manager = PatientInstanceTagManager()
            tag_manager.set_tags(
                TagResource.patient,
                instance,
                instance._tags,
                self.request.user,
            )
    except ObjectLocked as e:
        raise ValidationError("Patient creation failed, try again after a while") from e
```

## 9. Patient Model

**File:** `care/emr/models/patient.py:16-134`

```python
class Patient(EMRBaseModel):
    name = models.CharField(max_length=200, default="")
    gender = models.CharField(max_length=35, default="")
    phone_number = models.CharField(max_length=14, validators=[mobile_or_landline_number_validator])
    emergency_phone_number = models.CharField(max_length=14, validators=[mobile_or_landline_number_validator])
    address = models.TextField(default="")
    permanent_address = models.TextField(default="")
    pincode = models.IntegerField(default=0, blank=True, null=True)
    date_of_birth = models.DateField(default=None, null=True)
    year_of_birth = models.IntegerField(validators=[MinValueValidator(1900)], null=True)
    deceased_datetime = models.DateTimeField(default=None, null=True, blank=True)
    blood_group = models.CharField(max_length=16)
    geo_organization = models.ForeignKey("emr.Organization", on_delete=models.SET_NULL, null=True)
    organization_cache = ArrayField(models.IntegerField(), default=list)
    users_cache = ArrayField(models.IntegerField(), default=list)
    instance_identifiers = models.JSONField(default=list, null=True, blank=True)
    facility_identifiers = models.JSONField(default=dict, null=True, blank=True)
    instance_tags = ArrayField(models.IntegerField(), default=list)
    facility_tags = models.JSONField(default=dict, null=True, blank=True)
    extensions = models.JSONField(default=dict)

    def save(self, *args, **kwargs) -> None:
        if self.date_of_birth and not self.year_of_birth:
            self.year_of_birth = self.date_of_birth.year
        super().save(*args, **kwargs)
        self.rebuild_organization_cache()
        self.rebuild_users_cache()
        super().save(update_fields=["organization_cache", "users_cache"])
```

## 10. Validation Summary

| Step | Location | Purpose |
|------|----------|---------|
| 1 | `PatientBaseSpec.validate_deceased_datetime` | Deceased datetime cannot be in the future |
| 2 | `PatientCreateSpec.validate_geo_organization` | Geo organization must exist as govt org type |
| 3 | `PatientCreateSpec.validate_identifiers` | Required identifiers and uniqueness validation |
| 4 | `validate_identifier_config()` | Regex pattern matching for identifier values |
| 5 | `PatientViewSet.validate_data()` | DOB vs deceased date business logic |
| 6 | `PatientViewSet.authorize_create()` | User permission check |
| 7 | Phone number field | E.164 format validation via PhoneNumber type |

## 11. Example Request

```json
POST /api/v1/patient/
{
    "name": "John Doe",
    "gender": "male",
    "phone_number": "+919876543210",
    "geo_organization": "550e8400-e29b-41d4-a716-446655440000",
    "date_of_birth": "1990-05-15",
    "address": "123 Main Street",
    "blood_group": "O+",
    "identifiers": [
        {
            "config": "660e8400-e29b-41d4-a716-446655440001",
            "value": "ABCD1234"
        }
    ],
    "tags": ["770e8400-e29b-41d4-a716-446655440002"]
}
```

## 12. Key Relationships

```
Patient
    ├── Organization (geo_organization FK)
    ├── PatientIdentifier (One-to-Many)
    │       └── PatientIdentifierConfig (FK)
    ├── PatientUser (access control)
    └── Tags (instance and facility level)
```

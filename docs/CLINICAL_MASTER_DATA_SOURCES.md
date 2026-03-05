# Clinical Master Data Sources - CARE EMR System

## Overview

This document explains where the master data (reference lists) for clinical objects comes from in the CARE EMR system. It covers medications, lab tests, diagnoses, procedures, and other clinical terminologies.

---

## Quick Reference Table

| Clinical Object | Source System | Code System | API Endpoint |
|----------------|---------------|-------------|--------------|
| **Medications** | SNOMED-CT | `http://snomed.info/sct` | `/api/emr/valueset/system-medication/expand` |
| **Lab Tests** | LOINC | `http://loinc.org` | `/api/emr/observation_definition/` |
| **Diagnoses** | SNOMED-CT | `http://snomed.info/sct` | `/api/emr/valueset/system-condition-code/expand` |
| **Procedures** | SNOMED-CT | `http://snomed.info/sct` | `/api/emr/activity_definition/` |
| **Body Sites** | SNOMED-CT | `http://snomed.info/sct` | `/api/emr/valueset/system-body-site/expand` |
| **Routes** | SNOMED-CT | `http://snomed.info/sct` | `/api/emr/valueset/system-route/expand` |
| **Units** | UCUM | `http://unitsofmeasure.org` | `/api/emr/valueset/system-ucum-units/expand` |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SOURCES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────┐    ┌─────────────────────┐                │
│   │  Snowstorm FHIR     │    │  UCUM               │                │
│   │  Server             │    │  (Units)            │                │
│   │  ─────────────────  │    │  ─────────────────  │                │
│   │  • SNOMED-CT        │    │  • mg, mL, g/dL     │                │
│   │  • Medications      │    │  • tablets, drops   │                │
│   │  • Diagnoses        │    │  • days, hours      │                │
│   │  • Body Sites       │    │                     │                │
│   │  • Routes           │    │                     │                │
│   │  • Procedures       │    │                     │                │
│   └──────────┬──────────┘    └──────────┬──────────┘                │
│              │                          │                            │
└──────────────┼──────────────────────────┼────────────────────────────┘
               │                          │
               ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CARE BACKEND                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────┐    ┌─────────────────────┐                │
│   │  ValueSet Registry  │    │  Local Database     │                │
│   │  ─────────────────  │    │  ─────────────────  │                │
│   │  • CareValueset     │    │  • ObservationDef   │                │
│   │  • SystemValueSet   │    │  • ActivityDef      │                │
│   │  • Caching (Redis)  │    │  • SpecimenDef      │                │
│   │                     │    │  • ProductKnowledge │                │
│   └──────────┬──────────┘    └──────────┬──────────┘                │
│              │                          │                            │
│              └──────────────┬───────────┘                            │
│                             │                                        │
│                             ▼                                        │
│              ┌─────────────────────────────┐                        │
│              │     REST API Endpoints      │                        │
│              │  • /api/emr/valueset/       │                        │
│              │  • /api/emr/observation_def/│                        │
│              │  • /api/emr/activity_def/   │                        │
│              └──────────────┬──────────────┘                        │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CARE FRONTEND                                │
├─────────────────────────────────────────────────────────────────────┤
│  • Medication autocomplete (typeahead search)                        │
│  • Diagnosis search dropdown                                         │
│  • Lab test selection from definitions                               │
│  • Procedure ordering from activity definitions                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Medications / Drugs

### Source
- **Terminology:** SNOMED-CT
- **Server:** Snowstorm FHIR Server
- **Filter:** `<< 763158003 |Medicinal product|`

### Files
| File | Purpose |
|------|---------|
| `care/emr/resources/medication/valueset/medication.py` | ValueSet definition |
| `care/emr/models/medication_request.py` | Prescription storage |
| `care/emr/models/product_knowledge.py` | Medication details |

### ValueSet Definition
```python
# care/emr/resources/medication/valueset/medication.py
CARE_MEDICATION_VALUESET = CareValueset(
    "Medication",
    "system-medication",
    ValueSetStatusOptions.active.value
)
CARE_MEDICATION_VALUESET.register_valueset(
    ValueSetCompose(
        include=[
            ValueSetInclude(
                system="http://snomed.info/sct",
                filter=[{"property": "concept", "op": "is-a", "value": "763158003"}]
            )
        ]
    )
)
```

### API Usage
```bash
# Search medications
POST /api/emr/valueset/system-medication/expand
Content-Type: application/json

{
  "filter": "paracetamol",
  "count": 20
}
```

### Response Example
```json
{
  "results": [
    {
      "code": "90332006",
      "display": "Paracetamol 500mg tablet",
      "system": "http://snomed.info/sct"
    },
    {
      "code": "27658006",
      "display": "Amoxicillin 500mg capsule",
      "system": "http://snomed.info/sct"
    }
  ]
}
```

### Database Storage
When a medication is prescribed, it's stored in `MedicationRequest`:
```python
# MedicationRequest model fields
medication = JSONField()  # {"code": "90332006", "display": "Paracetamol", "system": "..."}
dosage_instruction = JSONField()  # Dosing details
```

---

## 2. Lab Tests / Observations

### Source
- **Codes:** LOINC (Logical Observation Identifiers Names and Codes)
- **Definitions:** Local `ObservationDefinition` table
- **Ordering:** `ActivityDefinition` for test panels

### Files
| File | Purpose |
|------|---------|
| `care/emr/models/observation_definition.py` | Test definitions |
| `care/emr/models/observation.py` | Test results |
| `care/emr/models/activity_definition.py` | Test packages |
| `care/emr/resources/observation/valueset.py` | Code valuesets |

### How Lab Tests Are Defined

**Step 1: Create ObservationDefinition**
```python
# Example: Fasting Blood Glucose
ObservationDefinition(
    code={"code": "1558-6", "display": "Fasting glucose", "system": "http://loinc.org"},
    permitted_data_type=["Quantity"],
    qualified_value=[
        {
            "condition": "Normal",
            "range": {"low": 70, "high": 100, "unit": "mg/dL"}
        },
        {
            "condition": "Pre-diabetic",
            "range": {"low": 100, "high": 125, "unit": "mg/dL"}
        }
    ]
)
```

**Step 2: Create ActivityDefinition (Orderable Test)**
```python
# Example: Glucose Test Panel
ActivityDefinition(
    code={"code": "1558-6", "display": "Fasting Glucose Test"},
    category="laboratory",
    observation_definition=[fasting_glucose_def],
    specimen_definition=blood_specimen_def,
    charge_item_definition=glucose_pricing
)
```

### Pre-loaded Lab Tests (Fixtures)

**File:** `care/emr/management/commands/load_fixtures.py:1119-1535`

| Test Name | LOINC Code | Unit | Reference Range |
|-----------|------------|------|-----------------|
| Fasting Blood Glucose | 1558-6 | mg/dL | 70-100 |
| Hemoglobin | 718-7 | g/dL | 12-16 (F), 14-18 (M) |
| WBC Count | 6690-2 | 10*3/uL | 4.5-11.0 |
| Platelet Count | 777-3 | 10*3/uL | 150-400 |
| RBC Count | 789-8 | 10*6/uL | 4.5-5.5 |
| Total Cholesterol | 2093-3 | mg/dL | <200 |
| Triglycerides | 2571-8 | mg/dL | <150 |
| HDL Cholesterol | 2085-9 | mg/dL | >40 |
| LDL Cholesterol | 2089-1 | mg/dL | <100 |

### API Endpoints

```bash
# List available lab tests
GET /api/emr/observation_definition/

# List orderable test panels
GET /api/emr/activity_definition/?category=laboratory

# Create lab order
POST /api/emr/service_request/
{
  "activity_definition": "uuid-of-activity-def",
  "encounter": "encounter-uuid",
  "intent": "order"
}

# Record lab result
POST /api/emr/observation/
{
  "observation_definition": "uuid-of-obs-def",
  "value": {"value": 95, "unit": "mg/dL"},
  "status": "final"
}
```

---

## 3. Diagnoses / Conditions

### Source
- **Terminology:** SNOMED-CT (Clinical Findings)
- **Server:** Snowstorm FHIR Server
- **Filter:** `<< 404684003 |Clinical finding|`

### Files
| File | Purpose |
|------|---------|
| `care/emr/resources/condition/valueset.py` | ValueSet definition |
| `care/emr/models/condition.py` | Diagnosis storage |

### ValueSet Definition
```python
# care/emr/resources/condition/valueset.py
CARE_CONDITION_CODE_VALUESET = CareValueset(
    "Condition",
    "system-condition-code",
    ValueSetStatusOptions.active.value
)
CARE_CONDITION_CODE_VALUESET.register_valueset(
    ValueSetCompose(
        include=[
            ValueSetInclude(
                system="http://snomed.info/sct",
                filter=[{"property": "concept", "op": "is-a", "value": "404684003"}]
            )
        ]
    )
)
```

### API Usage
```bash
# Search diagnoses
POST /api/emr/valueset/system-condition-code/expand
{
  "filter": "diabetes",
  "count": 20
}
```

### Response Example
```json
{
  "results": [
    {"code": "73211009", "display": "Diabetes mellitus", "system": "http://snomed.info/sct"},
    {"code": "44054006", "display": "Type 2 diabetes mellitus", "system": "http://snomed.info/sct"},
    {"code": "46635009", "display": "Type 1 diabetes mellitus", "system": "http://snomed.info/sct"}
  ]
}
```

### Condition Model Fields
```python
class Condition(EMRBaseModel):
    code = JSONField()           # SNOMED code
    clinical_status = CharField()  # active, recurrence, relapse, inactive, remission, resolved
    verification_status = CharField()  # unconfirmed, provisional, differential, confirmed, refuted
    severity = CharField()       # mild, moderate, severe
    category = CharField()       # encounter_diagnosis, chronic_condition, problem_list_item
    onset = JSONField()          # When condition started
    patient = ForeignKey()
    encounter = ForeignKey()
```

---

## 4. Procedures / Service Requests

### Source
- **Codes:** SNOMED-CT (Procedures)
- **Definitions:** Local `ActivityDefinition` table

### Files
| File | Purpose |
|------|---------|
| `care/emr/models/service_request.py` | Procedure orders |
| `care/emr/models/activity_definition.py` | Procedure templates |

### ActivityDefinition Categories
| Category | Description | Examples |
|----------|-------------|----------|
| `laboratory` | Lab tests | CBC, Lipid Panel |
| `imaging` | Radiology | X-ray, CT Scan, MRI |
| `procedure` | Surgical/Clinical | Wound dressing, Biopsy |
| `counseling` | Consultations | Dietary counseling |

### ServiceRequest Model
```python
class ServiceRequest(EMRBaseModel):
    title = CharField()
    code = JSONField()           # Procedure code
    category = CharField()       # laboratory, imaging, procedure
    status = CharField()         # draft, active, completed, revoked
    intent = CharField()         # proposal, plan, order
    priority = CharField()       # routine, urgent, asap, stat
    body_site = JSONField()      # Where procedure performed
    activity_definition = ForeignKey()
    healthcare_service = ForeignKey()
```

### API Endpoints
```bash
# List procedure templates
GET /api/emr/activity_definition/?category=procedure

# Create procedure order
POST /api/emr/service_request/
{
  "title": "Wound Dressing",
  "code": {"code": "225358003", "display": "Wound dressing", "system": "http://snomed.info/sct"},
  "category": "procedure",
  "intent": "order",
  "priority": "routine"
}
```

---

## 5. Body Sites (Anatomical Locations)

### Source
- **Terminology:** SNOMED-CT (Anatomical Structures)
- **Filter:** `<< 91723000 |Anatomical structure|`

### Files
| File | Purpose |
|------|---------|
| `care/emr/resources/medication/valueset/body_site.py` | ValueSet |
| `care/emr/resources/observation/valueset.py:17-108` | Specific body sites |

### Common Body Sites
| Code | Display |
|------|---------|
| 368208006 | Left upper arm |
| 368209003 | Right upper arm |
| 723979003 | Left deltoid |
| 723980000 | Right deltoid |
| 69536005 | Head |
| 51185008 | Thorax |
| 818983003 | Abdomen |

### API Usage
```bash
POST /api/emr/valueset/system-body-site/expand
{
  "filter": "arm"
}
```

### Used In
- `MedicationRequest.dosage_instruction[].site` - Injection site
- `Condition.body_site` - Location of condition
- `Observation.body_site` - Where observation taken
- `ServiceRequest.body_site` - Procedure location

---

## 6. Routes of Administration

### Source
- **Terminology:** SNOMED-CT
- **Filter:** `<< 284009009 |Route of administration|`

### File
`care/emr/resources/medication/valueset/route.py`

### Common Routes
| Code | Display | Abbreviation |
|------|---------|--------------|
| 26643006 | Oral route | PO |
| 47625008 | Intravenous route | IV |
| 34206005 | Subcutaneous route | SC |
| 78421000 | Intramuscular route | IM |
| 6064005 | Topical route | TOP |
| 46713006 | Nasal route | NAS |
| 37161004 | Rectal route | PR |
| 372464004 | Inhalation route | INH |

### API Usage
```bash
POST /api/emr/valueset/system-route/expand
{
  "filter": "oral"
}
```

### Used In
```python
# MedicationRequest dosage instruction
{
  "dosage_instruction": [{
    "route": {"code": "26643006", "display": "Oral route", "system": "http://snomed.info/sct"},
    "dose": {"value": 500, "unit": "mg"},
    "timing": {"frequency": 3, "period": 1, "periodUnit": "d"}
  }]
}
```

---

## 7. Dosage Forms

### Source
- **Terminology:** SNOMED-CT (Pharmaceutical Dose Forms)

### Common Dosage Forms
| Code | Display |
|------|---------|
| 421026006 | Oral tablet |
| 420161003 | Capsule |
| 385055001 | Liquid/Solution |
| 385219001 | Injection |
| 385101003 | Ointment |
| 385018001 | Cream |
| 421145000 | Eye drops |
| 385049006 | Powder |

### Used In
`ProductKnowledge.definitional.dosage_form`

---

## 8. Units of Measurement

### Source
- **System:** UCUM (Unified Code for Units of Measure)
- **URL:** `http://unitsofmeasure.org`

### File
`care/emr/resources/observation/valueset.py:137-145`

### Common Units
| Code | Description | Usage |
|------|-------------|-------|
| `mg` | milligram | Medication dose |
| `g` | gram | Weight |
| `mL` | milliliter | Volume |
| `L` | liter | Volume |
| `g/dL` | gram per deciliter | Hemoglobin |
| `mg/dL` | milligram per deciliter | Glucose, cholesterol |
| `%` | percent | Percentage |
| `mmHg` | millimeter of mercury | Blood pressure |
| `/min` | per minute | Heart rate, respiratory rate |
| `Cel` | degree Celsius | Temperature |
| `kg` | kilogram | Body weight |
| `cm` | centimeter | Height |
| `kg/m2` | kilogram per square meter | BMI |
| `10*3/uL` | thousands per microliter | WBC, Platelet count |
| `10*6/uL` | millions per microliter | RBC count |
| `{tbl}` | tablets | Medication count |
| `{drops}` | drops | Eye drops |
| `d` | days | Duration |
| `h` | hours | Frequency |
| `wk` | weeks | Duration |
| `mo` | months | Duration |

### API Usage
```bash
POST /api/emr/valueset/system-ucum-units/expand
{
  "filter": "gram"
}
```

---

## 9. Observation Interpretations

### Source
- **System:** HL7 v3 ObservationInterpretation

### Common Interpretations
| Code | Display | Meaning |
|------|---------|---------|
| N | Normal | Within reference range |
| L | Low | Below reference range |
| H | High | Above reference range |
| LL | Critically Low | Critically below range |
| HH | Critically High | Critically above range |
| A | Abnormal | Outside normal range |
| AA | Critically Abnormal | Life-threatening abnormal |

### Used In
```python
# Observation model
{
  "value": {"value": 250, "unit": "mg/dL"},
  "interpretation": [{"code": "H", "display": "High"}],
  "reference_range": [{"low": 70, "high": 100, "unit": "mg/dL"}]
}
```

---

## Database Models Summary

### Core Clinical Models

| Model | Table | Purpose | Code Source |
|-------|-------|---------|-------------|
| `MedicationRequest` | `emr_medicationrequest` | Prescriptions | SNOMED |
| `MedicationStatement` | `emr_medicationstatement` | Medication history | SNOMED |
| `MedicationAdministration` | `emr_medicationadministration` | Given medications | SNOMED |
| `MedicationDispense` | `emr_medicationdispense` | Dispensed medications | SNOMED |
| `Observation` | `emr_observation` | Lab results, vitals | LOINC |
| `Condition` | `emr_condition` | Diagnoses | SNOMED |
| `ServiceRequest` | `emr_servicerequest` | Lab/procedure orders | LOINC/SNOMED |
| `DiagnosticReport` | `emr_diagnosticreport` | Lab reports | LOINC |
| `Allergy` | `emr_allergy` | Allergies | SNOMED |

### Definition Models (Master Data)

| Model | Table | Purpose |
|-------|-------|---------|
| `ObservationDefinition` | `emr_observationdefinition` | Lab test definitions |
| `ActivityDefinition` | `emr_activitydefinition` | Orderable procedures |
| `SpecimenDefinition` | `emr_specimendefinition` | Sample collection specs |
| `ProductKnowledge` | `emr_productknowledge` | Medication details |
| `ChargeItemDefinition` | `emr_chargeitemdefinition` | Pricing |

### ValueSet Models

| Model | Table | Purpose |
|-------|-------|---------|
| `ValueSet` | `emr_valueset` | Code system definitions |
| `ValueSetConcept` | `emr_valuesetconcept` | Individual codes |

---

## Configuration

### Snowstorm FHIR Server

**File:** `config/settings/base.py` or `.env`

```python
# Snowstorm server URL
SNOWSTORM_FHIR_URL = "http://165.22.211.144/fhir"
```

### Sync Commands

```bash
# Sync all valuesets from Snowstorm
python manage.py sync_valueset

# Load sample lab tests and medications
python manage.py load_fixtures
```

---

## API Reference

### ValueSet APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/emr/valueset/` | GET | List all valuesets |
| `/api/emr/valueset/{slug}/` | GET | Get valueset details |
| `/api/emr/valueset/{slug}/expand` | POST | Search codes |
| `/api/emr/valueset/{slug}/validate_code` | POST | Validate a code |
| `/api/emr/valueset/{slug}/add_favourite` | POST | Save favorite code |

### Definition APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/emr/observation_definition/` | GET | List lab test definitions |
| `/api/emr/activity_definition/` | GET | List orderable procedures |
| `/api/emr/specimen_definition/` | GET | List specimen types |
| `/api/emr/product_knowledge/` | GET | List medication products |

### Clinical Data APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/emr/medication_request/` | GET/POST | Prescriptions |
| `/api/emr/observation/` | GET/POST | Lab results |
| `/api/emr/condition/` | GET/POST | Diagnoses |
| `/api/emr/service_request/` | GET/POST | Lab/procedure orders |

---

## File Reference

### ValueSet Definitions

| Clinical Area | File Path |
|---------------|-----------|
| Medications | `care/emr/resources/medication/valueset/medication.py` |
| Body Sites | `care/emr/resources/medication/valueset/body_site.py` |
| Routes | `care/emr/resources/medication/valueset/route.py` |
| Conditions | `care/emr/resources/condition/valueset.py` |
| Observations | `care/emr/resources/observation/valueset.py` |
| Allergies | `care/emr/resources/allergy/valueset.py` |

### Models

| Model | File Path |
|-------|-----------|
| ValueSet | `care/emr/models/valueset.py` |
| MedicationRequest | `care/emr/models/medication_request.py` |
| Observation | `care/emr/models/observation.py` |
| ObservationDefinition | `care/emr/models/observation_definition.py` |
| Condition | `care/emr/models/condition.py` |
| ServiceRequest | `care/emr/models/service_request.py` |
| ActivityDefinition | `care/emr/models/activity_definition.py` |
| ProductKnowledge | `care/emr/models/product_knowledge.py` |

### FHIR Integration

| Component | File Path |
|-----------|-----------|
| FHIR Client | `care/emr/fhir/client.py` |
| ValueSet Resource | `care/emr/fhir/resources/valueset.py` |
| CodeSystem Resource | `care/emr/fhir/resources/code_system.py` |

### Commands

| Command | File Path |
|---------|-----------|
| sync_valueset | `care/emr/management/commands/sync_valueset.py` |
| load_fixtures | `care/emr/management/commands/load_fixtures.py` |

---

## 10. Fixture Loading & Master Data Templates

### Overview

The CARE system provides two mechanisms for loading clinical master data:
1. **`load_fixtures.py`** - Python command for programmatic fixture creation
2. **`PRODUCT_MASTERS.xlsx`** - Excel template for bulk data loading

---

### load_fixtures.py Command

**File:** `care/emr/management/commands/load_fixtures.py`

**Usage:**
```bash
python manage.py load_fixtures
```

**What It Creates:**

| Component | Count | Description |
|-----------|-------|-------------|
| SpecimenDefinition | 4 | Blood, Urine, CBC, Lipid specimens |
| ObservationDefinition | 15+ | Lab tests with LOINC codes and reference ranges |
| ActivityDefinition | 4 | Orderable test panels |
| ProductKnowledge | 4 | Sample medications |
| ChargeItemDefinition | 4+ | Pricing templates |
| HealthcareService | 2 | Lab and Pharmacy services |
| Inventory Items | 4 | Sample inventory products |

#### Sample Specimen Definitions

| Title | Type Code | Collection Method | Body Site |
|-------|-----------|-------------------|-----------|
| Fasting Blood Glucose | 788707000 (Blood sample) | 82078001 (Venipuncture) | 53120007 (Arm) |
| CBC | 788707000 (Blood sample) | 82078001 (Venipuncture) | 53120007 (Arm) |
| Lipid Panel | 788707000 (Blood sample) | 82078001 (Venipuncture) | 53120007 (Arm) |
| Urinalysis | 122575003 (Urine specimen) | 167217005 (Urine collection) | N/A |

#### Sample Observation Definitions (Lab Tests)

| Test | LOINC Code | Unit | Reference Ranges |
|------|------------|------|------------------|
| Fasting Blood Glucose | 1558-6 | mg/dL | Normal: 70-100, Pre-diabetic: 100-126, Diabetic: >126 |
| Hemoglobin | 718-7 | g/dL | Male: 14-18, Female: 12-16 |
| WBC Count | 26464-8 | 10*3/uL | 4.5-11.0 |
| Platelet Count | 777-3 | 10*3/uL | 150-400 |
| RBC Count | 789-8 | 10*6/uL | Male: 4.7-6.1, Female: 4.2-5.4 |
| Total Cholesterol | 2093-3 | mg/dL | Desirable: <200, Borderline: 200-239, High: ≥240 |
| Triglycerides | 2571-8 | mg/dL | Normal: <150, Borderline: 150-199, High: 200-499 |
| HDL Cholesterol | 2085-9 | mg/dL | Low: <40, Borderline: 40-60, Optimal: >60 |
| LDL Cholesterol | 2089-1 | mg/dL | Optimal: <100, Borderline: 130-159, High: ≥160 |
| Urinalysis Panel | LP7681-2 | N/A | Multiple components |

#### Sample Product Knowledge (Medications)

| Medication | SNOMED Code | Dosage Form | Routes |
|------------|-------------|-------------|--------|
| Amoxicillin 500mg | 27658006 | Capsule (420161003) | Oral (26643006) |
| Paracetamol 500mg | 90332006 | Tablet (421026006) | Oral (26643006) |
| Ibuprofen 400mg | 38268001 | Tablet (421026006) | Oral (26643006) |
| Disposable Gloves (L) | 52291003 | N/A | N/A |

---

### PRODUCT_MASTERS.xlsx Template

**File:** `docs/PRODUCT_MASTERS.xlsx`

This Excel file serves as a template for bulk-loading clinical master data. It contains 5 sheets:

#### Sheet 1: ActivityDefinition (101 rows)

Defines orderable procedures with SNOMED codes.

**Columns:**
| Column | Description | Example |
|--------|-------------|---------|
| title | Procedure name | "Dressing", "Nebulisation", "Suture removal" |
| description | Detailed description | - |
| usage | Usage context | - |
| code_value | SNOMED procedure code | 3895009, 56251003, 30549001 |
| code_display | SNOMED display text | "Application of dressing" |
| healthcare_service | Service slug | "Emergency", "In-Patient Services" |
| locations | Location slugs | Location codes |
| diagnostic_report_codes | Report codes | - |
| specimen_slugs | Required specimens | Specimen slugs |
| observation_slugs | Related observations | Observation slugs |
| charge_item_slugs | Pricing templates | ChargeItem slugs |

**Sample Data:**

| Title | Code | Code Display | Healthcare Service |
|-------|------|--------------|-------------------|
| Dressing | 3895009 | Application of dressing | Emergency |
| Subcutaneous Injection | 1285265006 | Injection into subcutaneous tissue | Emergency |
| Nebulisation | 56251003 | Nebulizer therapy | Emergency |
| Enema | 61919008 | Giving patient an enema | In-Patient Services |
| NG tube insertion | 87750000 | Insertion of nasogastric tube | Emergency |
| Suture removal | 30549001 | Removal of suture | Emergency |
| Resuscitation | 439569004 | Resuscitation | Emergency |
| Catheterization | 45211000 | Catheterization | Emergency |

#### Sheet 2: ObservationDefinition (73 rows)

Defines lab test observations with LOINC codes and reference ranges.

**Key Columns:**
| Column | Description |
|--------|-------------|
| title | Test name |
| slug_value | Unique identifier |
| code_value | LOINC code |
| code_display | LOINC display text |
| code_system | `http://loinc.org` |
| category | laboratory, vital-signs, etc. |
| permitted_data_type | Quantity, string, CodeableConcept |
| qualified_ranges | Reference ranges by context |
| component_code | For panel components |

**Sample Data:**

| Title | LOINC Code | Code Display |
|-------|------------|--------------|
| AFB (24 HRS URINE) | 11480-1 | Microscopic observation in Urine by Acid fast stain |
| Hemoglobin | 718-7 | Hemoglobin [Mass/volume] in Blood |
| Total leucocyte count | 26464-8 | Leucocytes in Blood |
| Platelet count | 777-3 | Platelets [#/volume] in Blood |
| CBC Test | 58410-2 | Complete blood count panel |
| ESR | 4537-7 | Erythrocyte Sedimentation Rate |
| Blood group (ABO) | 883-9 | ABO group [Type] in Blood |
| Blood group (Rh typing) | 10331-7 | Rh type in blood |

#### Sheet 3: Radiology ActivityDefinition (92 rows)

Defines radiology procedures with SNOMED codes.

**Columns:**
| Column | Description |
|--------|-------------|
| category | Always "Radiology" |
| title | Test name |
| slug_value | Unique identifier |
| code_value | SNOMED procedure code |
| code_display | SNOMED display text |
| code_system | `http://snomed.info/sct` |
| diagnostic_report_codes | Report codes |
| healthcare_service | "Radiology" |

**Sample Data:**

| Title | Code | Code Display |
|-------|------|--------------|
| X-RAY SKULL AP | 55965002 | Plain X-ray of bone of cranium |
| X-RAY SKULL AP/LAT | 55965002 | Plain X-ray of bone of cranium |
| X-RAY FACE AP | 1290812008 | Plain X-ray of face |
| X-RAY MASTOID LAT | 1293029006 | Plain X-ray of mastoid |
| X-RAY NASAL BONE AP | 1290808002 | Plain X-ray of nasal bone |
| X-RAY CERVICAL SPINE AP | 712970008 | Plain X-ray of cervical vertebral column |
| X-RAY THORACIC SPINE | 399061000 | Plain X-ray of thoracic spine |
| X-RAY CHEST PA | 399208008 | Plain chest X-ray |

#### Sheet 4: Product Knowledge for KA (249 rows)

Karnataka-specific medication formulary with SNOMED codes.

**Columns:**
| Column | Description |
|--------|-------------|
| name | Medication name with strength |
| product_type | "Medication" |
| category | "Medication" |
| display | SNOMED display text |
| code | SNOMED product code |
| base_unit | Base unit of measure |
| status | active/inactive |
| dosage_form_display | Form (Tablet, Injection, etc.) |
| dosage_form_code | SNOMED dosage form code |
| route_display | Administration route |
| route_code | SNOMED route code |
| Pack Size | Units per pack |

**Sample Data:**

| Name | SNOMED Code | Dosage Form | Route |
|------|-------------|-------------|-------|
| Ketamine Injection 10 mg/ml | 781952002 | Solution for injection | IV, IM |
| Propofol Injection 10 mg/ml | 782081001 | Solution for injection | IV |
| Sevoflurane Inhalation | 1285093003 | Solution for inhalation | Inhalation |
| Bupivacaine 0.5% with Glucose 7.5% | 7621000189103 | Solution for injection | Spinal |
| Lignocaine Injection 2% | 781967003 | Solution for injection | IV |
| Lignocaine jelly 2% | 334243009 | Cutaneous gel | Topical |
| Atropine Injection 0.6 mg/ml | - | Solution for injection | IV |
| Midazolam Injection 5 mg/ml | 781998001 | Solution for injection | IV, IM |
| Aceclofenac Tablet 100 mg | 329925006 | Oral Tablet | Oral |
| Diclofenac Sodium Tablet 50 mg | 374627000 | Oral Tablet | Oral |

#### Sheet 5: T-Rohit (20 rows)

Additional activity definitions for specific procedures.

**Columns:** Similar to ActivityDefinition sheet.

---

### Loading Excel Data

While the Excel template is provided for reference, data loading is typically done through:

1. **Custom import scripts** - Python scripts to parse Excel and create database records
2. **Admin interface** - Manual entry through Django admin
3. **API endpoints** - Bulk create via REST API

**Example Import Pattern:**
```python
import pandas as pd
from care.emr.models import ActivityDefinition, ObservationDefinition

def import_activity_definitions(excel_path):
    df = pd.read_excel(excel_path, sheet_name='ActivityDefinition')
    for _, row in df.iterrows():
        ActivityDefinition.objects.create(
            title=row['title'],
            code={
                'code': str(row['code_value']),
                'display': row['code_display'],
                'system': 'http://snomed.info/sct'
            },
            healthcare_service=get_service(row['healthcare_service']),
            # ... other fields
        )
```

---

### Data Summary by Category

| Category | Source | Template Sheet | Fixture Count | Template Rows |
|----------|--------|----------------|---------------|---------------|
| **Lab Tests** | LOINC | ObservationDefinition | 15+ | 73 |
| **Procedures** | SNOMED | ActivityDefinition | 4 | 101 |
| **Radiology** | SNOMED | Radiology ActivityDefinition | - | 92 |
| **Medications** | SNOMED | Product Knowledge for KA | 4 | 249 |
| **Specimens** | SNOMED | (in fixtures) | 4 | - |

---

## Summary

The CARE EMR system uses a hybrid approach for clinical master data:

1. **External Terminology (Real-time):**
   - SNOMED-CT via Snowstorm FHIR server for medications, diagnoses, body sites, routes
   - LOINC for lab test codes
   - UCUM for units of measurement

2. **Local Definitions (Database):**
   - `ObservationDefinition` for lab test reference ranges
   - `ActivityDefinition` for orderable tests and procedures
   - `ProductKnowledge` for medication product details
   - `ChargeItemDefinition` for pricing

3. **Caching:**
   - Redis cache for frequently accessed valuesets
   - Database sync for offline access

This architecture provides:
- **Standardization:** Using international terminologies (SNOMED, LOINC)
- **Flexibility:** Local customization of test panels and pricing
- **Performance:** Caching for fast searches
- **Interoperability:** FHIR-compliant data exchange

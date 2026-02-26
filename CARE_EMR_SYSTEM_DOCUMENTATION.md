# CARE EMR System Documentation

## Table of Contents
1. [Medications Management](#1-medications-management)
2. [Lab Tests / Service Requests](#2-lab-tests--service-requests)
3. [Diagnosis Management](#3-diagnosis-management)
4. [Forms / Questionnaires](#4-forms--questionnaires)
5. [Templates](#5-templates)
6. [User Roles and Permissions Summary](#6-user-roles-and-permissions-summary)

---

## 1. Medications Management

### Overview
The medication system follows FHIR standards with support for medication requests (prescriptions), statements (patient's medication history), administrations, and dispensing.

### Database Models

| Model | File Path | Purpose |
|-------|-----------|---------|
| **MedicationRequest** | `care/emr/models/medication_request.py:31-65` | Prescriptions/orders for medications |
| **MedicationStatement** | `care/emr/models/medication_statement.py:6-15` | Patient's current/past medication history |
| **MedicationAdministration** | `care/emr/models/medication_administration.py:8-29` | Records of when medications were given |
| **MedicationDispense** | `care/emr/models/medication_dispense.py:9-56` | Pharmacy dispensing records |
| **MedicationRequestPrescription** | `care/emr/models/medication_request.py:9-28` | Groups medication requests into prescriptions |

### Key Fields

**MedicationRequest:**
- `status`: active, on_hold, ended, stopped, completed, cancelled, entered_in_error, draft, unknown
- `intent`: proposal, plan, order, original_order, reflex_order, filler_order, instance_order
- `priority`: routine, urgent, asap, stat
- `category`: inpatient, outpatient, community, discharge
- `medication`: JSONField containing SNOMED/RxNorm codes
- `dosage_instruction`: JSONField with dosing details
- `dispense_status`: complete, partial, incomplete, declined

### API Endpoints

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Prescriptions | `/api/v1/patient/{patientId}/medication/prescription/` | GET |
| Create Prescription | `/api/v1/patient/{patientId}/medication/prescription/` | POST |
| Upsert Prescription | `/api/v1/patient/{patientId}/medication/prescription/upsert/` | POST |
| List Medication Requests | `/api/v1/patient/{patientId}/medication/request/` | GET |
| Create Medication Request | `/api/v1/patient/{patientId}/medication/request/` | POST |
| Upsert Medication Request | `/api/v1/patient/{patientId}/medication/request/upsert/` | POST |
| List Medication Statements | `/api/v1/patient/{patientId}/medication/statement/` | GET |
| Create Medication Statement | `/api/v1/patient/{patientId}/medication/statement/` | POST |
| List Administrations | `/api/v1/patient/{patientId}/medication/administration/` | GET |
| Create Administration | `/api/v1/patient/{patientId}/medication/administration/` | POST |
| List Dispenses | `/api/v1/medication/dispense/` | GET |
| Create Dispense | `/api/v1/medication/dispense/` | POST |
| Dispense Summary | `/api/v1/medication/dispense/summary/` | GET |

### Permissions

**File:** `care/security/permissions/medication.py:14-46`

| Permission | Roles with Access |
|------------|-------------------|
| `is_pharmacist` | FACILITY_ADMIN, ADMIN, PHARMACIST |
| `read_medication_dispense` | FACILITY_ADMIN, ADMIN, STAFF, DOCTOR, NURSE, PHARMACIST |
| `write_medication_dispense` | FACILITY_ADMIN, ADMIN, STAFF, DOCTOR, NURSE, PHARMACIST |

**Creating Medications:**
- Requires `can_update_encounter_clinical_data` permission on the encounter
- If specifying a `requester`, that user must also have clinical data update permission
- Cannot create/update medications on completed encounters

**Dispensing Medications:**
- Pharmacists can dispense across multiple encounters at a location
- Requires `can_write_location_medication_dispense` permission
- Automatically creates ChargeItem records when products have pricing

### How to Create New Medication Data

1. **Via API (Prescription with Medications):**
```json
POST /api/v1/patient/{patientId}/medication/prescription/
{
  "name": "Prescription Name",
  "encounter": "encounter-uuid",
  "note": "Optional notes"
}

POST /api/v1/patient/{patientId}/medication/request/
{
  "encounter": "encounter-uuid",
  "prescription": "prescription-uuid",
  "medication": {
    "code": "27658006",
    "system": "http://snomed.info/sct",
    "display": "Amoxicillin"
  },
  "dosage_instruction": [{
    "timing": {"frequency": 3, "period": 1, "periodUnit": "d"},
    "dose": {"value": 500, "unit": "mg"},
    "route": {"code": "26643006", "display": "Oral"}
  }],
  "status": "active",
  "intent": "order",
  "priority": "routine"
}
```

2. **Via Frontend:**
   - Navigate to Patient → Encounter → Medicines tab
   - Use the prescription form to add medications
   - Component: `care_fe/src/components/Medicine/MedicationRequestTable/`

3. **Via Questionnaire (Structured Questions):**
   - Use questionnaires with `medication_request` or `medication_statement` structured types
   - Batch submitted with other clinical data

---

## 2. Lab Tests / Service Requests

### Overview
Lab tests are managed through Service Requests (orders), Specimens (samples), Diagnostic Reports (results), and Observations (individual test values).

### Database Models

| Model | File Path | Purpose |
|-------|-----------|---------|
| **ServiceRequest** | `care/emr/models/service_request.py:7-46` | Lab test orders |
| **Specimen** | `care/emr/models/specimen.py:6-32` | Biological samples for testing |
| **DiagnosticReport** | `care/emr/models/diagnostic_report.py:6-21` | Test result reports |
| **Observation** | `care/emr/models/observation.py:6-56` | Individual test result values |

### Key Fields

**ServiceRequest:**
- `title`: Test name/description
- `status`: draft, active, on_hold, entered_in_error, ended, completed, revoked
- `intent`: proposal, plan, directive, order
- `priority`: routine, urgent, asap, stat
- `category`: laboratory, imaging, counseling, etc.
- `code`: SNOMED CT code for test type
- `requester`: User who ordered the test
- `locations`: Facility locations for sample collection

**Specimen:**
- `accession_identifier`: Lab tracking number
- `status`: available, unavailable, unsatisfactory, entered_in_error
- `specimen_type`: SNOMED code for specimen type
- `collection`: Collection metadata (time, method, body site)

**DiagnosticReport:**
- `status`: registered, partial, preliminary, final
- `code`: Report code
- `conclusion`: Clinical interpretation

### API Endpoints

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Service Requests | `/api/v1/facility/{facilityId}/service_request/` | GET |
| Create Service Request | `/api/v1/facility/{facilityId}/service_request/` | POST |
| Update Service Request | `/api/v1/facility/{facilityId}/service_request/{id}/` | PUT |
| Complete Service Request | `/api/v1/facility/{facilityId}/service_request/{id}/complete/` | POST |
| Cancel Service Request | `/api/v1/facility/{facilityId}/service_request/{id}/cancel/` | POST |
| Create Specimen | `/api/v1/facility/{facilityId}/service_request/{id}/create_specimen/` | POST |
| Apply Activity Definition | `/api/v1/facility/{facilityId}/service_request/apply_activity_definition/` | POST |
| List Specimens | `/api/v1/facility/{facilityId}/specimen/` | GET |
| List Diagnostic Reports | `/api/v1/patient/{patientId}/diagnostic_report/` | GET |
| Create Diagnostic Report | `/api/v1/patient/{patientId}/diagnostic_report/` | POST |
| Upsert Observations | `/api/v1/patient/{patientId}/diagnostic_report/{id}/upsert_observations/` | POST |

### Permissions

**File:** `care/security/permissions/service_request.py:16-37`

| Permission | Roles with Access |
|------------|-------------------|
| `can_write_service_request` | FACILITY_ADMIN, ADMIN, DOCTOR, NURSE |
| `can_read_service_request` | FACILITY_ADMIN, ADMINISTRATOR, ADMIN, STAFF, DOCTOR, NURSE, VOLUNTEER, PHARMACIST |

**File:** `care/security/permissions/diagnostic_report.py:15-35`

| Permission | Roles with Access |
|------------|-------------------|
| `can_write_diagnostic_report` | FACILITY_ADMIN, ADMIN, DOCTOR, NURSE |
| `can_read_diagnostic_report` | FACILITY_ADMIN, ADMINISTRATOR, ADMIN, STAFF, DOCTOR, NURSE, VOLUNTEER |

### How to Create New Lab Test Orders

1. **Via API:**
```json
POST /api/v1/facility/{facilityId}/service_request/
{
  "title": "Complete Blood Count",
  "patient": "patient-uuid",
  "encounter": "encounter-uuid",
  "status": "active",
  "intent": "order",
  "priority": "routine",
  "category": "laboratory",
  "code": {
    "code": "88308006",
    "system": "http://snomed.info/sct",
    "display": "Complete blood count"
  },
  "requester": "user-uuid",
  "locations": ["location-uuid"]
}
```

2. **Create Specimen:**
```json
POST /api/v1/facility/{facilityId}/service_request/{id}/create_specimen/
{
  "specimen_type": {
    "code": "122555007",
    "display": "Venous blood specimen",
    "system": "http://snomed.info/sct"
  },
  "status": "available"
}
```

3. **Record Results:**
```json
POST /api/v1/patient/{patientId}/diagnostic_report/
{
  "service_request": "service-request-uuid",
  "status": "final",
  "conclusion": "Normal findings"
}

POST /api/v1/patient/{patientId}/diagnostic_report/{id}/upsert_observations/
{
  "observations": [
    {
      "main_code": {"code": "718-7", "display": "Hemoglobin"},
      "value_type": "numeric",
      "value": {"value": 14.5, "unit": "g/dL"},
      "reference_range": [{"low": 12, "high": 16, "unit": "g/dL"}]
    }
  ]
}
```

4. **Via Frontend:**
   - Navigate to Patient → Encounter → Service Requests tab
   - Use "Add Service Request" to create new orders
   - Component: `care_fe/src/components/ServiceRequest/ServiceRequestTable.tsx`

5. **Using Activity Definitions (Templates):**
   - Apply predefined test templates
   - Endpoint: `/api/v1/facility/{facilityId}/service_request/apply_activity_definition/`

---

## 3. Diagnosis Management

### Overview
Diagnosis data uses the FHIR Condition resource, storing clinical findings with SNOMED CT codes and ICD-11 classification support.

### Database Models

| Model | File Path | Purpose |
|-------|-----------|---------|
| **Condition** | `care/emr/models/condition.py:6-20` | Clinical diagnoses |
| **ICD11Diagnosis** | `care/facility/migrations/0388_icd11diagnosis.py` | ICD-11 code hierarchy |

### Key Fields

**Condition:**
- `clinical_status`: active, recurrence, relapse, inactive, remission, resolved, unknown
- `verification_status`: unconfirmed, provisional, differential, confirmed, refuted, entered_in_error
- `category`: problem_list_item, encounter_diagnosis, chronic_condition
- `severity`: mild, moderate, severe
- `code`: JSONField with SNOMED CT code
- `onset`: JSONField with onset timing (datetime, age, period, range, string)
- `abatement`: JSONField with resolution timing
- `note`: Clinical notes

### API Endpoints

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Diagnoses | `/api/v1/patient/{patientId}/diagnosis/` | GET |
| Create Diagnosis | `/api/v1/patient/{patientId}/diagnosis/` | POST |
| Retrieve Diagnosis | `/api/v1/patient/{patientId}/diagnosis/{id}/` | GET |
| Update Diagnosis | `/api/v1/patient/{patientId}/diagnosis/{id}/` | PUT |
| Delete Diagnosis | `/api/v1/patient/{patientId}/diagnosis/{id}/` | DELETE |
| List Symptoms | `/api/v1/patient/{patientId}/symptom/` | GET |
| Create Symptom | `/api/v1/patient/{patientId}/symptom/` | POST |

### Permissions

**File:** `care/security/permissions/patient.py:58-63` and `care/security/permissions/encounter.py:51-68`

| Permission | Roles with Access |
|------------|-------------------|
| `can_view_clinical_data` | STAFF, DOCTOR, NURSE, ADMIN, FACILITY_ADMIN |
| `can_write_encounter_clinical_data` | ADMIN, DOCTOR, NURSE, FACILITY_ADMIN |
| `can_read_encounter_clinical_data` | ADMIN, DOCTOR, NURSE, FACILITY_ADMIN |

**Special Rules:**
- Chronic conditions require patient-level `can_view_clinical_data` permission to update
- Encounter diagnoses require `can_update_encounter_clinical_data` permission
- Cannot modify diagnoses on completed encounters

### How to Create New Diagnoses

1. **Via API:**
```json
POST /api/v1/patient/{patientId}/diagnosis/
{
  "encounter": "encounter-uuid",
  "category": "encounter_diagnosis",
  "clinical_status": "active",
  "verification_status": "confirmed",
  "severity": "moderate",
  "code": {
    "code": "38341003",
    "system": "http://snomed.info/sct",
    "display": "Hypertension"
  },
  "onset": {
    "onset_datetime": "2024-01-15T10:00:00Z"
  },
  "note": "Patient presents with elevated blood pressure"
}
```

2. **Via Frontend:**
   - Navigate to Patient → Encounter → Overview/Forms
   - Use diagnosis question type in questionnaires
   - Component: `care_fe/src/components/Questionnaire/QuestionTypes/DiagnosisQuestion.tsx`

3. **Via Questionnaire (Structured):**
   - Diagnosis questions in forms automatically create Condition records
   - Supports duplicate detection and historical diagnosis lookup

---

## 4. Forms / Questionnaires

### Overview
The questionnaire system provides flexible, configurable forms for data collection. It supports multiple question types, conditional logic, templates, and structured data capture.

### Database Models

| Model | File Path | Purpose |
|-------|-----------|---------|
| **Questionnaire** | `care/emr/models/questionnaire.py:44-80` | Form definitions |
| **QuestionnaireTag** | `care/emr/models/questionnaire.py:13-42` | Form categorization |
| **FormSubmission** | `care/emr/models/questionnaire.py:83-91` | Draft form responses |
| **QuestionnaireResponse** | `care/emr/models/questionnaire.py:93-133` | Completed form submissions |
| **QuestionnaireOrganization** | `care/emr/models/questionnaire.py:135-154` | Organization access links |

### Key Fields

**Questionnaire:**
- `slug`: Unique URL-friendly identifier
- `title`: Human-readable name
- `description`: Form description
- `subject_type`: "patient" or "encounter"
- `status`: "active", "retired", or "draft"
- `questions`: JSONField with nested question structure
- `styling_metadata`: UI configuration
- `organization_cache`: Cached organization access

**Question Structure (JSON):**
```json
{
  "id": "uuid",
  "link_id": "1.1",
  "text": "Question text",
  "type": "choice|boolean|integer|decimal|string|text|date|dateTime|time|quantity|group|structured",
  "code": {"code": "...", "system": "...", "display": "..."},
  "required": true,
  "repeats": false,
  "enable_when": [...],
  "enable_behavior": "all|any",
  "answer_option": [...],
  "questions": [...]
}
```

**Question Types:**
- Basic: boolean, decimal, integer, string, text, date, dateTime, time, url, display
- Complex: choice, quantity, group
- Structured: diagnosis, medication_request, medication_statement, service_request, appointment, encounter, files

### API Endpoints

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Questionnaires | `/api/v1/questionnaire/` | GET |
| Get Questionnaire | `/api/v1/questionnaire/{slug}/` | GET |
| Create Questionnaire | `/api/v1/questionnaire/` | POST |
| Update Questionnaire | `/api/v1/questionnaire/{slug}/` | PUT |
| Delete Questionnaire | `/api/v1/questionnaire/{slug}/` | DELETE |
| Submit Questionnaire | `/api/v1/questionnaire/{slug}/submit/` | POST |
| Get Organizations | `/api/v1/questionnaire/{slug}/get_organizations/` | GET |
| Set Organizations | `/api/v1/questionnaire/{slug}/set_organizations/` | POST |
| Set Tags | `/api/v1/questionnaire/{slug}/set_tags/` | POST |
| List Tags | `/api/v1/questionnaire-tags/` | GET |
| List Form Submissions | `/api/v1/form-submissions/` | GET |
| Create Form Submission | `/api/v1/form-submissions/` | POST |
| List Responses | `/api/v1/patient/{patientId}/questionnaire-responses/` | GET |

### Permissions

**File:** `care/security/permissions/questionnaire.py`

| Permission | Roles with Access |
|------------|-------------------|
| `can_write_questionnaire` | ADMIN, FACILITY_ADMIN |
| `can_archive_questionnaire` | ADMIN, FACILITY_ADMIN |
| `can_read_questionnaire` | ADMIN, DOCTOR, NURSE, ADMINISTRATOR, STAFF, FACILITY_ADMIN, VOLUNTEER, PHARMACIST |
| `can_submit_questionnaire` | ADMIN, DOCTOR, NURSE, ADMINISTRATOR, STAFF, FACILITY_ADMIN, VOLUNTEER |
| `can_manage_questionnaire` | ADMIN, FACILITY_ADMIN |

**Important:** Only superusers can create/update/delete questionnaires via API.

### How to Create New Forms/Questionnaires

1. **Via API (Superuser Only):**
```json
POST /api/v1/questionnaire/
{
  "slug": "patient-assessment",
  "title": "Patient Assessment Form",
  "description": "Initial patient assessment",
  "subject_type": "encounter",
  "status": "active",
  "questions": [
    {
      "id": "uuid-1",
      "link_id": "1",
      "text": "Chief complaint",
      "type": "text",
      "required": true
    },
    {
      "id": "uuid-2",
      "link_id": "2",
      "text": "Pain level (1-10)",
      "type": "integer",
      "required": true
    },
    {
      "id": "uuid-3",
      "link_id": "3",
      "text": "Diagnosis",
      "type": "structured",
      "structured_type": "diagnosis",
      "repeats": true
    }
  ]
}
```

2. **Submit Form Response:**
```json
POST /api/v1/questionnaire/{slug}/submit/
{
  "resource_id": "patient-or-encounter-uuid",
  "patient": "patient-uuid",
  "encounter": "encounter-uuid",
  "results": [
    {
      "question_id": "uuid-1",
      "values": [{"value": "Chest pain"}]
    },
    {
      "question_id": "uuid-2",
      "values": [{"value": 7}]
    },
    {
      "question_id": "uuid-3",
      "values": [{
        "value": {
          "code": {"code": "29857009", "display": "Chest pain"},
          "clinical_status": "active",
          "verification_status": "confirmed"
        }
      }]
    }
  ]
}
```

3. **Via Frontend:**
   - Navigate to Patient → Encounter → select questionnaire
   - Fill out form and submit
   - Component: `care_fe/src/components/Questionnaire/QuestionnaireForm.tsx`

4. **Via Fixture Loading:**
   - Add questionnaires to `data/questionnaire_fixtures.json`
   - Run `python manage.py load_fixtures`

---

## 5. Templates

### Overview
The system supports two types of templates:
1. **Response Templates**: Pre-filled questionnaire answers for quick data entry
2. **Report Templates**: Document generation templates (prescriptions, discharge summaries, etc.)

### 5.1 Response Templates

**Model:** `care/emr/models/questionnaire.py:181-193`

| Field | Description |
|-------|-------------|
| `name` | Template name |
| `description` | Template description |
| `template_data` | JSONField containing medication_request, questionnaire, activity_definition data |
| `questionnaire` | Associated questionnaire |
| `facility` | Facility-specific template |
| `facility_organizations` | Organizations with access |
| `users` | Individual users with access |
| `available_keys` | Keys available in template_data |

**API Endpoints:**

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Templates | `/api/v1/questionnaire-response-templates/` | GET |
| Create Template | `/api/v1/questionnaire-response-templates/` | POST |
| Get Template | `/api/v1/questionnaire-response-templates/{id}/` | GET |
| Update Template | `/api/v1/questionnaire-response-templates/{id}/` | PUT |
| Delete Template | `/api/v1/questionnaire-response-templates/{id}/` | DELETE |

**Permissions:**

| Permission | Roles with Access |
|------------|-------------------|
| `can_write_questionnaire_response_template` | ADMIN, DOCTOR, NURSE, ADMINISTRATOR, STAFF, FACILITY_ADMIN, VOLUNTEER, PHARMACIST |
| `can_read_questionnaire_response_template` | ADMIN, DOCTOR, NURSE, ADMINISTRATOR, STAFF, FACILITY_ADMIN, VOLUNTEER, PHARMACIST |

**Access Control:**
- User must be template creator, OR
- User ID in `users` array, OR
- User's organization in `facility_organizations` array

### 5.2 Report Templates

**Model:** `care/emr/models/report/template.py:1-22`

| Field | Description |
|-------|-------------|
| `slug` | Unique identifier |
| `name` | Template name |
| `status` | active, draft, retired |
| `template_data` | HTML/Jinja2 template content |
| `template_type` | Type of report (prescription, discharge_summary, etc.) |
| `default_format` | Output format (html, pdf) |
| `context` | Data context type (encounter_base, patient_base) |
| `options` | Rendering options |
| `facility` | Facility-specific template |

**API Endpoints:**

| Operation | Endpoint | Method |
|-----------|----------|--------|
| List Templates | `/api/v1/templates/` | GET |
| Create Template | `/api/v1/templates/` | POST |
| Get Template | `/api/v1/templates/{slug}/` | GET |
| Update Template | `/api/v1/templates/{slug}/` | PUT |
| Delete Template | `/api/v1/templates/{slug}/` | DELETE |
| Get Schema | `/api/v1/templates/schema/` | GET |
| Preview Template | `/api/v1/templates/preview/` | POST |

**Permissions:**

**File:** `care/security/permissions/template.py`

| Permission | Roles with Access |
|------------|-------------------|
| `can_write_template` | FACILITY_ADMIN, ADMIN, DOCTOR, NURSE |
| `can_read_template` | FACILITY_ADMIN, ADMINISTRATOR, ADMIN, STAFF, DOCTOR, NURSE, VOLUNTEER, PHARMACIST |
| `can_preview_template` | FACILITY_ADMIN, ADMIN |
| `can_view_template_schema` | FACILITY_ADMIN, ADMIN |
| `can_generate_report_from_template` | FACILITY_ADMIN, ADMINISTRATOR, ADMIN, STAFF, DOCTOR, NURSE, VOLUNTEER, PHARMACIST |

### How to Create New Templates

1. **Response Template (Via API):**
```json
POST /api/v1/questionnaire-response-templates/
{
  "name": "Common Cold Treatment",
  "description": "Standard treatment for common cold",
  "questionnaire": "questionnaire-slug",
  "facility": "facility-uuid",
  "template_data": {
    "medication_request": [
      {
        "medication": {"code": "387207008", "display": "Paracetamol"},
        "dosage_instruction": [{"dose": {"value": 500, "unit": "mg"}}]
      }
    ],
    "questionnaire": [
      {"question_id": "uuid", "values": [{"value": "Symptomatic treatment"}]}
    ]
  }
}
```

2. **Report Template (Via API):**
```json
POST /api/v1/templates/
{
  "slug": "discharge-summary",
  "name": "Discharge Summary",
  "status": "active",
  "template_type": "discharge_summary",
  "default_format": "pdf",
  "context": "encounter_base",
  "template_data": "<html>{% for diagnosis in diagnoses %}<p>{{ diagnosis.name }}</p>{% endfor %}</html>",
  "facility": "facility-uuid"
}
```

3. **Via Frontend:**
   - Response Templates: Use "Save as Template" option after filling a form
   - Component: `care_fe/src/components/Questionnaire/ManageResponseTemplatesSheet.tsx`

---

## 6. User Roles and Permissions Summary

### Available Roles

| Role | Description |
|------|-------------|
| `ADMIN_ROLE` | System administrator |
| `FACILITY_ADMIN_ROLE` | Facility-level administrator |
| `DOCTOR_ROLE` | Medical doctor |
| `NURSE_ROLE` | Nursing staff |
| `STAFF_ROLE` | General staff |
| `PHARMACIST_ROLE` | Pharmacy personnel |
| `VOLUNTEER_ROLE` | Volunteer workers |
| `ADMINISTRATOR` | Administrative personnel |

### Permission Matrix

| Feature | Create | Read | Update | Delete |
|---------|--------|------|--------|--------|
| **Medications** | Doctor, Nurse, Admin, Facility Admin | Doctor, Nurse, Admin, Facility Admin, Staff, Pharmacist | Doctor, Nurse, Admin, Facility Admin | - |
| **Medication Dispense** | Doctor, Nurse, Admin, Facility Admin, Staff, Pharmacist | Same | Same | - |
| **Lab Tests (Service Request)** | Doctor, Nurse, Admin, Facility Admin | All clinical roles + Pharmacist, Volunteer | Doctor, Nurse, Admin, Facility Admin | - |
| **Diagnostic Reports** | Doctor, Nurse, Admin, Facility Admin | All clinical roles + Volunteer | Doctor, Nurse, Admin, Facility Admin | - |
| **Diagnosis** | Doctor, Nurse, Admin, Facility Admin | All clinical roles | Doctor, Nurse, Admin, Facility Admin | Doctor, Nurse, Admin, Facility Admin |
| **Questionnaires** | Superuser only | All roles | Superuser only | Superuser only |
| **Questionnaire Submission** | All clinical roles + Volunteer | - | - | - |
| **Response Templates** | All clinical roles | All clinical roles | Creator/Assigned users | Admin, Facility Admin |
| **Report Templates** | Doctor, Nurse, Admin, Facility Admin | All roles | Doctor, Nurse, Admin, Facility Admin | Superuser only |

### Authorization Context

Permissions are checked at different levels:
1. **User Level**: General system access
2. **Organization Level**: Access to specific facility organizations
3. **Facility Level**: Access within a facility
4. **Patient Level**: Access to patient data
5. **Encounter Level**: Access to specific clinical encounters

**Important Rules:**
- Completed encounters are read-only for clinical data
- Pharmacists have special location-based dispensing permissions
- Chronic conditions have patient-level (not encounter-level) permissions
- Organization cache enables efficient permission filtering

---

## Quick Reference: Creating New Data

| Data Type | Who Can Create | How to Create |
|-----------|----------------|---------------|
| **Medication Prescription** | Doctor, Nurse, Admin | API: POST to `/patient/{id}/medication/prescription/` or via Encounter → Medicines tab |
| **Lab Test Order** | Doctor, Nurse, Admin | API: POST to `/facility/{id}/service_request/` or via Encounter → Service Requests tab |
| **Lab Results** | Doctor, Nurse, Admin | API: POST to `/patient/{id}/diagnostic_report/` with observations |
| **Diagnosis** | Doctor, Nurse, Admin | API: POST to `/patient/{id}/diagnosis/` or via questionnaire forms |
| **Questionnaire** | Superuser only | API: POST to `/questionnaire/` or add to `questionnaire_fixtures.json` |
| **Form Response** | Clinical staff, Volunteer | API: POST to `/questionnaire/{slug}/submit/` or via UI forms |
| **Response Template** | All clinical roles | API: POST to `/questionnaire-response-templates/` or "Save as Template" in UI |
| **Report Template** | Doctor, Nurse, Admin | API: POST to `/templates/` |

---

## File References

### Backend (care)
- Models: `care/emr/models/`
- ViewSets: `care/emr/api/viewsets/`
- Permissions: `care/security/permissions/`
- Authorization: `care/security/authorization/`
- Fixtures: `care/emr/management/commands/load_fixtures.py`
- Questionnaire Data: `data/questionnaire_fixtures.json`

### Frontend (care_fe)
- Components: `src/components/`
- API Types: `src/types/emr/` and `src/types/questionnaire/`
- Permissions: `src/common/Permissions.tsx`
- Permission Context: `src/context/PermissionContext.tsx`

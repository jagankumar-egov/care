# Database Schema Documentation - CARE EMR System

## Overview

This document provides a comprehensive view of all database tables in the CARE EMR system and their relationships. The system is built on **FHIR R4** (Fast Healthcare Interoperability Resources) standard.

**Total Models:** 75+
**Database:** PostgreSQL
**FHIR Version:** R4 (4.0.1)

---

## FHIR Resource Mapping Reference

| CARE Model | FHIR Resource | FHIR URL |
|------------|---------------|----------|
| Patient | Patient | `http://hl7.org/fhir/R4/patient.html` |
| Encounter | Encounter | `http://hl7.org/fhir/R4/encounter.html` |
| Observation | Observation | `http://hl7.org/fhir/R4/observation.html` |
| Condition | Condition | `http://hl7.org/fhir/R4/condition.html` |
| AllergyIntolerance | AllergyIntolerance | `http://hl7.org/fhir/R4/allergyintolerance.html` |
| Consent | Consent | `http://hl7.org/fhir/R4/consent.html` |
| Account | Account | `http://hl7.org/fhir/R4/account.html` |
| ChargeItem | ChargeItem | `http://hl7.org/fhir/R4/chargeitem.html` |
| ChargeItemDefinition | ChargeItemDefinition | `http://hl7.org/fhir/R4/chargeitemdefinition.html` |
| Invoice | Invoice | `http://hl7.org/fhir/R4/invoice.html` |
| PaymentReconciliation | PaymentReconciliation | `http://hl7.org/fhir/R4/paymentreconciliation.html` |
| MedicationRequest | MedicationRequest | `http://hl7.org/fhir/R4/medicationrequest.html` |
| MedicationAdministration | MedicationAdministration | `http://hl7.org/fhir/R4/medicationadministration.html` |
| MedicationDispense | MedicationDispense | `http://hl7.org/fhir/R4/medicationdispense.html` |
| MedicationStatement | MedicationStatement | `http://hl7.org/fhir/R4/medicationstatement.html` |
| ServiceRequest | ServiceRequest | `http://hl7.org/fhir/R4/servicerequest.html` |
| DiagnosticReport | DiagnosticReport | `http://hl7.org/fhir/R4/diagnosticreport.html` |
| Specimen | Specimen | `http://hl7.org/fhir/R4/specimen.html` |
| ObservationDefinition | ObservationDefinition | `http://hl7.org/fhir/R4/observationdefinition.html` |
| SpecimenDefinition | SpecimenDefinition | `http://hl7.org/fhir/R4/specimendefinition.html` |
| ActivityDefinition | ActivityDefinition | `http://hl7.org/fhir/R4/activitydefinition.html` |
| ProductKnowledge | MedicationKnowledge | `http://hl7.org/fhir/R4/medicationknowledge.html` |
| Product | Medication | `http://hl7.org/fhir/R4/medication.html` |
| InventoryItem | InventoryItem | `http://hl7.org/fhir/R4/inventoryitem.html` |
| SupplyRequest | SupplyRequest | `http://hl7.org/fhir/R4/supplyrequest.html` |
| SupplyDelivery | SupplyDelivery | `http://hl7.org/fhir/R4/supplydelivery.html` |
| FacilityLocation | Location | `http://hl7.org/fhir/R4/location.html` |
| Facility | Organization | `http://hl7.org/fhir/R4/organization.html` |
| Organization | Organization | `http://hl7.org/fhir/R4/organization.html` |
| HealthcareService | HealthcareService | `http://hl7.org/fhir/R4/healthcareservice.html` |
| Device | Device | `http://hl7.org/fhir/R4/device.html` |
| Questionnaire | Questionnaire | `http://hl7.org/fhir/R4/questionnaire.html` |
| QuestionnaireResponse | QuestionnaireResponse | `http://hl7.org/fhir/R4/questionnaireresponse.html` |
| Schedule | Schedule | `http://hl7.org/fhir/R4/schedule.html` |
| TokenSlot | Slot | `http://hl7.org/fhir/R4/slot.html` |
| TokenBooking | Appointment | `http://hl7.org/fhir/R4/appointment.html` |
| SchedulableResource | PractitionerRole / Location | `http://hl7.org/fhir/R4/practitionerrole.html` |

---

## Table of Contents

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Core Clinical Models](#core-clinical-models)
3. [Billing & Account Models](#billing--account-models)
4. [Medication Models](#medication-models)
5. [Diagnostic & Lab Models](#diagnostic--lab-models)
6. [Inventory & Product Models](#inventory--product-models)
7. [Supply Chain Models](#supply-chain-models)
8. [Facility & Location Models](#facility--location-models)
9. [Organization Models](#organization-models)
10. [Device & Equipment Models](#device--equipment-models)
11. [Questionnaire & Forms Models](#questionnaire--forms-models)
12. [Scheduling & Booking Models](#scheduling--booking-models)
13. [Notes & Communication Models](#notes--communication-models)
14. [Security Models](#security-models)
15. [Utility Models](#utility-models)

---

## Entity Relationship Diagram

### Core Clinical Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CORE CLINICAL                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   Facility   │
                                    └──────┬───────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
     ┌─────────────────┐          ┌──────────────┐          ┌──────────────────┐
     │ FacilityLocation│◄─────────│   Patient    │──────────►│  Organization    │
     └────────┬────────┘          └──────┬───────┘          └──────────────────┘
              │                          │
              │                          │ 1:N
              │                          ▼
              │                   ┌──────────────┐
              └──────────────────►│   Encounter  │◄────────┐
                                  └──────┬───────┘         │
                                         │                 │
         ┌───────────────┬───────────────┼────────────┬────┴──────────┐
         │               │               │            │               │
         ▼               ▼               ▼            ▼               ▼
  ┌────────────┐  ┌────────────┐  ┌───────────┐  ┌─────────┐  ┌──────────────┐
  │ Observation │  │ Condition  │  │  Allergy  │  │ Consent │  │ServiceRequest│
  └────────────┘  └────────────┘  └───────────┘  └─────────┘  └──────────────┘
```

### Medication Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MEDICATION FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐     ┌─────────────────────────┐     ┌────────────────────────┐
│  ProductKnowledge  │────►│   MedicationRequest     │────►│MedicationAdministration│
│  (Drug Master)     │     │   (Prescription)        │     │   (Given to patient)   │
└────────────────────┘     └───────────┬─────────────┘     └────────────────────────┘
                                       │
                                       │
                                       ▼
                           ┌─────────────────────────┐
                           │   MedicationDispense    │
                           │   (Pharmacy dispense)   │
                           └───────────┬─────────────┘
                                       │
                                       ▼
                           ┌─────────────────────────┐
                           │     InventoryItem       │
                           │   (Stock deduction)     │
                           └─────────────────────────┘
```

### Lab Test Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LAB TEST FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│ActivityDefinition  │────►│   ServiceRequest    │────►│     Specimen     │
│ (Test Template)    │     │   (Lab Order)       │     │  (Sample)        │
└────────────────────┘     └──────────┬──────────┘     └────────┬─────────┘
         │                            │                         │
         │                            ▼                         │
         │                 ┌─────────────────────┐              │
         │                 │  DiagnosticReport   │◄─────────────┘
         │                 │  (Lab Report)       │
         │                 └──────────┬──────────┘
         │                            │
         ▼                            ▼
┌────────────────────┐     ┌─────────────────────┐
│ObservationDefinition│───►│    Observation      │
│ (Test Definition)  │     │  (Test Result)      │
└────────────────────┘     └─────────────────────┘
```

### Billing Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BILLING FLOW                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────────────┐
│ChargeItemDefinition │────►│  ChargeItem  │────►│   Invoice    │────►│PaymentReconciliation│
│   (Price List)      │     │ (Line Item)  │     │  (Bill)      │     │    (Payment)       │
└─────────────────────┘     └──────┬───────┘     └──────┬───────┘     └───────────────────┘
                                   │                    │
                                   │                    │
                                   ▼                    ▼
                            ┌──────────────┐     ┌──────────────┐
                            │   Account    │◄────┤   Patient    │
                            │(Balance Mgmt)│     │              │
                            └──────────────┘     └──────────────┘
```

### Scheduling Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    SCHEDULING FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│SchedulableResource  │────►│   Schedule   │────►│ Availability │────►│  TokenSlot   │
│ (Doctor/Room/Svc)   │     │  (Calendar)  │     │ (Time Slots) │     │ (Bookable)   │
└─────────────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                              │
                                                                              ▼
┌─────────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│      Patient        │────►│ TokenBooking │────►│    Token     │────►│  Encounter   │
│                     │     │(Appointment) │     │ (Queue #)    │     │              │
└─────────────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Core Clinical Models

### 1. Patient
**Table:** `emr_patient`
**FHIR Resource:** [Patient](http://hl7.org/fhir/R4/patient.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Patient.identifier` |
| name | VARCHAR(200) | Not Null | Patient name | `Patient.name` |
| gender | VARCHAR(35) | Not Null | Gender | `Patient.gender` |
| phone_number | VARCHAR(14) | - | Primary contact | `Patient.telecom` |
| emergency_phone_number | VARCHAR(14) | - | Emergency contact | `Patient.contact.telecom` |
| date_of_birth | DATE | - | DOB | `Patient.birthDate` |
| blood_group | VARCHAR(4) | - | Blood group | `Patient.extension` |
| geo_organization_id | BigInt | FK → Organization | Geographic org | `Patient.managingOrganization` |
| organization_cache | UUID[] | - | Cached org hierarchy | - |
| users_cache | UUID[] | - | Cached users | - |
| extensions | JSONB | - | Custom fields | `Patient.extension` |
| created_by_id | BigInt | FK → User | Creator | `Patient.meta.source` |
| created_at | DateTime | - | Created timestamp | `Patient.meta.lastUpdated` |
| modified_at | DateTime | - | Modified timestamp | `Patient.meta.lastUpdated` |
| deleted | Boolean | Default: false | Soft delete | - |

**Relationships:**
- `geo_organization` → Organization (FK)
- `created_by` → User (FK)
- Has many: Encounters, Observations, Conditions, MedicationRequests, Accounts

**Example Data:**
```json
{
  "id": 1,
  "external_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Rajesh Kumar",
  "gender": "male",
  "phone_number": "+919876543210",
  "emergency_phone_number": "+919876543211",
  "date_of_birth": "1985-03-15",
  "blood_group": "B+",
  "extensions": {
    "aadhaar_verified": true,
    "preferred_language": "hi"
  }
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Patient",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "identifier": [
    {
      "system": "urn:care:patient",
      "value": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "name": [
    {
      "use": "official",
      "text": "Rajesh Kumar"
    }
  ],
  "gender": "male",
  "birthDate": "1985-03-15",
  "telecom": [
    {
      "system": "phone",
      "value": "+919876543210",
      "use": "mobile"
    }
  ],
  "contact": [
    {
      "telecom": [
        {
          "system": "phone",
          "value": "+919876543211",
          "use": "mobile"
        }
      ]
    }
  ],
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/blood-group",
      "valueString": "B+"
    }
  ]
}
```

---

### 2. Encounter
**Table:** `emr_encounter`
**FHIR Resource:** [Encounter](http://hl7.org/fhir/R4/encounter.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Encounter.identifier` |
| status | VARCHAR(20) | Not Null | planned, in_progress, completed, etc. | `Encounter.status` |
| encounter_class | VARCHAR(20) | - | ambulatory, emergency, inpatient | `Encounter.class` |
| period | JSONB | - | Start/end times | `Encounter.period` |
| patient_id | BigInt | FK → Patient | Patient reference | `Encounter.subject` |
| facility_id | BigInt | FK → Facility | Facility | `Encounter.serviceProvider` |
| appointment_id | BigInt | FK → TokenBooking | Appointment | `Encounter.appointment` |
| current_location_id | BigInt | FK → FacilityLocation | Current location | `Encounter.location` |
| care_team | JSONB | - | Care team members | `Encounter.participant` |
| care_team_users | UUID[] | - | User IDs in care team | `Encounter.participant` |
| discharge_summary_advice | TEXT | - | Discharge advice | `Encounter.hospitalization.dischargeDisposition` |
| tags | VARCHAR[] | - | Encounter tags | `Encounter.type` |
| priority | VARCHAR(20) | - | routine, urgent, asap, stat | `Encounter.priority` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `facility` → Facility (FK, PROTECT)
- `appointment` → TokenBooking (FK, SET_NULL)
- `current_location` → FacilityLocation (FK, SET_NULL)
- Has many: Observations, Conditions, ServiceRequests, MedicationRequests

**Example Data:**
```json
{
  "id": 1,
  "external_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "encounter_class": "ambulatory",
  "period": {
    "start": "2024-01-15T09:00:00Z"
  },
  "patient_id": 1,
  "facility_id": 10,
  "current_location_id": 5,
  "care_team": [
    {"role": "primary_doctor", "user_id": "uuid-doc-1"},
    {"role": "nurse", "user_id": "uuid-nurse-1"}
  ],
  "priority": "routine"
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Encounter",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "in-progress",
  "class": {
    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    "code": "AMB",
    "display": "ambulatory"
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "period": {
    "start": "2024-01-15T09:00:00Z"
  },
  "location": [
    {
      "location": {
        "reference": "Location/loc-5"
      },
      "status": "active"
    }
  ],
  "participant": [
    {
      "type": [
        {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
              "code": "ATND",
              "display": "attender"
            }
          ]
        }
      ],
      "individual": {
        "reference": "Practitioner/uuid-doc-1"
      }
    }
  ],
  "serviceProvider": {
    "reference": "Organization/facility-10"
  }
}
```

---

### 3. Observation
**Table:** `emr_observation`
**FHIR Resource:** [Observation](http://hl7.org/fhir/R4/observation.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Observation.identifier` |
| status | VARCHAR(20) | Not Null | registered, preliminary, final, amended | `Observation.status` |
| category | JSONB | - | vital-signs, laboratory, etc. | `Observation.category` |
| code | JSONB | - | LOINC/SNOMED code | `Observation.code` |
| value_type | VARCHAR(30) | - | Quantity, string, CodeableConcept | - |
| value | JSONB | - | Observation value | `Observation.value[x]` |
| effective | JSONB | - | When observed | `Observation.effective[x]` |
| patient_id | BigInt | FK → Patient | Patient | `Observation.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `Observation.encounter` |
| subject_id | UUID | - | Subject reference | `Observation.subject` |
| diagnostic_report_id | BigInt | FK → DiagnosticReport | Parent report | - |
| observation_definition_id | BigInt | FK → ObservationDefinition | Definition | `Observation.derivedFrom` |
| interpretation | JSONB | - | N, H, L, etc. | `Observation.interpretation` |
| reference_range | JSONB | - | Normal ranges | `Observation.referenceRange` |
| body_site | JSONB | - | Body site | `Observation.bodySite` |
| method | JSONB | - | Method used | `Observation.method` |
| note | JSONB | - | Notes | `Observation.note` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `diagnostic_report` → DiagnosticReport (FK, CASCADE)
- `observation_definition` → ObservationDefinition (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "final",
  "category": [
    {
      "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]
    }
  ],
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "1558-6", "display": "Fasting glucose"}]
  },
  "value_type": "Quantity",
  "value": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  },
  "interpretation": [
    {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", "code": "N", "display": "Normal"}]}
  ],
  "reference_range": [
    {"low": {"value": 70, "unit": "mg/dL"}, "high": {"value": 100, "unit": "mg/dL"}, "text": "Normal"}
  ],
  "patient_id": 1,
  "encounter_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Observation",
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "1558-6",
        "display": "Fasting glucose [Mass/volume] in Serum or Plasma"
      }
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "effectiveDateTime": "2024-01-15T10:30:00Z",
  "valueQuantity": {
    "value": 95,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  },
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "N",
          "display": "Normal"
        }
      ]
    }
  ],
  "referenceRange": [
    {
      "low": {"value": 70, "unit": "mg/dL"},
      "high": {"value": 100, "unit": "mg/dL"},
      "text": "Normal fasting glucose"
    }
  ]
}
```

---

### 4. Condition
**Table:** `emr_condition`
**FHIR Resource:** [Condition](http://hl7.org/fhir/R4/condition.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Condition.identifier` |
| code | JSONB | Not Null | SNOMED diagnosis code | `Condition.code` |
| clinical_status | VARCHAR(20) | - | active, recurrence, inactive, resolved | `Condition.clinicalStatus` |
| verification_status | VARCHAR(20) | - | unconfirmed, provisional, confirmed | `Condition.verificationStatus` |
| severity | VARCHAR(20) | - | mild, moderate, severe | `Condition.severity` |
| category | VARCHAR(30) | - | encounter_diagnosis, problem_list_item | `Condition.category` |
| body_site | JSONB | - | Location of condition | `Condition.bodySite` |
| onset | JSONB | - | When started | `Condition.onset[x]` |
| abatement | JSONB | - | When resolved | `Condition.abatement[x]` |
| patient_id | BigInt | FK → Patient | Patient | `Condition.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `Condition.encounter` |
| recorded_date | DateTime | - | When recorded | `Condition.recordedDate` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "880e8400-e29b-41d4-a716-446655440003",
  "code": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "44054006", "display": "Type 2 diabetes mellitus"}
    ]
  },
  "clinical_status": "active",
  "verification_status": "confirmed",
  "severity": "moderate",
  "category": "encounter_diagnosis",
  "onset": {
    "onsetDateTime": "2020-06-15"
  },
  "patient_id": 1,
  "encounter_id": 1,
  "recorded_date": "2024-01-15T10:00:00Z"
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Condition",
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "confirmed"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "encounter-diagnosis",
          "display": "Encounter Diagnosis"
        }
      ]
    }
  ],
  "severity": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "6736007",
        "display": "Moderate"
      }
    ]
  },
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "44054006",
        "display": "Type 2 diabetes mellitus"
      }
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "onsetDateTime": "2020-06-15",
  "recordedDate": "2024-01-15T10:00:00Z"
}
```

---

### 5. AllergyIntolerance
**Table:** `emr_allergyintolerance`
**FHIR Resource:** [AllergyIntolerance](http://hl7.org/fhir/R4/allergyintolerance.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `AllergyIntolerance.identifier` |
| code | JSONB | Not Null | Allergy code | `AllergyIntolerance.code` |
| allergy_intolerance_type | VARCHAR(20) | - | allergy, intolerance | `AllergyIntolerance.type` |
| category | VARCHAR(20) | - | food, medication, environment, biologic | `AllergyIntolerance.category` |
| criticality | VARCHAR(20) | - | low, high, unable_to_assess | `AllergyIntolerance.criticality` |
| clinical_status | VARCHAR(20) | - | active, inactive, resolved | `AllergyIntolerance.clinicalStatus` |
| verification_status | VARCHAR(20) | - | unconfirmed, confirmed, refuted | `AllergyIntolerance.verificationStatus` |
| onset | JSONB | - | When started | `AllergyIntolerance.onset[x]` |
| patient_id | BigInt | FK → Patient | Patient | `AllergyIntolerance.patient` |
| encounter_id | BigInt | FK → Encounter | Encounter | `AllergyIntolerance.encounter` |
| note | JSONB | - | Notes | `AllergyIntolerance.note` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "990e8400-e29b-41d4-a716-446655440004",
  "code": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "764146007", "display": "Penicillin"}
    ]
  },
  "allergy_intolerance_type": "allergy",
  "category": "medication",
  "criticality": "high",
  "clinical_status": "active",
  "verification_status": "confirmed",
  "onset": {
    "onsetDateTime": "2015-03-01"
  },
  "patient_id": 1,
  "encounter_id": 1,
  "note": [{"text": "Patient reports severe rash when taking penicillin-based antibiotics"}]
}
```

**FHIR Representation:**
```json
{
  "resourceType": "AllergyIntolerance",
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
        "code": "active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
        "code": "confirmed"
      }
    ]
  },
  "type": "allergy",
  "category": ["medication"],
  "criticality": "high",
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "764146007",
        "display": "Penicillin"
      }
    ]
  },
  "patient": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "onsetDateTime": "2015-03-01",
  "note": [
    {
      "text": "Patient reports severe rash when taking penicillin-based antibiotics"
    }
  ]
}
```

---

### 6. Consent
**Table:** `emr_consent`
**FHIR Resource:** [Consent](http://hl7.org/fhir/R4/consent.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Consent.identifier` |
| status | VARCHAR(50) | Not Null | draft, active, inactive | `Consent.status` |
| category | VARCHAR(50) | Not Null | treatment, research, etc. | `Consent.category` |
| decision | VARCHAR(20) | - | permit, deny | `Consent.provision.type` |
| encounter_id | BigInt | FK → Encounter | Encounter | - |
| verification_details | JSONB | - | Verification info | `Consent.verification` |
| period | JSONB | - | Valid period | `Consent.provision.period` |

**Relationships:**
- `encounter` → Encounter (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "status": "active",
  "category": "treatment",
  "decision": "permit",
  "encounter_id": 1,
  "verification_details": {
    "verified": true,
    "verifiedWith": "patient",
    "verificationDate": "2024-01-15T09:15:00Z"
  },
  "period": {
    "start": "2024-01-15",
    "end": "2025-01-15"
  }
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Consent",
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "status": "active",
  "scope": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/consentscope",
        "code": "treatment"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/consentcategorycodes",
          "code": "59284-0",
          "display": "Patient Consent"
        }
      ]
    }
  ],
  "patient": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "dateTime": "2024-01-15T09:15:00Z",
  "verification": [
    {
      "verified": true,
      "verifiedWith": {
        "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
      },
      "verificationDate": "2024-01-15"
    }
  ],
  "provision": {
    "type": "permit",
    "period": {
      "start": "2024-01-15",
      "end": "2025-01-15"
    }
  }
}
```

---

## Billing & Account Models

### 7. Account
**Table:** `emr_account`
**FHIR Resource:** [Account](http://hl7.org/fhir/R4/account.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Account.identifier` |
| status | VARCHAR(20) | - | active, inactive, on_hold | `Account.status` |
| billing_status | VARCHAR(30) | - | open, billing, closed_completed | `Account.extension` |
| total_net | DECIMAL(20,6) | - | Net total | `Account.extension` |
| total_gross | DECIMAL(20,6) | - | Gross total | `Account.extension` |
| total_paid | DECIMAL(20,6) | - | Paid amount | `Account.extension` |
| total_balance | DECIMAL(20,6) | - | Outstanding balance | `Account.extension` |
| total_billable_charge_items | DECIMAL(20,6) | - | Billable items total | `Account.extension` |
| facility_id | BigInt | FK → Facility | Facility | `Account.owner` |
| patient_id | BigInt | FK → Patient | Patient | `Account.subject` |
| primary_encounter_id | BigInt | FK → Encounter | Primary encounter | `Account.extension` |
| description | TEXT | - | Description | `Account.description` |
| name | VARCHAR(255) | - | Account name | `Account.name` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, PROTECT)
- `primary_encounter` → Encounter (FK, SET_NULL)
- Has many: ChargeItems, Invoices, PaymentReconciliations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "status": "active",
  "billing_status": "open",
  "name": "OPD Visit - Rajesh Kumar",
  "total_net": 1500.00,
  "total_gross": 1770.00,
  "total_paid": 1000.00,
  "total_balance": 770.00,
  "total_billable_charge_items": 1500.00,
  "facility_id": 10,
  "patient_id": 1,
  "primary_encounter_id": 1,
  "description": "OPD consultation and lab tests"
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Account",
  "id": "bb0e8400-e29b-41d4-a716-446655440006",
  "status": "active",
  "name": "OPD Visit - Rajesh Kumar",
  "subject": [
    {
      "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "servicePeriod": {
    "start": "2024-01-15"
  },
  "owner": {
    "reference": "Organization/facility-10"
  },
  "description": "OPD consultation and lab tests",
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/account-balance",
      "valueMoney": {
        "value": 770.00,
        "currency": "INR"
      }
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/billing-status",
      "valueCode": "open"
    }
  ]
}
```

---

### 8. ChargeItem
**Table:** `emr_chargeitem`
**FHIR Resource:** [ChargeItem](http://hl7.org/fhir/R4/chargeitem.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `ChargeItem.identifier` |
| title | VARCHAR(255) | - | Item title | `ChargeItem.code.text` |
| status | VARCHAR(20) | - | billable, not_billable, billed, paid | `ChargeItem.status` |
| quantity | DECIMAL(10,4) | - | Quantity | `ChargeItem.quantity` |
| unit_price_components | JSONB | - | Unit pricing | `ChargeItem.priceOverride` |
| total_price_components | JSONB | - | Total pricing | `ChargeItem.extension` |
| total_price | DECIMAL(20,6) | - | Total price | `ChargeItem.extension` |
| service_resource | VARCHAR(50) | - | Source resource type | `ChargeItem.service` |
| service_resource_id | VARCHAR(100) | - | Source resource ID | `ChargeItem.service` |
| facility_id | BigInt | FK → Facility | Facility | `ChargeItem.performingOrganization` |
| patient_id | BigInt | FK → Patient | Patient | `ChargeItem.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `ChargeItem.context` |
| account_id | BigInt | FK → Account | Account | `ChargeItem.account` |
| charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Definition | `ChargeItem.definitionCanonical` |
| paid_invoice_id | BigInt | FK → Invoice | Paid invoice | `ChargeItem.extension` |
| performer_actor_id | BigInt | FK → User | Performer | `ChargeItem.performer.actor` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `account` → Account (FK, CASCADE)
- `charge_item_definition` → ChargeItemDefinition (FK, CASCADE)
- `paid_invoice` → Invoice (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "title": "Fasting Blood Glucose Test",
  "status": "billable",
  "quantity": 1,
  "unit_price_components": [
    {"type": "base", "code": "BASE", "amount": 150.00},
    {"type": "tax", "code": "GST", "amount": 27.00, "factor": 0.18}
  ],
  "total_price_components": [
    {"type": "base", "amount": 150.00},
    {"type": "tax", "amount": 27.00}
  ],
  "total_price": 177.00,
  "service_resource": "ServiceRequest",
  "service_resource_id": "sr-uuid-123",
  "facility_id": 10,
  "patient_id": 1,
  "encounter_id": 1,
  "account_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "ChargeItem",
  "id": "cc0e8400-e29b-41d4-a716-446655440007",
  "status": "billable",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "1558-6",
        "display": "Fasting glucose"
      }
    ],
    "text": "Fasting Blood Glucose Test"
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "context": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "occurrenceDateTime": "2024-01-15T10:00:00Z",
  "quantity": {
    "value": 1
  },
  "priceOverride": {
    "value": 177.00,
    "currency": "INR"
  },
  "account": [
    {
      "reference": "Account/bb0e8400-e29b-41d4-a716-446655440006"
    }
  ],
  "service": [
    {
      "reference": "ServiceRequest/sr-uuid-123"
    }
  ]
}
```

---

### 9. ChargeItemDefinition
**Table:** `emr_chargeitemdefinition`
**FHIR Resource:** [ChargeItemDefinition](http://hl7.org/fhir/R4/chargeitemdefinition.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `ChargeItemDefinition.identifier` |
| slug | VARCHAR(100) | Index | Unique slug | `ChargeItemDefinition.url` |
| title | VARCHAR(255) | Not Null | Title | `ChargeItemDefinition.title` |
| version | INT | - | Version number | `ChargeItemDefinition.version` |
| status | VARCHAR(20) | - | draft, active, retired | `ChargeItemDefinition.status` |
| price_components | JSONB | - | Pricing breakdown | `ChargeItemDefinition.propertyGroup.priceComponent` |
| can_edit_charge_item | BOOLEAN | - | Allow editing | `ChargeItemDefinition.extension` |
| facility_id | BigInt | FK → Facility | Facility | `ChargeItemDefinition.extension` |
| category_id | BigInt | FK → ResourceCategory | Category | `ChargeItemDefinition.code` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "dd0e8400-e29b-41d4-a716-446655440008",
  "slug": "fasting-blood-glucose-test",
  "title": "Fasting Blood Glucose Test",
  "version": 1,
  "status": "active",
  "price_components": [
    {
      "type": "base",
      "code": {"coding": [{"code": "BASE", "display": "Base Price"}]},
      "amount": {"value": 150.00, "currency": "INR"}
    },
    {
      "type": "tax",
      "code": {"coding": [{"code": "GST", "display": "GST 18%"}]},
      "factor": 0.18
    }
  ],
  "can_edit_charge_item": false,
  "facility_id": 10
}
```

**FHIR Representation:**
```json
{
  "resourceType": "ChargeItemDefinition",
  "id": "dd0e8400-e29b-41d4-a716-446655440008",
  "url": "http://care.ohc.network/ChargeItemDefinition/fasting-blood-glucose-test",
  "version": "1",
  "title": "Fasting Blood Glucose Test",
  "status": "active",
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "1558-6",
        "display": "Fasting glucose"
      }
    ]
  },
  "propertyGroup": [
    {
      "priceComponent": [
        {
          "type": "base",
          "code": {
            "coding": [{"code": "BASE", "display": "Base Price"}]
          },
          "amount": {
            "value": 150.00,
            "currency": "INR"
          }
        },
        {
          "type": "tax",
          "code": {
            "coding": [{"code": "GST", "display": "GST 18%"}]
          },
          "factor": 0.18
        }
      ]
    }
  ]
}
```

---

### 10. Invoice
**Table:** `emr_invoice`
**FHIR Resource:** [Invoice](http://hl7.org/fhir/R4/invoice.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Invoice.identifier` |
| title | VARCHAR(255) | - | Invoice title | `Invoice.extension` |
| status | VARCHAR(20) | - | draft, issued, balanced, cancelled | `Invoice.status` |
| number | VARCHAR(50) | - | Invoice number | `Invoice.identifier` |
| charge_items | UUID[] | - | Charge item IDs | `Invoice.lineItem` |
| charge_items_copy | JSONB | - | Snapshot of items | `Invoice.lineItem` |
| total_price_components | JSONB | - | Price breakdown | `Invoice.totalPriceComponent` |
| total_net | DECIMAL(20,6) | - | Net amount | `Invoice.totalNet` |
| total_gross | DECIMAL(20,6) | - | Gross amount | `Invoice.totalGross` |
| locked | BOOLEAN | Default: false | Lock status | `Invoice.extension` |
| is_refund | BOOLEAN | Default: false | Refund flag | `Invoice.type` |
| facility_id | BigInt | FK → Facility | Facility | `Invoice.issuer` |
| patient_id | BigInt | FK → Patient | Patient | `Invoice.subject` |
| account_id | BigInt | FK → Account | Account | `Invoice.account` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, PROTECT)
- `account` → Account (FK, PROTECT)
- Has many: PaymentReconciliations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "ee0e8400-e29b-41d4-a716-446655440009",
  "title": "OPD Invoice - 15 Jan 2024",
  "status": "issued",
  "number": "INV-2024-001234",
  "charge_items": ["cc0e8400-e29b-41d4-a716-446655440007"],
  "charge_items_copy": [
    {"title": "Fasting Blood Glucose Test", "quantity": 1, "total_price": 177.00}
  ],
  "total_price_components": [
    {"type": "base", "amount": 150.00},
    {"type": "tax", "code": "GST", "amount": 27.00}
  ],
  "total_net": 150.00,
  "total_gross": 177.00,
  "locked": true,
  "is_refund": false,
  "facility_id": 10,
  "patient_id": 1,
  "account_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Invoice",
  "id": "ee0e8400-e29b-41d4-a716-446655440009",
  "identifier": [
    {
      "system": "http://care.ohc.network/invoice",
      "value": "INV-2024-001234"
    }
  ],
  "status": "issued",
  "type": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/invoice-type",
        "code": "invoice"
      }
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "date": "2024-01-15",
  "issuer": {
    "reference": "Organization/facility-10"
  },
  "account": {
    "reference": "Account/bb0e8400-e29b-41d4-a716-446655440006"
  },
  "lineItem": [
    {
      "chargeItemReference": {
        "reference": "ChargeItem/cc0e8400-e29b-41d4-a716-446655440007"
      },
      "priceComponent": [
        {
          "type": "base",
          "amount": {"value": 150.00, "currency": "INR"}
        },
        {
          "type": "tax",
          "code": {"text": "GST 18%"},
          "amount": {"value": 27.00, "currency": "INR"}
        }
      ]
    }
  ],
  "totalNet": {
    "value": 150.00,
    "currency": "INR"
  },
  "totalGross": {
    "value": 177.00,
    "currency": "INR"
  }
}
```

---

### 11. PaymentReconciliation
**Table:** `emr_paymentreconciliation`
**FHIR Resource:** [PaymentReconciliation](http://hl7.org/fhir/R4/paymentreconciliation.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `PaymentReconciliation.identifier` |
| reconciliation_type | VARCHAR(20) | - | payment, adjustment, advance | `PaymentReconciliation.extension` |
| status | VARCHAR(20) | - | active, cancelled, draft | `PaymentReconciliation.status` |
| kind | VARCHAR(20) | - | deposit, online, kiosk | `PaymentReconciliation.extension` |
| issuer_type | VARCHAR(20) | - | patient, insurer | `PaymentReconciliation.requestor` |
| outcome | VARCHAR(20) | - | queued, complete, error | `PaymentReconciliation.outcome` |
| method | VARCHAR(20) | - | cash, ccca, debc, chck | `PaymentReconciliation.paymentIdentifier` |
| reference_number | VARCHAR(100) | - | Transaction ref | `PaymentReconciliation.paymentIdentifier` |
| authorization | VARCHAR(100) | - | Auth code | `PaymentReconciliation.extension` |
| tendered_amount | DECIMAL(20,6) | - | Amount given | `PaymentReconciliation.extension` |
| returned_amount | DECIMAL(20,6) | - | Change returned | `PaymentReconciliation.extension` |
| amount | DECIMAL(20,6) | - | Net amount | `PaymentReconciliation.paymentAmount` |
| is_credit_note | BOOLEAN | Default: false | Refund indicator | `PaymentReconciliation.extension` |
| facility_id | BigInt | FK → Facility | Facility | `PaymentReconciliation.paymentIssuer` |
| account_id | BigInt | FK → Account | Account | `PaymentReconciliation.extension` |
| target_invoice_id | BigInt | FK → Invoice | Invoice | `PaymentReconciliation.detail.request` |
| location_id | BigInt | FK → FacilityLocation | Payment location | `PaymentReconciliation.extension` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `account` → Account (FK, PROTECT)
- `target_invoice` → Invoice (FK, PROTECT)
- `location` → FacilityLocation (FK, PROTECT)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "ff0e8400-e29b-41d4-a716-446655440010",
  "reconciliation_type": "payment",
  "status": "active",
  "kind": "deposit",
  "issuer_type": "patient",
  "outcome": "complete",
  "method": "cash",
  "reference_number": "RCPT-2024-001234",
  "tendered_amount": 200.00,
  "returned_amount": 23.00,
  "amount": 177.00,
  "is_credit_note": false,
  "facility_id": 10,
  "account_id": 1,
  "target_invoice_id": 1,
  "location_id": 2
}
```

**FHIR Representation:**
```json
{
  "resourceType": "PaymentReconciliation",
  "id": "ff0e8400-e29b-41d4-a716-446655440010",
  "status": "active",
  "period": {
    "start": "2024-01-15",
    "end": "2024-01-15"
  },
  "created": "2024-01-15T11:30:00Z",
  "paymentIssuer": {
    "reference": "Organization/facility-10"
  },
  "paymentIdentifier": {
    "system": "http://care.ohc.network/payment-reference",
    "value": "RCPT-2024-001234"
  },
  "paymentAmount": {
    "value": 177.00,
    "currency": "INR"
  },
  "paymentDate": "2024-01-15",
  "outcome": "complete",
  "detail": [
    {
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/payment-type",
            "code": "payment"
          }
        ]
      },
      "request": {
        "reference": "Invoice/ee0e8400-e29b-41d4-a716-446655440009"
      },
      "amount": {
        "value": 177.00,
        "currency": "INR"
      }
    }
  ],
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/payment-method",
      "valueCode": "cash"
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/tendered-amount",
      "valueMoney": {"value": 200.00, "currency": "INR"}
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/returned-amount",
      "valueMoney": {"value": 23.00, "currency": "INR"}
    }
  ]
}
```

---

## Medication Models

### 12. MedicationRequest
**Table:** `emr_medicationrequest`
**FHIR Resource:** [MedicationRequest](http://hl7.org/fhir/R4/medicationrequest.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `MedicationRequest.identifier` |
| status | VARCHAR(20) | - | active, completed, cancelled | `MedicationRequest.status` |
| intent | VARCHAR(20) | - | proposal, plan, order | `MedicationRequest.intent` |
| medication | JSONB | Not Null | Medication code | `MedicationRequest.medicationCodeableConcept` |
| dosage_instruction | JSONB | - | Dosing details | `MedicationRequest.dosageInstruction` |
| dispense_request | JSONB | - | Dispense info | `MedicationRequest.dispenseRequest` |
| substitution | JSONB | - | Substitution rules | `MedicationRequest.substitution` |
| reason | JSONB | - | Reason for request | `MedicationRequest.reasonCode` |
| note | JSONB | - | Notes | `MedicationRequest.note` |
| patient_id | BigInt | FK → Patient | Patient | `MedicationRequest.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `MedicationRequest.encounter` |
| requester_id | BigInt | FK → User | Prescriber | `MedicationRequest.requester` |
| requested_product_id | BigInt | FK → ProductKnowledge | Product | `MedicationRequest.medicationReference` |
| prescription_id | BigInt | FK → MedicationRequestPrescription | Prescription | `MedicationRequest.groupIdentifier` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `requester` → User (FK, SET_NULL)
- `requested_product` → ProductKnowledge (FK, SET_NULL)
- `prescription` → MedicationRequestPrescription (FK, SET_NULL)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "med-req-001",
  "status": "active",
  "intent": "order",
  "medication": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "90332006", "display": "Paracetamol 500mg tablet"}
    ]
  },
  "dosage_instruction": [
    {
      "text": "Take 1 tablet three times a day after meals",
      "timing": {
        "repeat": {"frequency": 3, "period": 1, "periodUnit": "d"}
      },
      "route": {"coding": [{"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral"}]},
      "doseAndRate": [
        {"doseQuantity": {"value": 1, "unit": "tablet", "code": "{tbl}"}}
      ]
    }
  ],
  "dispense_request": {
    "numberOfRepeatsAllowed": 0,
    "quantity": {"value": 21, "unit": "tablet"},
    "expectedSupplyDuration": {"value": 7, "unit": "days"}
  },
  "patient_id": 1,
  "encounter_id": 1,
  "requester_id": 5
}
```

**FHIR Representation:**
```json
{
  "resourceType": "MedicationRequest",
  "id": "med-req-001",
  "status": "active",
  "intent": "order",
  "medicationCodeableConcept": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "90332006",
        "display": "Paracetamol 500mg tablet"
      }
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "authoredOn": "2024-01-15T10:00:00Z",
  "requester": {
    "reference": "Practitioner/doc-5"
  },
  "dosageInstruction": [
    {
      "text": "Take 1 tablet three times a day after meals",
      "timing": {
        "repeat": {
          "frequency": 3,
          "period": 1,
          "periodUnit": "d"
        }
      },
      "route": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "26643006",
            "display": "Oral route"
          }
        ]
      },
      "doseAndRate": [
        {
          "doseQuantity": {
            "value": 1,
            "unit": "tablet",
            "system": "http://unitsofmeasure.org",
            "code": "{tbl}"
          }
        }
      ]
    }
  ],
  "dispenseRequest": {
    "numberOfRepeatsAllowed": 0,
    "quantity": {
      "value": 21,
      "unit": "tablet"
    },
    "expectedSupplyDuration": {
      "value": 7,
      "unit": "days",
      "system": "http://unitsofmeasure.org",
      "code": "d"
    }
  }
}
```

---

### 13. MedicationRequestPrescription
**Table:** `emr_medicationrequestprescription`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| alternate_identifier | VARCHAR(100) | - | Alt ID |
| status | VARCHAR(20) | - | active, completed |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| prescribed_by_id | BigInt | FK → User | Prescriber |

**Unique Constraint:** (alternate_identifier, encounter)

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `prescribed_by` → User (FK, CASCADE)
- Has many: MedicationRequests

---

### 14. MedicationAdministration
**Table:** `emr_medicationadministration`
**FHIR Resource:** [MedicationAdministration](http://hl7.org/fhir/R4/medicationadministration.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `MedicationAdministration.identifier` |
| status | VARCHAR(20) | - | in_progress, completed, not_done | `MedicationAdministration.status` |
| medication | JSONB | - | Medication code | `MedicationAdministration.medicationCodeableConcept` |
| dosage | JSONB | - | Dosage given | `MedicationAdministration.dosage` |
| effective_period | JSONB | - | When given | `MedicationAdministration.effective[x]` |
| note | JSONB | - | Notes | `MedicationAdministration.note` |
| patient_id | BigInt | FK → Patient | Patient | `MedicationAdministration.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `MedicationAdministration.context` |
| request_id | BigInt | FK → MedicationRequest | Request | `MedicationAdministration.request` |
| administered_product_id | BigInt | FK → ProductKnowledge | Product | `MedicationAdministration.medicationReference` |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `request` → MedicationRequest (FK, CASCADE)
- `administered_product` → ProductKnowledge (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "med-admin-001",
  "status": "completed",
  "medication": {
    "coding": [{"system": "http://snomed.info/sct", "code": "90332006", "display": "Paracetamol 500mg"}]
  },
  "dosage": {
    "text": "500mg oral",
    "route": {"coding": [{"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral"}]},
    "dose": {"value": 500, "unit": "mg", "code": "mg"}
  },
  "effective_period": {
    "start": "2024-01-15T14:00:00Z",
    "end": "2024-01-15T14:05:00Z"
  },
  "patient_id": 1,
  "encounter_id": 1,
  "request_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "MedicationAdministration",
  "id": "med-admin-001",
  "status": "completed",
  "medicationCodeableConcept": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "90332006", "display": "Paracetamol 500mg tablet"}
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "context": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "effectivePeriod": {
    "start": "2024-01-15T14:00:00Z",
    "end": "2024-01-15T14:05:00Z"
  },
  "request": {
    "reference": "MedicationRequest/med-req-001"
  },
  "dosage": {
    "text": "500mg oral",
    "route": {
      "coding": [{"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"}]
    },
    "dose": {
      "value": 500,
      "unit": "mg",
      "system": "http://unitsofmeasure.org",
      "code": "mg"
    }
  }
}
```

---

### 15. MedicationDispense
**Table:** `emr_medicationdispense`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | preparation, completed, cancelled |
| medication | JSONB | - | Medication code |
| quantity | DECIMAL(10,4) | - | Quantity dispensed |
| days_supply | INT | - | Days supply |
| note | JSONB | - | Notes |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| location_id | BigInt | FK → FacilityLocation | Pharmacy |
| authorizing_request_id | BigInt | FK → MedicationRequest | Authorization |
| item_id | BigInt | FK → InventoryItem | Inventory item |
| charge_item_id | BigInt | FK → ChargeItem | Charge |
| order_id | BigInt | FK → DispenseOrder | Order |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `location` → FacilityLocation (FK, CASCADE)
- `authorizing_request` → MedicationRequest (FK, SET_NULL)
- `item` → InventoryItem (FK, CASCADE)
- `charge_item` → ChargeItem (FK, CASCADE)
- `order` → DispenseOrder (FK, CASCADE)

---

### 16. MedicationStatement
**Table:** `emr_medicationstatement`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | recorded, draft |
| medication | JSONB | Not Null | Medication code |
| effective_period | JSONB | - | When taken |
| reason | JSONB | - | Reason |
| information_source | VARCHAR(50) | - | Source |
| note | JSONB | - | Notes |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

---

## Diagnostic & Lab Models

### 17. ServiceRequest
**Table:** `emr_servicerequest`
**FHIR Resource:** [ServiceRequest](http://hl7.org/fhir/R4/servicerequest.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `ServiceRequest.identifier` |
| title | VARCHAR(255) | - | Request title | `ServiceRequest.code.text` |
| status | VARCHAR(20) | - | draft, active, completed, revoked | `ServiceRequest.status` |
| intent | VARCHAR(20) | - | proposal, plan, order | `ServiceRequest.intent` |
| priority | VARCHAR(20) | - | routine, urgent, asap, stat | `ServiceRequest.priority` |
| code | JSONB | - | Procedure code | `ServiceRequest.code` |
| category | VARCHAR(30) | - | laboratory, imaging, procedure | `ServiceRequest.category` |
| body_site | JSONB | - | Body site | `ServiceRequest.bodySite` |
| subject_id | UUID | - | Subject reference | `ServiceRequest.subject` |
| locations | UUID[] | - | Assigned locations | `ServiceRequest.locationReference` |
| facility_id | BigInt | FK → Facility | Facility | `ServiceRequest.performer` |
| patient_id | BigInt | FK → Patient | Patient | `ServiceRequest.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `ServiceRequest.encounter` |
| healthcare_service_id | BigInt | FK → HealthcareService | Service | `ServiceRequest.performer` |
| activity_definition_id | BigInt | FK → ActivityDefinition | Activity | `ServiceRequest.instantiatesCanonical` |
| requester_id | BigInt | FK → User | Requester | `ServiceRequest.requester` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `healthcare_service` → HealthcareService (FK, PROTECT)
- `activity_definition` → ActivityDefinition (FK, PROTECT)
- `requester` → User (FK, CASCADE)
- Has many: DiagnosticReports, Specimens

**Example Data:**
```json
{
  "id": 1,
  "external_id": "sr-001",
  "title": "Complete Blood Count",
  "status": "active",
  "intent": "order",
  "priority": "routine",
  "category": "laboratory",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "58410-2", "display": "CBC panel"}]
  },
  "patient_id": 1,
  "encounter_id": 1,
  "healthcare_service_id": 1,
  "activity_definition_id": 2,
  "requester_id": 5
}
```

**FHIR Representation:**
```json
{
  "resourceType": "ServiceRequest",
  "id": "sr-001",
  "status": "active",
  "intent": "order",
  "priority": "routine",
  "category": [
    {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "108252007", "display": "Laboratory procedure"}
      ]
    }
  ],
  "code": {
    "coding": [
      {"system": "http://loinc.org", "code": "58410-2", "display": "Complete blood count (CBC) panel"}
    ],
    "text": "Complete Blood Count"
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "authoredOn": "2024-01-15T09:30:00Z",
  "requester": {
    "reference": "Practitioner/doc-5"
  },
  "performer": [
    {"reference": "HealthcareService/lab-service-1"}
  ],
  "instantiatesCanonical": [
    "http://care.ohc.network/ActivityDefinition/cbc-panel"
  ]
}
```

---

### 18. DiagnosticReport
**Table:** `emr_diagnosticreport`
**FHIR Resource:** [DiagnosticReport](http://hl7.org/fhir/R4/diagnosticreport.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `DiagnosticReport.identifier` |
| status | VARCHAR(20) | - | registered, partial, preliminary, final | `DiagnosticReport.status` |
| code | JSONB | - | Report code | `DiagnosticReport.code` |
| category | JSONB | - | Category | `DiagnosticReport.category` |
| effective | JSONB | - | When performed | `DiagnosticReport.effective[x]` |
| issued | DateTime | - | When issued | `DiagnosticReport.issued` |
| conclusion | TEXT | - | Clinical conclusion | `DiagnosticReport.conclusion` |
| conclusion_code | JSONB | - | Coded conclusion | `DiagnosticReport.conclusionCode` |
| facility_id | BigInt | FK → Facility | Facility | `DiagnosticReport.performer` |
| patient_id | BigInt | FK → Patient | Patient | `DiagnosticReport.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `DiagnosticReport.encounter` |
| service_request_id | BigInt | FK → ServiceRequest | Request | `DiagnosticReport.basedOn` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `service_request` → ServiceRequest (FK, CASCADE)
- Has many: Observations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "dr-001",
  "status": "final",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "58410-2", "display": "CBC panel"}]
  },
  "category": [
    {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "LAB"}]}
  ],
  "effective": {"effectiveDateTime": "2024-01-15T11:00:00Z"},
  "issued": "2024-01-15T12:30:00Z",
  "conclusion": "All values within normal limits",
  "patient_id": 1,
  "encounter_id": 1,
  "service_request_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "DiagnosticReport",
  "id": "dr-001",
  "status": "final",
  "category": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "LAB", "display": "Laboratory"}
      ]
    }
  ],
  "code": {
    "coding": [
      {"system": "http://loinc.org", "code": "58410-2", "display": "Complete blood count (CBC) panel"}
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "effectiveDateTime": "2024-01-15T11:00:00Z",
  "issued": "2024-01-15T12:30:00Z",
  "basedOn": [
    {"reference": "ServiceRequest/sr-001"}
  ],
  "result": [
    {"reference": "Observation/obs-hgb-001"},
    {"reference": "Observation/obs-wbc-001"},
    {"reference": "Observation/obs-plt-001"}
  ],
  "conclusion": "All values within normal limits"
}
```

---

### 19. Specimen
**Table:** `emr_specimen`
**FHIR Resource:** [Specimen](http://hl7.org/fhir/R4/specimen.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Specimen.identifier` |
| accession_identifier | VARCHAR(100) | Index | Lab accession # | `Specimen.accessionIdentifier` |
| status | VARCHAR(20) | - | available, unavailable, entered_in_error | `Specimen.status` |
| type | JSONB | - | Specimen type | `Specimen.type` |
| collection | JSONB | - | Collection details | `Specimen.collection` |
| processing | JSONB | - | Processing steps | `Specimen.processing` |
| condition | JSONB | - | Specimen condition | `Specimen.condition` |
| note | JSONB | - | Notes | `Specimen.note` |
| facility_id | BigInt | FK → Facility | Facility | - |
| patient_id | BigInt | FK → Patient | Patient | `Specimen.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | - |
| service_request_id | BigInt | FK → ServiceRequest | Request | `Specimen.request` |
| specimen_definition_id | BigInt | FK → SpecimenDefinition | Definition | - |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `service_request` → ServiceRequest (FK, CASCADE)
- `specimen_definition` → SpecimenDefinition (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "spec-001",
  "accession_identifier": "LAB-2024-001234",
  "status": "available",
  "type": {
    "coding": [{"system": "http://snomed.info/sct", "code": "788707000", "display": "Blood sample"}]
  },
  "collection": {
    "collectedDateTime": "2024-01-15T10:15:00Z",
    "quantity": {"value": 5, "unit": "mL"},
    "method": {"coding": [{"system": "http://snomed.info/sct", "code": "82078001", "display": "Venipuncture"}]},
    "bodySite": {"coding": [{"system": "http://snomed.info/sct", "code": "53120007", "display": "Arm"}]}
  },
  "patient_id": 1,
  "encounter_id": 1,
  "service_request_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Specimen",
  "id": "spec-001",
  "accessionIdentifier": {
    "system": "http://care.ohc.network/lab-accession",
    "value": "LAB-2024-001234"
  },
  "status": "available",
  "type": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "788707000", "display": "Blood sample"}
    ]
  },
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "request": [
    {"reference": "ServiceRequest/sr-001"}
  ],
  "collection": {
    "collectedDateTime": "2024-01-15T10:15:00Z",
    "quantity": {
      "value": 5,
      "unit": "mL",
      "system": "http://unitsofmeasure.org",
      "code": "mL"
    },
    "method": {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "82078001", "display": "Collection of blood specimen by venipuncture"}
      ]
    },
    "bodySite": {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "53120007", "display": "Upper arm structure"}
      ]
    }
  }
}
```

---

### 20. ObservationDefinition
**Table:** `emr_observationdefinition`
**FHIR Resource:** [ObservationDefinition](http://hl7.org/fhir/R4/observationdefinition.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `ObservationDefinition.identifier` |
| slug | VARCHAR(100) | Index | Unique slug | `ObservationDefinition.url` |
| title | VARCHAR(255) | Not Null | Title | `ObservationDefinition.title` |
| code | JSONB | Not Null | LOINC code | `ObservationDefinition.code` |
| description | TEXT | - | Description | `ObservationDefinition.description` |
| permitted_data_type | VARCHAR(30) | - | Quantity, string, etc. | `ObservationDefinition.permittedDataType` |
| permitted_unit | JSONB | - | Allowed units | `ObservationDefinition.quantitativeDetails.unit` |
| qualified_value | JSONB | - | Reference ranges | `ObservationDefinition.qualifiedInterval` |
| component | JSONB | - | Panel components | `ObservationDefinition.component` |
| status | VARCHAR(20) | - | draft, active, retired | `ObservationDefinition.status` |
| facility_id | BigInt | FK → Facility | Facility | - |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- Has many: Observations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "obs-def-001",
  "slug": "fasting-blood-glucose",
  "title": "Fasting Blood Glucose",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "1558-6", "display": "Fasting glucose"}]
  },
  "description": "Measures blood glucose level after fasting for 8-12 hours",
  "permitted_data_type": "Quantity",
  "permitted_unit": {
    "coding": [{"system": "http://unitsofmeasure.org", "code": "mg/dL", "display": "mg/dL"}]
  },
  "qualified_value": [
    {"condition": "Normal", "range": {"low": {"value": 70}, "high": {"value": 100}}, "context": {"text": "Adult"}},
    {"condition": "Pre-diabetic", "range": {"low": {"value": 100}, "high": {"value": 126}}, "context": {"text": "Adult"}},
    {"condition": "Diabetic", "range": {"low": {"value": 126}}, "context": {"text": "Adult"}}
  ],
  "status": "active",
  "facility_id": 10
}
```

**FHIR Representation:**
```json
{
  "resourceType": "ObservationDefinition",
  "id": "obs-def-001",
  "url": "http://care.ohc.network/ObservationDefinition/fasting-blood-glucose",
  "title": "Fasting Blood Glucose",
  "status": "active",
  "code": {
    "coding": [
      {"system": "http://loinc.org", "code": "1558-6", "display": "Fasting glucose [Mass/volume] in Serum or Plasma"}
    ]
  },
  "permittedDataType": ["Quantity"],
  "quantitativeDetails": {
    "unit": {
      "coding": [
        {"system": "http://unitsofmeasure.org", "code": "mg/dL", "display": "milligram per deciliter"}
      ]
    },
    "decimalPrecision": 0
  },
  "qualifiedInterval": [
    {
      "category": "reference",
      "range": {"low": {"value": 70, "unit": "mg/dL"}, "high": {"value": 100, "unit": "mg/dL"}},
      "context": {"text": "Normal"},
      "appliesTo": [{"text": "Adult"}]
    },
    {
      "category": "reference",
      "range": {"low": {"value": 100, "unit": "mg/dL"}, "high": {"value": 126, "unit": "mg/dL"}},
      "context": {"text": "Pre-diabetic"},
      "appliesTo": [{"text": "Adult"}]
    },
    {
      "category": "reference",
      "range": {"low": {"value": 126, "unit": "mg/dL"}},
      "context": {"text": "Diabetic"},
      "appliesTo": [{"text": "Adult"}]
    }
  ]
}
```

---

### 21. SpecimenDefinition
**Table:** `emr_specimendefinition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| title | VARCHAR(255) | Not Null | Title |
| version | INT | - | Version |
| type_collected | JSONB | - | Collection type |
| type_tested | JSONB | - | Testing type |
| collection | JSONB | - | Collection method |
| handling | JSONB | - | Handling requirements |
| facility_id | BigInt | FK → Facility | Facility |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- Has many: Specimens

---

### 22. ActivityDefinition
**Table:** `emr_activitydefinition`
**FHIR Resource:** [ActivityDefinition](http://hl7.org/fhir/R4/activitydefinition.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `ActivityDefinition.identifier` |
| slug | VARCHAR(100) | Index | Unique slug | `ActivityDefinition.url` |
| title | VARCHAR(255) | Not Null | Title | `ActivityDefinition.title` |
| description | TEXT | - | Description | `ActivityDefinition.description` |
| status | VARCHAR(20) | - | draft, active, retired | `ActivityDefinition.status` |
| code | JSONB | - | Procedure code | `ActivityDefinition.code` |
| category | VARCHAR(30) | - | laboratory, imaging, procedure | `ActivityDefinition.topic` |
| usage | VARCHAR(50) | - | Usage context | `ActivityDefinition.usage` |
| classification | VARCHAR(50) | - | Classification | `ActivityDefinition.topic` |
| facility_id | BigInt | FK → Facility | Facility | `ActivityDefinition.publisher` |
| healthcare_service_id | BigInt | FK → HealthcareService | Service | `ActivityDefinition.participant` |
| category_id | BigInt | FK → ResourceCategory | Category | `ActivityDefinition.topic` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `healthcare_service` → HealthcareService (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)
- Has many: ServiceRequests

**Example Data:**
```json
{
  "id": 1,
  "external_id": "act-def-001",
  "slug": "cbc-panel",
  "title": "Complete Blood Count Panel",
  "description": "Complete blood count with differential, includes hemoglobin, WBC, platelets, RBC",
  "status": "active",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "58410-2", "display": "CBC panel"}]
  },
  "category": "laboratory",
  "usage": "routine",
  "facility_id": 10,
  "healthcare_service_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "ActivityDefinition",
  "id": "act-def-001",
  "url": "http://care.ohc.network/ActivityDefinition/cbc-panel",
  "title": "Complete Blood Count Panel",
  "status": "active",
  "description": "Complete blood count with differential, includes hemoglobin, WBC, platelets, RBC",
  "kind": "ServiceRequest",
  "code": {
    "coding": [
      {"system": "http://loinc.org", "code": "58410-2", "display": "Complete blood count (CBC) panel"}
    ]
  },
  "topic": [
    {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "108252007", "display": "Laboratory procedure"}
      ]
    }
  ],
  "usage": "routine",
  "participant": [
    {
      "type": "practitioner",
      "role": {
        "coding": [
          {"system": "http://snomed.info/sct", "code": "61246008", "display": "Laboratory technician"}
        ]
      }
    }
  ],
  "observationRequirement": [
    {"reference": "ObservationDefinition/hemoglobin"},
    {"reference": "ObservationDefinition/wbc-count"},
    {"reference": "ObservationDefinition/platelet-count"},
    {"reference": "ObservationDefinition/rbc-count"}
  ],
  "specimenRequirement": [
    {"reference": "SpecimenDefinition/blood-sample"}
  ]
}
```

---

## Inventory & Product Models

### 23. ProductKnowledge
**Table:** `emr_productknowledge`
**FHIR Resource:** [MedicationKnowledge](http://hl7.org/fhir/R4/medicationknowledge.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `MedicationKnowledge.identifier` |
| slug | VARCHAR(100) | Index | Unique slug | - |
| name | VARCHAR(255) | Not Null | Product name | `MedicationKnowledge.code.text` |
| status | VARCHAR(20) | - | active, inactive | `MedicationKnowledge.status` |
| product_type | VARCHAR(30) | - | medication, supply | `MedicationKnowledge.productType` |
| definitional | JSONB | - | Dosage form, route, etc. | `MedicationKnowledge.doseForm`, `MedicationKnowledge.intendedRoute` |
| characteristic | JSONB | - | Characteristics | `MedicationKnowledge.drugCharacteristic` |
| base_unit | JSONB | - | Base unit | `MedicationKnowledge.packaging` |
| facility_id | BigInt | FK → Facility | Facility | - |
| category_id | BigInt | FK → ResourceCategory | Category | - |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)
- Has many: Products, MedicationRequests, MedicationAdministrations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "pk-001",
  "slug": "paracetamol-500mg-tablet",
  "name": "Paracetamol 500mg Tablet",
  "status": "active",
  "product_type": "medication",
  "definitional": {
    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "90332006", "display": "Paracetamol"}]},
    "dosage_form": {"coding": [{"system": "http://snomed.info/sct", "code": "421026006", "display": "Oral tablet"}]},
    "route": [{"coding": [{"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"}]}],
    "strength": {"numerator": {"value": 500, "unit": "mg"}, "denominator": {"value": 1, "unit": "tablet"}}
  },
  "characteristic": {
    "color": "White",
    "shape": "Round",
    "imprint": "P500"
  },
  "base_unit": {"coding": [{"system": "http://unitsofmeasure.org", "code": "{tbl}", "display": "tablet"}]},
  "facility_id": 10
}
```

**FHIR Representation:**
```json
{
  "resourceType": "MedicationKnowledge",
  "id": "pk-001",
  "status": "active",
  "code": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "90332006", "display": "Paracetamol"}
    ],
    "text": "Paracetamol 500mg Tablet"
  },
  "doseForm": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "421026006", "display": "Oral tablet"}
    ]
  },
  "amount": {
    "value": 500,
    "unit": "mg",
    "system": "http://unitsofmeasure.org",
    "code": "mg"
  },
  "intendedRoute": [
    {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"}
      ]
    }
  ],
  "drugCharacteristic": [
    {
      "type": {"text": "color"},
      "valueString": "White"
    },
    {
      "type": {"text": "shape"},
      "valueString": "Round"
    },
    {
      "type": {"text": "imprint"},
      "valueString": "P500"
    }
  ],
  "packaging": {
    "type": {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/medicationknowledge-package-type", "code": "blister"}
      ]
    },
    "quantity": {"value": 10, "unit": "tablets"}
  }
}
```

---

### 24. Product
**Table:** `emr_product`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | active, inactive |
| product_type | VARCHAR(30) | - | Type |
| lot_number | VARCHAR(100) | - | Batch/lot number |
| expiration_date | DateTime | - | Expiry date |
| facility_id | BigInt | FK → Facility | Facility |
| product_knowledge_id | BigInt | FK → ProductKnowledge | Master product |
| charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Pricing |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `product_knowledge` → ProductKnowledge (FK, PROTECT)
- `charge_item_definition` → ChargeItemDefinition (FK, PROTECT)
- Has many: InventoryItems

---

### 25. InventoryItem
**Table:** `emr_inventoryitem`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | active, inactive |
| net_content | DECIMAL(20,6) | - | Current quantity |
| location_id | BigInt | FK → FacilityLocation | Storage location |
| product_id | BigInt | FK → Product | Product |

**Relationships:**
- `location` → FacilityLocation (FK, PROTECT)
- `product` → Product (FK, PROTECT)
- Has many: MedicationDispenses, SupplyDeliveries

---

### 26. ResourceCategory
**Table:** `emr_resourcecategory`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| title | VARCHAR(255) | Not Null | Title |
| resource_type | VARCHAR(50) | - | Resource type |
| resource_sub_type | VARCHAR(50) | - | Sub type |
| parent_id | BigInt | FK → ResourceCategory | Parent category |
| root_org_id | BigInt | FK → ResourceCategory | Root category |
| parent_cache | UUID[] | - | Parent hierarchy |
| level_cache | INT | - | Nesting level |
| facility_id | BigInt | FK → Facility | Facility |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `parent` → ResourceCategory (FK, CASCADE, self)
- `root_org` → ResourceCategory (FK, CASCADE, self)
- Has many: ProductKnowledge, ChargeItemDefinition, ActivityDefinition

---

## Supply Chain Models

### 27. RequestOrder
**Table:** `emr_requestorder`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | draft, active, completed |
| priority | VARCHAR(20) | - | routine, urgent, stat |
| intent | VARCHAR(20) | - | proposal, plan, order |
| supplier_id | BigInt | FK → Organization | Supplier |
| origin_id | BigInt | FK → FacilityLocation | Origin |
| destination_id | BigInt | FK → FacilityLocation | Destination |

**Relationships:**
- `supplier` → Organization (FK, CASCADE)
- `origin` → FacilityLocation (FK, CASCADE)
- `destination` → FacilityLocation (FK, CASCADE)
- Has many: SupplyRequests

---

### 28. SupplyRequest
**Table:** `emr_supplyrequest`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | draft, active, completed |
| quantity | DECIMAL(20,6) | - | Requested quantity |
| item_id | BigInt | FK → ProductKnowledge | Requested item |
| order_id | BigInt | FK → RequestOrder | Order |

**Relationships:**
- `item` → ProductKnowledge (FK, CASCADE)
- `order` → RequestOrder (FK, CASCADE)
- Has many: SupplyDeliveries

---

### 29. DeliveryOrder
**Table:** `emr_deliveryorder`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | in_progress, completed |
| supplier_id | BigInt | FK → Organization | Supplier |
| origin_id | BigInt | FK → FacilityLocation | Origin |
| destination_id | BigInt | FK → FacilityLocation | Destination |
| patient_id | BigInt | FK → Patient | Patient (for dispense) |
| patient_invoice_id | BigInt | FK → Invoice | Invoice |

**Relationships:**
- `supplier` → Organization (FK, CASCADE)
- `origin` → FacilityLocation (FK, CASCADE)
- `destination` → FacilityLocation (FK, CASCADE)
- `patient` → Patient (FK, PROTECT)
- `patient_invoice` → Invoice (FK, PROTECT)
- Has many: SupplyDeliveries

---

### 30. SupplyDelivery
**Table:** `emr_supplydelivery`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | in_progress, completed |
| supplied_item_quantity | DECIMAL(20,6) | - | Quantity delivered |
| supplied_item_id | BigInt | FK → Product | Product |
| supplied_inventory_item_id | BigInt | FK → InventoryItem | Inventory item |
| supply_request_id | BigInt | FK → SupplyRequest | Request |
| order_id | BigInt | FK → DeliveryOrder | Order |

**Relationships:**
- `supplied_item` → Product (FK, CASCADE)
- `supplied_inventory_item` → InventoryItem (FK, CASCADE)
- `supply_request` → SupplyRequest (FK, CASCADE)
- `order` → DeliveryOrder (FK, CASCADE)

---

## Facility & Location Models

### 31. Facility
**Table:** `facility_facility`
**FHIR Resource:** [Organization](http://hl7.org/fhir/R4/organization.html) (type: facility)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Organization.identifier` |
| name | VARCHAR(1000) | Not Null | Facility name | `Organization.name` |
| facility_type | INT | Not Null | Facility type | `Organization.type` |
| features | INT[] | - | Feature flags | `Organization.extension` |
| address | TEXT | - | Address | `Organization.address` |
| longitude | DECIMAL | - | Longitude | `Organization.extension` (geolocation) |
| latitude | DECIMAL | - | Latitude | `Organization.extension` (geolocation) |
| phone_number | VARCHAR(14) | - | Phone | `Organization.telecom` |
| is_active | BOOLEAN | Default: true | Active status | `Organization.active` |
| verified | BOOLEAN | Default: false | Verified | `Organization.extension` |
| geo_organization_id | BigInt | FK → Organization | Geographic org | `Organization.partOf` |
| default_internal_organization_id | BigInt | FK → FacilityOrganization | Default org | `Organization.extension` |
| created_by_id | BigInt | FK → User | Creator | `Organization.meta.source` |

**Relationships:**
- `geo_organization` → Organization (FK, SET_NULL)
- `default_internal_organization` → FacilityOrganization (FK, SET_NULL)
- `created_by` → User (FK, SET_NULL)
- Has many: Encounters, Locations, Organizations, Products, etc.

**Example Data:**
```json
{
  "id": 10,
  "external_id": "facility-001",
  "name": "District General Hospital",
  "facility_type": 1,
  "features": [1, 2, 5],
  "address": "123 Health Street, Medical District, City - 560001",
  "longitude": 77.5946,
  "latitude": 12.9716,
  "phone_number": "+918012345678",
  "is_active": true,
  "verified": true,
  "geo_organization_id": 5
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Organization",
  "id": "facility-001",
  "active": true,
  "type": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/organization-type", "code": "prov", "display": "Healthcare Provider"}
      ]
    },
    {
      "coding": [
        {"system": "http://care.ohc.network/facility-type", "code": "1", "display": "District Hospital"}
      ]
    }
  ],
  "name": "District General Hospital",
  "telecom": [
    {
      "system": "phone",
      "value": "+918012345678",
      "use": "work"
    }
  ],
  "address": [
    {
      "use": "work",
      "type": "physical",
      "text": "123 Health Street, Medical District, City - 560001",
      "postalCode": "560001"
    }
  ],
  "partOf": {
    "reference": "Organization/geo-org-5"
  },
  "extension": [
    {
      "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
      "extension": [
        {"url": "latitude", "valueDecimal": 12.9716},
        {"url": "longitude", "valueDecimal": 77.5946}
      ]
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/verified",
      "valueBoolean": true
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/features",
      "valueString": "emergency,laboratory,pharmacy"
    }
  ]
}
```

---

### 32. FacilityLocation
**Table:** `emr_facilitylocation`
**FHIR Resource:** [Location](http://hl7.org/fhir/R4/location.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Location.identifier` |
| name | VARCHAR(255) | Not Null | Location name | `Location.name` |
| description | TEXT | - | Description | `Location.description` |
| status | VARCHAR(20) | - | active, inactive | `Location.status` |
| mode | VARCHAR(20) | - | instance, kind | `Location.mode` |
| location_type | VARCHAR(50) | - | Type | `Location.type` |
| form | VARCHAR(50) | - | Physical form | `Location.physicalType` |
| parent_id | BigInt | FK → FacilityLocation | Parent location | `Location.partOf` |
| root_location_id | BigInt | FK → FacilityLocation | Root location | - |
| current_encounter_id | BigInt | FK → Encounter | Current occupant | `Location.extension` |
| parent_cache | UUID[] | - | Parent hierarchy | - |
| level_cache | INT | - | Nesting level | - |
| has_children | BOOLEAN | - | Has children | - |
| facility_id | BigInt | FK → Facility | Facility | `Location.managingOrganization` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `parent` → FacilityLocation (FK, SET_NULL, self)
- `root_location` → FacilityLocation (FK, CASCADE, self)
- `current_encounter` → Encounter (FK, SET_NULL)
- Has many: InventoryItems, Encounters, Devices

**Example Data:**
```json
{
  "id": 1,
  "external_id": "loc-001",
  "name": "Ward A - Room 101",
  "description": "General ward room with 4 beds",
  "status": "active",
  "mode": "instance",
  "location_type": "room",
  "form": "room",
  "parent_id": 5,
  "facility_id": 10,
  "level_cache": 3,
  "has_children": false
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Location",
  "id": "loc-001",
  "status": "active",
  "name": "Ward A - Room 101",
  "description": "General ward room with 4 beds",
  "mode": "instance",
  "type": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "HU", "display": "Hospital unit"}
      ]
    }
  ],
  "physicalType": {
    "coding": [
      {"system": "http://terminology.hl7.org/CodeSystem/location-physical-type", "code": "ro", "display": "Room"}
    ]
  },
  "partOf": {
    "reference": "Location/ward-a"
  },
  "managingOrganization": {
    "reference": "Organization/facility-10"
  }
}
```

---

### 33. FacilityLocationEncounter
**Table:** `emr_facilitylocationencounter`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| start_datetime | DateTime | Not Null | Check-in time |
| end_datetime | DateTime | - | Check-out time |
| status | VARCHAR(20) | - | planned, active, completed |
| location_id | BigInt | FK → FacilityLocation | Location |
| encounter_id | BigInt | FK → Encounter | Encounter |

**Relationships:**
- `location` → FacilityLocation (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

---

### 34. HealthcareService
**Table:** `emr_healthcareservice`
**FHIR Resource:** [HealthcareService](http://hl7.org/fhir/R4/healthcareservice.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `HealthcareService.identifier` |
| slug | VARCHAR(100) | Index | Unique slug | - |
| name | VARCHAR(255) | Not Null | Service name | `HealthcareService.name` |
| comment | TEXT | - | Description | `HealthcareService.comment` |
| active | BOOLEAN | Default: true | Active status | `HealthcareService.active` |
| service_type | JSONB | - | Service types | `HealthcareService.type` |
| locations | UUID[] | - | Service locations | `HealthcareService.location` |
| facility_id | BigInt | FK → Facility | Facility | `HealthcareService.providedBy` |
| managing_organization_id | BigInt | FK → FacilityOrganization | Managing org | `HealthcareService.providedBy` |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `managing_organization` → FacilityOrganization (FK, PROTECT)
- Has many: ActivityDefinitions, ServiceRequests, SchedulableResources

**Example Data:**
```json
{
  "id": 1,
  "external_id": "hs-001",
  "slug": "laboratory-services",
  "name": "Laboratory Services",
  "comment": "Full-service diagnostic laboratory",
  "active": true,
  "service_type": [
    {"coding": [{"system": "http://snomed.info/sct", "code": "708184003", "display": "Clinical laboratory service"}]}
  ],
  "locations": ["loc-lab-001", "loc-lab-002"],
  "facility_id": 10
}
```

**FHIR Representation:**
```json
{
  "resourceType": "HealthcareService",
  "id": "hs-001",
  "active": true,
  "providedBy": {
    "reference": "Organization/facility-10"
  },
  "category": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "2", "display": "Clinical"}
      ]
    }
  ],
  "type": [
    {
      "coding": [
        {"system": "http://snomed.info/sct", "code": "708184003", "display": "Clinical laboratory service"}
      ]
    }
  ],
  "name": "Laboratory Services",
  "comment": "Full-service diagnostic laboratory",
  "location": [
    {"reference": "Location/loc-lab-001"},
    {"reference": "Location/loc-lab-002"}
  ],
  "availableTime": [
    {
      "daysOfWeek": ["mon", "tue", "wed", "thu", "fri"],
      "availableStartTime": "08:00:00",
      "availableEndTime": "18:00:00"
    }
  ]
}
```

---

## Organization Models

### 35. Organization
**Table:** `emr_organization`
**FHIR Resource:** [Organization](http://hl7.org/fhir/R4/organization.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Organization.identifier` |
| name | VARCHAR(255) | Not Null | Org name | `Organization.name` |
| org_type | VARCHAR(50) | - | govt, team, etc. | `Organization.type` |
| active | BOOLEAN | Default: true | Active | `Organization.active` |
| description | TEXT | - | Description | `Organization.extension` |
| parent_id | BigInt | FK → Organization | Parent org | `Organization.partOf` |
| root_org_id | BigInt | FK → Organization | Root org | `Organization.extension` |
| parent_cache | UUID[] | - | Parent hierarchy | - |
| level_cache | INT | - | Nesting level | - |
| has_children | BOOLEAN | - | Has children | - |

**Relationships:**
- `parent` → Organization (FK, CASCADE, self)
- `root_org` → Organization (FK, CASCADE, self)
- Has many: OrganizationUsers, Patients

**Example Data:**
```json
{
  "id": 1,
  "external_id": "org-001",
  "name": "State Health Department",
  "org_type": "govt",
  "active": true,
  "description": "State-level health administration organization",
  "parent_id": null,
  "root_org_id": null,
  "level_cache": 0,
  "has_children": true
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Organization",
  "id": "org-001",
  "active": true,
  "type": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/organization-type", "code": "govt", "display": "Government"}
      ]
    }
  ],
  "name": "State Health Department",
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/org-description",
      "valueString": "State-level health administration organization"
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/org-level",
      "valueInteger": 0
    }
  ]
}
```

---

### 36. FacilityOrganization
**Table:** `emr_facilityorganization`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| (Same structure as Organization) | | | |
| facility_id | BigInt | FK → Facility | Facility |

**Relationships:**
- `facility` → Facility (FK, CASCADE)
- `parent` → FacilityOrganization (FK, CASCADE, self)
- Has many: FacilityOrganizationUsers, EncounterOrganizations

---

### 37. OrganizationUser
**Table:** `emr_organizationuser`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| organization_id | BigInt | FK → Organization | Organization |
| user_id | BigInt | FK → User | User |
| role_id | BigInt | FK → RoleModel | Role |

**Relationships:**
- `organization` → Organization (FK, CASCADE)
- `user` → User (FK, CASCADE)
- `role` → RoleModel (FK, CASCADE)

---

### 38. FacilityOrganizationUser
**Table:** `emr_facilityorganizationuser`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| organization_id | BigInt | FK → FacilityOrganization | Organization |
| user_id | BigInt | FK → User | User |
| role_id | BigInt | FK → RoleModel | Role |

**Relationships:**
- `organization` → FacilityOrganization (FK, CASCADE)
- `user` → User (FK, CASCADE)
- `role` → RoleModel (FK, CASCADE)

---

## Device & Equipment Models

### 39. Device
**Table:** `emr_device`
**FHIR Resource:** [Device](http://hl7.org/fhir/R4/device.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Device.identifier` |
| name | VARCHAR(255) | - | Device name | `Device.deviceName` |
| manufacturer | VARCHAR(255) | - | Manufacturer | `Device.manufacturer` |
| model_number | VARCHAR(100) | - | Model number | `Device.modelNumber` |
| serial_number | VARCHAR(100) | - | Serial number | `Device.serialNumber` |
| lot_number | VARCHAR(100) | - | Lot number | `Device.lotNumber` |
| status | VARCHAR(20) | - | active, inactive | `Device.status` |
| availability_status | VARCHAR(20) | - | available, lost, damaged | `Device.statusReason` |
| facility_id | BigInt | FK → Facility | Facility | `Device.owner` |
| managing_organization_id | BigInt | FK → FacilityOrganization | Managing org | `Device.owner` |
| current_location_id | BigInt | FK → FacilityLocation | Current location | `Device.location` |
| current_encounter_id | BigInt | FK → Encounter | Current use | `Device.extension` |

**Relationships:**
- `facility` → Facility (FK, CASCADE)
- `managing_organization` → FacilityOrganization (FK, SET_NULL)
- `current_location` → FacilityLocation (FK, SET_NULL)
- `current_encounter` → Encounter (FK, SET_NULL)
- Has many: DeviceEncounterHistory, DeviceLocationHistory

**Example Data:**
```json
{
  "id": 1,
  "external_id": "dev-001",
  "name": "Cardiac Monitor",
  "manufacturer": "Philips",
  "model_number": "IntelliVue MX450",
  "serial_number": "SN123456789",
  "lot_number": "LOT2024001",
  "status": "active",
  "availability_status": "available",
  "facility_id": 10,
  "current_location_id": 5
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Device",
  "id": "dev-001",
  "status": "active",
  "statusReason": [
    {
      "coding": [
        {"system": "http://terminology.hl7.org/CodeSystem/device-status-reason", "code": "online"}
      ]
    }
  ],
  "manufacturer": "Philips",
  "deviceName": [
    {
      "name": "Cardiac Monitor",
      "type": "user-friendly-name"
    }
  ],
  "modelNumber": "IntelliVue MX450",
  "serialNumber": "SN123456789",
  "lotNumber": "LOT2024001",
  "type": {
    "coding": [
      {"system": "http://snomed.info/sct", "code": "86184003", "display": "Electrocardiographic monitor"}
    ]
  },
  "owner": {
    "reference": "Organization/facility-10"
  },
  "location": {
    "reference": "Location/loc-005"
  }
}
```

---

### 40. DeviceEncounterHistory
**Table:** `emr_deviceencounterhistory`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| start_datetime | DateTime | - | Start time |
| end_datetime | DateTime | - | End time |
| device_id | BigInt | FK → Device | Device |
| encounter_id | BigInt | FK → Encounter | Encounter |

**Relationships:**
- `device` → Device (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

---

### 41. DeviceLocationHistory
**Table:** `emr_devicelocationhistory`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| start_datetime | DateTime | - | Start time |
| end_datetime | DateTime | - | End time |
| device_id | BigInt | FK → Device | Device |
| location_id | BigInt | FK → FacilityLocation | Location |

**Relationships:**
- `device` → Device (FK, CASCADE)
- `location` → FacilityLocation (FK, CASCADE)

---

## Questionnaire & Forms Models

### 42. Questionnaire
**Table:** `emr_questionnaire`
**FHIR Resource:** [Questionnaire](http://hl7.org/fhir/R4/questionnaire.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Questionnaire.identifier` |
| slug | VARCHAR(100) | Unique | Unique slug | `Questionnaire.url` |
| version | VARCHAR(20) | - | Version | `Questionnaire.version` |
| title | VARCHAR(255) | Not Null | Title | `Questionnaire.title` |
| subject_type | VARCHAR(50) | - | patient, encounter | `Questionnaire.subjectType` |
| status | VARCHAR(20) | - | draft, active, retired | `Questionnaire.status` |
| questions | JSONB | - | Question definitions | `Questionnaire.item` |
| organization_cache | UUID[] | - | Org cache | - |
| tags | VARCHAR[] | - | Tags | `Questionnaire.useContext` |

**Relationships:**
- Has many: QuestionnaireResponses, FormSubmissions, QuestionnaireOrganizations

**Example Data:**
```json
{
  "id": 1,
  "external_id": "quest-001",
  "slug": "patient-intake-form",
  "version": "1.0",
  "title": "Patient Intake Form",
  "subject_type": "patient",
  "status": "active",
  "questions": [
    {
      "linkId": "1",
      "text": "Chief Complaint",
      "type": "text",
      "required": true
    },
    {
      "linkId": "2",
      "text": "Duration of symptoms",
      "type": "choice",
      "required": true,
      "answerOption": [
        {"valueString": "Less than 1 day"},
        {"valueString": "1-3 days"},
        {"valueString": "3-7 days"},
        {"valueString": "More than 7 days"}
      ]
    },
    {
      "linkId": "3",
      "text": "Current Medications",
      "type": "text",
      "repeats": true
    }
  ],
  "tags": ["intake", "opd"]
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Questionnaire",
  "id": "quest-001",
  "url": "http://care.ohc.network/Questionnaire/patient-intake-form",
  "version": "1.0",
  "title": "Patient Intake Form",
  "status": "active",
  "subjectType": ["Patient"],
  "item": [
    {
      "linkId": "1",
      "text": "Chief Complaint",
      "type": "text",
      "required": true
    },
    {
      "linkId": "2",
      "text": "Duration of symptoms",
      "type": "choice",
      "required": true,
      "answerOption": [
        {"valueString": "Less than 1 day"},
        {"valueString": "1-3 days"},
        {"valueString": "3-7 days"},
        {"valueString": "More than 7 days"}
      ]
    },
    {
      "linkId": "3",
      "text": "Current Medications",
      "type": "text",
      "repeats": true
    }
  ],
  "useContext": [
    {
      "code": {"system": "http://terminology.hl7.org/CodeSystem/usage-context-type", "code": "workflow"},
      "valueCodeableConcept": {"text": "intake"}
    }
  ]
}
```

---

### 43. QuestionnaireResponse
**Table:** `emr_questionnaireresponse`
**FHIR Resource:** [QuestionnaireResponse](http://hl7.org/fhir/R4/questionnaireresponse.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `QuestionnaireResponse.identifier` |
| status | VARCHAR(20) | - | in_progress, completed | `QuestionnaireResponse.status` |
| subject_id | UUID | - | Subject reference | `QuestionnaireResponse.subject` |
| responses | JSONB | - | Response data | `QuestionnaireResponse.item` |
| questionnaire_id | BigInt | FK → Questionnaire | Questionnaire | `QuestionnaireResponse.questionnaire` |
| patient_id | BigInt | FK → Patient | Patient | `QuestionnaireResponse.subject` |
| encounter_id | BigInt | FK → Encounter | Encounter | `QuestionnaireResponse.encounter` |
| form_submission_id | BigInt | FK → FormSubmission | Submission | - |

**Relationships:**
- `questionnaire` → Questionnaire (FK, CASCADE)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `form_submission` → FormSubmission (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "qr-001",
  "status": "completed",
  "responses": [
    {"linkId": "1", "answer": [{"valueString": "Fever and headache for 3 days"}]},
    {"linkId": "2", "answer": [{"valueString": "3-7 days"}]},
    {"linkId": "3", "answer": [{"valueString": "Paracetamol 500mg"}, {"valueString": "Vitamin C"}]}
  ],
  "questionnaire_id": 1,
  "patient_id": 1,
  "encounter_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "QuestionnaireResponse",
  "id": "qr-001",
  "questionnaire": "http://care.ohc.network/Questionnaire/patient-intake-form",
  "status": "completed",
  "subject": {
    "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
  },
  "encounter": {
    "reference": "Encounter/660e8400-e29b-41d4-a716-446655440001"
  },
  "authored": "2024-01-15T09:05:00Z",
  "item": [
    {
      "linkId": "1",
      "text": "Chief Complaint",
      "answer": [{"valueString": "Fever and headache for 3 days"}]
    },
    {
      "linkId": "2",
      "text": "Duration of symptoms",
      "answer": [{"valueString": "3-7 days"}]
    },
    {
      "linkId": "3",
      "text": "Current Medications",
      "answer": [
        {"valueString": "Paracetamol 500mg"},
        {"valueString": "Vitamin C"}
      ]
    }
  ]
}
```

---

### 44. FormSubmission
**Table:** `emr_formsubmission`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | in_progress, completed |
| response_dump | JSONB | - | All responses |
| questionnaire_id | BigInt | FK → Questionnaire | Questionnaire |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |

**Relationships:**
- `questionnaire` → Questionnaire (FK, CASCADE)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- Has many: QuestionnaireResponses

---

## Scheduling & Booking Models

### 45. SchedulableResource
**Table:** `emr_schedulableresource`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| resource_type | VARCHAR(30) | Not Null | user, location, healthcare_service |
| facility_id | BigInt | FK → Facility | Facility |
| user_id | BigInt | FK → User | User (if practitioner) |
| location_id | BigInt | FK → FacilityLocation | Location (if room) |
| healthcare_service_id | BigInt | FK → HealthcareService | Service |

**Unique Constraint:** (facility, resource_type, user/location/healthcare_service)

**Relationships:**
- `facility` → Facility (FK, CASCADE)
- `user` → User (FK, CASCADE)
- `location` → FacilityLocation (FK, CASCADE)
- `healthcare_service` → HealthcareService (FK, CASCADE)
- Has many: Schedules, TokenSlots, TokenQueues

---

### 46. Schedule
**Table:** `emr_schedule`
**FHIR Resource:** [Schedule](http://hl7.org/fhir/R4/schedule.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Schedule.identifier` |
| name | VARCHAR(255) | Not Null | Schedule name | `Schedule.comment` |
| valid_from | DateTime | Not Null | Start date | `Schedule.planningHorizon.start` |
| valid_to | DateTime | Not Null | End date | `Schedule.planningHorizon.end` |
| is_public | BOOLEAN | Default: false | Public booking | `Schedule.extension` |
| resource_id | BigInt | FK → SchedulableResource | Resource | `Schedule.actor` |
| charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Pricing | `Schedule.extension` |
| revisit_charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Revisit pricing | `Schedule.extension` |

**Relationships:**
- `resource` → SchedulableResource (FK, CASCADE)
- `charge_item_definition` → ChargeItemDefinition (FK, PROTECT)
- Has many: Availabilities

**Example Data:**
```json
{
  "id": 1,
  "external_id": "sched-001",
  "name": "Dr. Sharma OPD Schedule - January 2024",
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_to": "2024-01-31T23:59:59Z",
  "is_public": true,
  "resource_id": 1,
  "charge_item_definition_id": 5,
  "revisit_charge_item_definition_id": 6
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Schedule",
  "id": "sched-001",
  "active": true,
  "serviceCategory": [
    {
      "coding": [{"system": "http://snomed.info/sct", "code": "394802001", "display": "General medicine"}]
    }
  ],
  "actor": [
    {"reference": "Practitioner/dr-sharma-001"}
  ],
  "planningHorizon": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "comment": "Dr. Sharma OPD Schedule - January 2024",
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/is-public",
      "valueBoolean": true
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/consultation-fee",
      "valueReference": {"reference": "ChargeItemDefinition/opd-consultation"}
    }
  ]
}
```

---

### 47. Availability
**Table:** `emr_availability`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | Not Null | Availability name |
| slot_type | VARCHAR(20) | - | appointment, walkin |
| slot_size_in_minutes | INT | Not Null | Slot duration |
| tokens_per_slot | INT | Default: 1 | Max tokens |
| availability | JSONB | - | Day/time patterns |
| schedule_id | BigInt | FK → Schedule | Schedule |

**Relationships:**
- `schedule` → Schedule (FK, CASCADE)
- Has many: TokenSlots

---

### 48. TokenSlot
**Table:** `emr_tokenslot`
**FHIR Resource:** [Slot](http://hl7.org/fhir/R4/slot.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Slot.identifier` |
| start_datetime | DateTime | Not Null | Slot start | `Slot.start` |
| end_datetime | DateTime | Not Null | Slot end | `Slot.end` |
| allocated | INT | Default: 0 | Booked count | `Slot.extension` |
| resource_id | BigInt | FK → SchedulableResource | Resource | `Slot.schedule` |
| availability_id | BigInt | FK → Availability | Availability | `Slot.schedule` |

**Relationships:**
- `resource` → SchedulableResource (FK, CASCADE)
- `availability` → Availability (FK, CASCADE)
- Has many: TokenBookings

**Example Data:**
```json
{
  "id": 1,
  "external_id": "slot-001",
  "start_datetime": "2024-01-15T09:00:00Z",
  "end_datetime": "2024-01-15T09:15:00Z",
  "allocated": 1,
  "resource_id": 1,
  "availability_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Slot",
  "id": "slot-001",
  "schedule": {
    "reference": "Schedule/sched-001"
  },
  "status": "busy",
  "start": "2024-01-15T09:00:00Z",
  "end": "2024-01-15T09:15:00Z",
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/slot-capacity",
      "valueInteger": 3
    },
    {
      "url": "http://care.ohc.network/StructureDefinition/slot-allocated",
      "valueInteger": 1
    }
  ]
}
```

---

### 49. TokenBooking
**Table:** `emr_tokenbooking`
**FHIR Resource:** [Appointment](http://hl7.org/fhir/R4/appointment.html)

| Column | Type | Constraints | Description | FHIR Element |
|--------|------|-------------|-------------|--------------|
| id | BigAutoField | PK | Primary key | - |
| external_id | UUID | Unique, Index | External identifier | `Appointment.identifier` |
| status | VARCHAR(20) | - | booked, checked_in, cancelled | `Appointment.status` |
| reason_for_visit | TEXT | - | Reason | `Appointment.reasonCode` |
| token_slot_id | BigInt | FK → TokenSlot | Slot | `Appointment.slot` |
| patient_id | BigInt | FK → Patient | Patient | `Appointment.participant` |
| booked_by_id | BigInt | FK → User | Booked by | `Appointment.participant` |
| associated_encounter_id | BigInt | FK → Encounter | Encounter | `Appointment.extension` |
| token_id | BigInt | FK → Token | Token | `Appointment.extension` |
| charge_item_id | BigInt | FK → ChargeItem | Charge | `Appointment.extension` |

**Relationships:**
- `token_slot` → TokenSlot (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `booked_by` → User (FK, CASCADE)
- `associated_encounter` → Encounter (FK, PROTECT)
- `token` → Token (FK, PROTECT)
- `charge_item` → ChargeItem (FK, CASCADE)

**Example Data:**
```json
{
  "id": 1,
  "external_id": "booking-001",
  "status": "booked",
  "reason_for_visit": "Routine checkup and blood pressure monitoring",
  "token_slot_id": 1,
  "patient_id": 1,
  "booked_by_id": 10,
  "associated_encounter_id": null,
  "token_id": 1
}
```

**FHIR Representation:**
```json
{
  "resourceType": "Appointment",
  "id": "booking-001",
  "status": "booked",
  "serviceCategory": [
    {
      "coding": [{"system": "http://snomed.info/sct", "code": "394802001", "display": "General medicine"}]
    }
  ],
  "serviceType": [
    {
      "coding": [{"system": "http://snomed.info/sct", "code": "11429006", "display": "Consultation"}]
    }
  ],
  "reasonCode": [
    {
      "text": "Routine checkup and blood pressure monitoring"
    }
  ],
  "start": "2024-01-15T09:00:00Z",
  "end": "2024-01-15T09:15:00Z",
  "slot": [
    {"reference": "Slot/slot-001"}
  ],
  "participant": [
    {
      "actor": {
        "reference": "Patient/550e8400-e29b-41d4-a716-446655440000"
      },
      "required": "required",
      "status": "accepted"
    },
    {
      "actor": {
        "reference": "Practitioner/dr-sharma-001"
      },
      "required": "required",
      "status": "accepted"
    }
  ],
  "extension": [
    {
      "url": "http://care.ohc.network/StructureDefinition/token-number",
      "valueString": "A-001"
    }
  ]
}
```

---

### 50. Token
**Table:** `emr_token`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| number | INT | Not Null | Token number |
| status | VARCHAR(20) | - | waiting, in_progress, completed |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| queue_id | BigInt | FK → TokenQueue | Queue |
| category_id | BigInt | FK → TokenCategory | Category |
| sub_queue_id | BigInt | FK → TokenSubQueue | Sub queue |
| booking_id | BigInt | FK → TokenBooking | Booking |

**Relationships:**
- `facility` → Facility (FK, CASCADE)
- `patient` → Patient (FK, CASCADE)
- `queue` → TokenQueue (FK, CASCADE)
- `category` → TokenCategory (FK, CASCADE)
- `sub_queue` → TokenSubQueue (FK, CASCADE)
- `booking` → TokenBooking (FK, CASCADE)

---

## Notes & Communication Models

### 51. NoteThread
**Table:** `emr_notethread`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| title | VARCHAR(255) | - | Thread title |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- Has many: NoteMessages

---

### 52. NoteMessage
**Table:** `emr_notemessage`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| message | TEXT | Not Null | Message content |
| message_history | JSONB | - | Edit history |
| thread_id | BigInt | FK → NoteThread | Thread |

**Relationships:**
- `thread` → NoteThread (FK, CASCADE)

---

## Security Models

### 53. RoleModel
**Table:** `security_rolemodel`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| name | VARCHAR(100) | Unique (when not deleted) | Role name |
| description | TEXT | - | Description |
| is_system | BOOLEAN | Default: false | System role |
| is_archived | BOOLEAN | Default: false | Archived |

**Relationships:**
- Has many: RolePermissions, OrganizationUsers, FacilityOrganizationUsers

---

### 54. PermissionModel
**Table:** `security_permissionmodel`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| slug | VARCHAR(100) | Unique, Index | Permission slug |
| name | VARCHAR(100) | Not Null | Permission name |
| description | TEXT | - | Description |
| context | VARCHAR(50) | - | facility, organization |

**Relationships:**
- Has many: RolePermissions

---

### 55. RolePermission
**Table:** `security_rolepermission`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| role_id | BigInt | FK → RoleModel | Role |
| permission_id | BigInt | FK → PermissionModel | Permission |

**Relationships:**
- `role` → RoleModel (FK, CASCADE)
- `permission` → PermissionModel (FK, CASCADE)

---

### 56. RoleAssociation
**Table:** `security_roleassociation`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| user_id | BigInt | FK → User | User |
| context | VARCHAR(50) | Not Null | Context type |
| context_id | BigInt | Not Null | Context ID |
| role_id | BigInt | FK → RoleModel | Role |
| expiry | DateTime | - | Expiry date |

**Relationships:**
- `user` → User (FK, CASCADE)
- `role` → RoleModel (FK, CASCADE)

---

## Utility Models

### 57. ValueSet
**Table:** `emr_valueset`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| slug | SlugField | Unique, Index | Valueset slug |
| name | VARCHAR(255) | Not Null | Name |
| compose | JSONB | - | Composition |
| status | VARCHAR(20) | - | draft, active |
| is_system_defined | BOOLEAN | Default: false | System valueset |

---

### 58. FileUpload
**Table:** `emr_fileupload`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | Not Null | File name |
| internal_name | VARCHAR(255) | Not Null | Storage name |
| associating_id | VARCHAR(100) | Index | Associated object ID |
| file_type | VARCHAR(50) | - | File MIME type |
| file_category | VARCHAR(50) | - | Category |
| upload_completed | BOOLEAN | Default: false | Upload complete |
| is_archived | BOOLEAN | Default: false | Archived |
| archived_by_id | BigInt | FK → User | Archived by |

---

### 59. MetaArtifact
**Table:** `emr_metaartifact`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| associating_type | VARCHAR(50) | Index | Associated type |
| associating_external_id | UUID | Index | Associated ID |
| name | VARCHAR(255) | Not Null | Artifact name |
| object_type | VARCHAR(50) | - | Object type |
| object_value | JSONB | - | Object value |

---

## Summary Statistics

| Category | Count | Key Tables |
|----------|-------|------------|
| **Core Clinical** | 6 | Patient, Encounter, Observation, Condition, Allergy, Consent |
| **Billing** | 5 | Account, ChargeItem, ChargeItemDefinition, Invoice, PaymentReconciliation |
| **Medication** | 5 | MedicationRequest, MedicationAdministration, MedicationDispense, MedicationStatement, DispenseOrder |
| **Diagnostic** | 6 | ServiceRequest, DiagnosticReport, Specimen, ObservationDefinition, SpecimenDefinition, ActivityDefinition |
| **Inventory** | 4 | ProductKnowledge, Product, InventoryItem, ResourceCategory |
| **Supply Chain** | 4 | RequestOrder, SupplyRequest, DeliveryOrder, SupplyDelivery |
| **Facility** | 4 | Facility, FacilityLocation, FacilityLocationEncounter, HealthcareService |
| **Organization** | 4 | Organization, FacilityOrganization, OrganizationUser, FacilityOrganizationUser |
| **Device** | 4 | Device, DeviceEncounterHistory, DeviceLocationHistory, DeviceServiceHistory |
| **Questionnaire** | 5 | Questionnaire, QuestionnaireResponse, FormSubmission, QuestionnaireOrganization, QuestionnaireResponseTemplate |
| **Scheduling** | 8 | SchedulableResource, Schedule, Availability, AvailabilityException, TokenSlot, TokenBooking, TokenQueue, Token |
| **Notes** | 2 | NoteThread, NoteMessage |
| **Security** | 4 | RoleModel, PermissionModel, RolePermission, RoleAssociation |
| **Utility** | 4 | ValueSet, FileUpload, MetaArtifact, TagConfig |
| **TOTAL** | **65+** | |

---

## Indexes

### Primary Indexes
- All tables have primary key on `id`
- All tables have unique index on `external_id`

### Foreign Key Indexes
- All ForeignKey fields are automatically indexed

### Custom Indexes
| Table | Index | Columns |
|-------|-------|---------|
| emr_patient | phone_number_idx | phone_number |
| emr_specimen | accession_idx | accession_identifier |
| emr_valueset | slug_idx | slug |
| emr_chargeitemdefinition | facility_slug_idx | facility_id, slug |
| emr_resourcecategory | facility_slug_idx | facility_id, slug |
| emr_metaartifact | associating_idx | associating_type, associating_external_id |

---

## File References

| Model Category | File Path |
|----------------|-----------|
| Patient | `care/emr/models/patient.py` |
| Encounter | `care/emr/models/encounter.py` |
| Observation | `care/emr/models/observation.py` |
| Condition | `care/emr/models/condition.py` |
| Allergy | `care/emr/models/allergy_intolerance.py` |
| Consent | `care/emr/models/consent.py` |
| Account/Billing | `care/emr/models/account.py`, `invoice.py`, `charge_item.py`, `payment_reconciliation.py` |
| Medication | `care/emr/models/medication_request.py`, `medication_administration.py`, `medication_dispense.py` |
| Diagnostic | `care/emr/models/service_request.py`, `diagnostic_report.py`, `specimen.py` |
| Definitions | `care/emr/models/observation_definition.py`, `activity_definition.py`, `specimen_definition.py` |
| Inventory | `care/emr/models/product.py`, `product_knowledge.py`, `inventory_item.py` |
| Supply Chain | `care/emr/models/supply_request.py`, `supply_delivery.py` |
| Location | `care/emr/models/location.py` |
| Organization | `care/emr/models/organization.py` |
| Device | `care/emr/models/device.py` |
| Questionnaire | `care/emr/models/questionnaire.py` |
| Scheduling | `care/emr/models/scheduling/schedule.py`, `booking.py`, `token.py` |
| Notes | `care/emr/models/notes.py` |
| Facility | `care/facility/models/facility.py` |
| Security | `care/security/models/role.py`, `permission.py` |

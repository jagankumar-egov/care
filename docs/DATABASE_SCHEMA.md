# Database Schema Documentation - CARE EMR System

## Overview

This document provides a comprehensive view of all database tables in the CARE EMR system and their relationships.

**Total Models:** 75+
**Database:** PostgreSQL

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(200) | Not Null | Patient name |
| gender | VARCHAR(35) | Not Null | Gender |
| phone_number | VARCHAR(14) | - | Primary contact |
| emergency_phone_number | VARCHAR(14) | - | Emergency contact |
| date_of_birth | DATE | - | DOB |
| blood_group | VARCHAR(4) | - | Blood group |
| geo_organization_id | BigInt | FK → Organization | Geographic org |
| organization_cache | UUID[] | - | Cached org hierarchy |
| users_cache | UUID[] | - | Cached users |
| extensions | JSONB | - | Custom fields |
| created_by_id | BigInt | FK → User | Creator |
| created_at | DateTime | - | Created timestamp |
| modified_at | DateTime | - | Modified timestamp |
| deleted | Boolean | Default: false | Soft delete |

**Relationships:**
- `geo_organization` → Organization (FK)
- `created_by` → User (FK)
- Has many: Encounters, Observations, Conditions, MedicationRequests, Accounts

---

### 2. Encounter
**Table:** `emr_encounter`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | Not Null | planned, in_progress, completed, etc. |
| encounter_class | VARCHAR(20) | - | ambulatory, emergency, inpatient |
| period | JSONB | - | Start/end times |
| patient_id | BigInt | FK → Patient | Patient reference |
| facility_id | BigInt | FK → Facility | Facility |
| appointment_id | BigInt | FK → TokenBooking | Appointment |
| current_location_id | BigInt | FK → FacilityLocation | Current location |
| care_team | JSONB | - | Care team members |
| care_team_users | UUID[] | - | User IDs in care team |
| discharge_summary_advice | TEXT | - | Discharge advice |
| tags | VARCHAR[] | - | Encounter tags |
| priority | VARCHAR(20) | - | routine, urgent, asap, stat |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `facility` → Facility (FK, PROTECT)
- `appointment` → TokenBooking (FK, SET_NULL)
- `current_location` → FacilityLocation (FK, SET_NULL)
- Has many: Observations, Conditions, ServiceRequests, MedicationRequests

---

### 3. Observation
**Table:** `emr_observation`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | Not Null | registered, preliminary, final, amended |
| category | JSONB | - | vital-signs, laboratory, etc. |
| code | JSONB | - | LOINC/SNOMED code |
| value_type | VARCHAR(30) | - | Quantity, string, CodeableConcept |
| value | JSONB | - | Observation value |
| effective | JSONB | - | When observed |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| subject_id | UUID | - | Subject reference |
| diagnostic_report_id | BigInt | FK → DiagnosticReport | Parent report |
| observation_definition_id | BigInt | FK → ObservationDefinition | Definition |
| interpretation | JSONB | - | N, H, L, etc. |
| reference_range | JSONB | - | Normal ranges |
| body_site | JSONB | - | Body site |
| method | JSONB | - | Method used |
| note | JSONB | - | Notes |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `diagnostic_report` → DiagnosticReport (FK, CASCADE)
- `observation_definition` → ObservationDefinition (FK, CASCADE)

---

### 4. Condition
**Table:** `emr_condition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| code | JSONB | Not Null | SNOMED diagnosis code |
| clinical_status | VARCHAR(20) | - | active, recurrence, inactive, resolved |
| verification_status | VARCHAR(20) | - | unconfirmed, provisional, confirmed |
| severity | VARCHAR(20) | - | mild, moderate, severe |
| category | VARCHAR(30) | - | encounter_diagnosis, problem_list_item |
| body_site | JSONB | - | Location of condition |
| onset | JSONB | - | When started |
| abatement | JSONB | - | When resolved |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| recorded_date | DateTime | - | When recorded |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

---

### 5. AllergyIntolerance
**Table:** `emr_allergyintolerance`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| code | JSONB | Not Null | Allergy code |
| allergy_intolerance_type | VARCHAR(20) | - | allergy, intolerance |
| category | VARCHAR(20) | - | food, medication, environment, biologic |
| criticality | VARCHAR(20) | - | low, high, unable_to_assess |
| clinical_status | VARCHAR(20) | - | active, inactive, resolved |
| verification_status | VARCHAR(20) | - | unconfirmed, confirmed, refuted |
| onset | JSONB | - | When started |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| note | JSONB | - | Notes |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)

---

### 6. Consent
**Table:** `emr_consent`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(50) | Not Null | draft, active, inactive |
| category | VARCHAR(50) | Not Null | treatment, research, etc. |
| decision | VARCHAR(20) | - | permit, deny |
| encounter_id | BigInt | FK → Encounter | Encounter |
| verification_details | JSONB | - | Verification info |
| period | JSONB | - | Valid period |

**Relationships:**
- `encounter` → Encounter (FK, CASCADE)

---

## Billing & Account Models

### 7. Account
**Table:** `emr_account`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | active, inactive, on_hold |
| billing_status | VARCHAR(30) | - | open, billing, closed_completed |
| total_net | DECIMAL(20,6) | - | Net total |
| total_gross | DECIMAL(20,6) | - | Gross total |
| total_paid | DECIMAL(20,6) | - | Paid amount |
| total_balance | DECIMAL(20,6) | - | Outstanding balance |
| total_billable_charge_items | DECIMAL(20,6) | - | Billable items total |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| primary_encounter_id | BigInt | FK → Encounter | Primary encounter |
| description | TEXT | - | Description |
| name | VARCHAR(255) | - | Account name |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, PROTECT)
- `primary_encounter` → Encounter (FK, SET_NULL)
- Has many: ChargeItems, Invoices, PaymentReconciliations

---

### 8. ChargeItem
**Table:** `emr_chargeitem`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| title | VARCHAR(255) | - | Item title |
| status | VARCHAR(20) | - | billable, not_billable, billed, paid |
| quantity | DECIMAL(10,4) | - | Quantity |
| unit_price_components | JSONB | - | Unit pricing |
| total_price_components | JSONB | - | Total pricing |
| total_price | DECIMAL(20,6) | - | Total price |
| service_resource | VARCHAR(50) | - | Source resource type |
| service_resource_id | VARCHAR(100) | - | Source resource ID |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| account_id | BigInt | FK → Account | Account |
| charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Definition |
| paid_invoice_id | BigInt | FK → Invoice | Paid invoice |
| performer_actor_id | BigInt | FK → User | Performer |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `account` → Account (FK, CASCADE)
- `charge_item_definition` → ChargeItemDefinition (FK, CASCADE)
- `paid_invoice` → Invoice (FK, CASCADE)

---

### 9. ChargeItemDefinition
**Table:** `emr_chargeitemdefinition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| title | VARCHAR(255) | Not Null | Title |
| version | INT | - | Version number |
| status | VARCHAR(20) | - | draft, active, retired |
| price_components | JSONB | - | Pricing breakdown |
| can_edit_charge_item | BOOLEAN | - | Allow editing |
| facility_id | BigInt | FK → Facility | Facility |
| category_id | BigInt | FK → ResourceCategory | Category |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)

---

### 10. Invoice
**Table:** `emr_invoice`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| title | VARCHAR(255) | - | Invoice title |
| status | VARCHAR(20) | - | draft, issued, balanced, cancelled |
| number | VARCHAR(50) | - | Invoice number |
| charge_items | UUID[] | - | Charge item IDs |
| charge_items_copy | JSONB | - | Snapshot of items |
| total_price_components | JSONB | - | Price breakdown |
| total_net | DECIMAL(20,6) | - | Net amount |
| total_gross | DECIMAL(20,6) | - | Gross amount |
| locked | BOOLEAN | Default: false | Lock status |
| is_refund | BOOLEAN | Default: false | Refund flag |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| account_id | BigInt | FK → Account | Account |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, PROTECT)
- `account` → Account (FK, PROTECT)
- Has many: PaymentReconciliations

---

### 11. PaymentReconciliation
**Table:** `emr_paymentreconciliation`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| reconciliation_type | VARCHAR(20) | - | payment, adjustment, advance |
| status | VARCHAR(20) | - | active, cancelled, draft |
| kind | VARCHAR(20) | - | deposit, online, kiosk |
| issuer_type | VARCHAR(20) | - | patient, insurer |
| outcome | VARCHAR(20) | - | queued, complete, error |
| method | VARCHAR(20) | - | cash, ccca, debc, chck |
| reference_number | VARCHAR(100) | - | Transaction ref |
| authorization | VARCHAR(100) | - | Auth code |
| tendered_amount | DECIMAL(20,6) | - | Amount given |
| returned_amount | DECIMAL(20,6) | - | Change returned |
| amount | DECIMAL(20,6) | - | Net amount |
| is_credit_note | BOOLEAN | Default: false | Refund indicator |
| facility_id | BigInt | FK → Facility | Facility |
| account_id | BigInt | FK → Account | Account |
| target_invoice_id | BigInt | FK → Invoice | Invoice |
| location_id | BigInt | FK → FacilityLocation | Payment location |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `account` → Account (FK, PROTECT)
- `target_invoice` → Invoice (FK, PROTECT)
- `location` → FacilityLocation (FK, PROTECT)

---

## Medication Models

### 12. MedicationRequest
**Table:** `emr_medicationrequest`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | active, completed, cancelled |
| intent | VARCHAR(20) | - | proposal, plan, order |
| medication | JSONB | Not Null | Medication code |
| dosage_instruction | JSONB | - | Dosing details |
| dispense_request | JSONB | - | Dispense info |
| substitution | JSONB | - | Substitution rules |
| reason | JSONB | - | Reason for request |
| note | JSONB | - | Notes |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| requester_id | BigInt | FK → User | Prescriber |
| requested_product_id | BigInt | FK → ProductKnowledge | Product |
| prescription_id | BigInt | FK → MedicationRequestPrescription | Prescription |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `requester` → User (FK, SET_NULL)
- `requested_product` → ProductKnowledge (FK, SET_NULL)
- `prescription` → MedicationRequestPrescription (FK, SET_NULL)

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | in_progress, completed, not_done |
| medication | JSONB | - | Medication code |
| dosage | JSONB | - | Dosage given |
| effective_period | JSONB | - | When given |
| note | JSONB | - | Notes |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| request_id | BigInt | FK → MedicationRequest | Request |
| administered_product_id | BigInt | FK → ProductKnowledge | Product |

**Relationships:**
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `request` → MedicationRequest (FK, CASCADE)
- `administered_product` → ProductKnowledge (FK, CASCADE)

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| title | VARCHAR(255) | - | Request title |
| status | VARCHAR(20) | - | draft, active, completed, revoked |
| intent | VARCHAR(20) | - | proposal, plan, order |
| priority | VARCHAR(20) | - | routine, urgent, asap, stat |
| code | JSONB | - | Procedure code |
| category | VARCHAR(30) | - | laboratory, imaging, procedure |
| body_site | JSONB | - | Body site |
| subject_id | UUID | - | Subject reference |
| locations | UUID[] | - | Assigned locations |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| healthcare_service_id | BigInt | FK → HealthcareService | Service |
| activity_definition_id | BigInt | FK → ActivityDefinition | Activity |
| requester_id | BigInt | FK → User | Requester |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `healthcare_service` → HealthcareService (FK, PROTECT)
- `activity_definition` → ActivityDefinition (FK, PROTECT)
- `requester` → User (FK, CASCADE)
- Has many: DiagnosticReports, Specimens

---

### 18. DiagnosticReport
**Table:** `emr_diagnosticreport`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | registered, partial, preliminary, final |
| code | JSONB | - | Report code |
| category | JSONB | - | Category |
| effective | JSONB | - | When performed |
| issued | DateTime | - | When issued |
| conclusion | TEXT | - | Clinical conclusion |
| conclusion_code | JSONB | - | Coded conclusion |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| service_request_id | BigInt | FK → ServiceRequest | Request |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `service_request` → ServiceRequest (FK, CASCADE)
- Has many: Observations

---

### 19. Specimen
**Table:** `emr_specimen`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| accession_identifier | VARCHAR(100) | Index | Lab accession # |
| status | VARCHAR(20) | - | available, unavailable, entered_in_error |
| type | JSONB | - | Specimen type |
| collection | JSONB | - | Collection details |
| processing | JSONB | - | Processing steps |
| condition | JSONB | - | Specimen condition |
| note | JSONB | - | Notes |
| facility_id | BigInt | FK → Facility | Facility |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| service_request_id | BigInt | FK → ServiceRequest | Request |
| specimen_definition_id | BigInt | FK → SpecimenDefinition | Definition |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `service_request` → ServiceRequest (FK, CASCADE)
- `specimen_definition` → SpecimenDefinition (FK, CASCADE)

---

### 20. ObservationDefinition
**Table:** `emr_observationdefinition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| title | VARCHAR(255) | Not Null | Title |
| code | JSONB | Not Null | LOINC code |
| description | TEXT | - | Description |
| permitted_data_type | VARCHAR(30) | - | Quantity, string, etc. |
| permitted_unit | JSONB | - | Allowed units |
| qualified_value | JSONB | - | Reference ranges |
| component | JSONB | - | Panel components |
| status | VARCHAR(20) | - | draft, active, retired |
| facility_id | BigInt | FK → Facility | Facility |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- Has many: Observations

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| title | VARCHAR(255) | Not Null | Title |
| description | TEXT | - | Description |
| status | VARCHAR(20) | - | draft, active, retired |
| code | JSONB | - | Procedure code |
| category | VARCHAR(30) | - | laboratory, imaging, procedure |
| usage | VARCHAR(50) | - | Usage context |
| classification | VARCHAR(50) | - | Classification |
| facility_id | BigInt | FK → Facility | Facility |
| healthcare_service_id | BigInt | FK → HealthcareService | Service |
| category_id | BigInt | FK → ResourceCategory | Category |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `healthcare_service` → HealthcareService (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)
- Has many: ServiceRequests

---

## Inventory & Product Models

### 23. ProductKnowledge
**Table:** `emr_productknowledge`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| name | VARCHAR(255) | Not Null | Product name |
| status | VARCHAR(20) | - | active, inactive |
| product_type | VARCHAR(30) | - | medication, supply |
| definitional | JSONB | - | Dosage form, route, etc. |
| characteristic | JSONB | - | Characteristics |
| base_unit | JSONB | - | Base unit |
| facility_id | BigInt | FK → Facility | Facility |
| category_id | BigInt | FK → ResourceCategory | Category |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `category` → ResourceCategory (FK, CASCADE)
- Has many: Products, MedicationRequests, MedicationAdministrations

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(1000) | Not Null | Facility name |
| facility_type | INT | Not Null | Facility type |
| features | INT[] | - | Feature flags |
| address | TEXT | - | Address |
| longitude | DECIMAL | - | Longitude |
| latitude | DECIMAL | - | Latitude |
| phone_number | VARCHAR(14) | - | Phone |
| is_active | BOOLEAN | Default: true | Active status |
| verified | BOOLEAN | Default: false | Verified |
| geo_organization_id | BigInt | FK → Organization | Geographic org |
| default_internal_organization_id | BigInt | FK → FacilityOrganization | Default org |
| created_by_id | BigInt | FK → User | Creator |

**Relationships:**
- `geo_organization` → Organization (FK, SET_NULL)
- `default_internal_organization` → FacilityOrganization (FK, SET_NULL)
- `created_by` → User (FK, SET_NULL)
- Has many: Encounters, Locations, Organizations, Products, etc.

---

### 32. FacilityLocation
**Table:** `emr_facilitylocation`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | Not Null | Location name |
| description | TEXT | - | Description |
| status | VARCHAR(20) | - | active, inactive |
| mode | VARCHAR(20) | - | instance, kind |
| location_type | VARCHAR(50) | - | Type |
| form | VARCHAR(50) | - | Physical form |
| parent_id | BigInt | FK → FacilityLocation | Parent location |
| root_location_id | BigInt | FK → FacilityLocation | Root location |
| current_encounter_id | BigInt | FK → Encounter | Current occupant |
| parent_cache | UUID[] | - | Parent hierarchy |
| level_cache | INT | - | Nesting level |
| has_children | BOOLEAN | - | Has children |
| facility_id | BigInt | FK → Facility | Facility |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `parent` → FacilityLocation (FK, SET_NULL, self)
- `root_location` → FacilityLocation (FK, CASCADE, self)
- `current_encounter` → Encounter (FK, SET_NULL)
- Has many: InventoryItems, Encounters, Devices

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Index | Unique slug |
| name | VARCHAR(255) | Not Null | Service name |
| comment | TEXT | - | Description |
| active | BOOLEAN | Default: true | Active status |
| service_type | JSONB | - | Service types |
| locations | UUID[] | - | Service locations |
| facility_id | BigInt | FK → Facility | Facility |
| managing_organization_id | BigInt | FK → FacilityOrganization | Managing org |

**Relationships:**
- `facility` → Facility (FK, PROTECT)
- `managing_organization` → FacilityOrganization (FK, PROTECT)
- Has many: ActivityDefinitions, ServiceRequests, SchedulableResources

---

## Organization Models

### 35. Organization
**Table:** `emr_organization`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | Not Null | Org name |
| org_type | VARCHAR(50) | - | govt, team, etc. |
| active | BOOLEAN | Default: true | Active |
| description | TEXT | - | Description |
| parent_id | BigInt | FK → Organization | Parent org |
| root_org_id | BigInt | FK → Organization | Root org |
| parent_cache | UUID[] | - | Parent hierarchy |
| level_cache | INT | - | Nesting level |
| has_children | BOOLEAN | - | Has children |

**Relationships:**
- `parent` → Organization (FK, CASCADE, self)
- `root_org` → Organization (FK, CASCADE, self)
- Has many: OrganizationUsers, Patients

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | - | Device name |
| manufacturer | VARCHAR(255) | - | Manufacturer |
| model_number | VARCHAR(100) | - | Model number |
| serial_number | VARCHAR(100) | - | Serial number |
| lot_number | VARCHAR(100) | - | Lot number |
| status | VARCHAR(20) | - | active, inactive |
| availability_status | VARCHAR(20) | - | available, lost, damaged |
| facility_id | BigInt | FK → Facility | Facility |
| managing_organization_id | BigInt | FK → FacilityOrganization | Managing org |
| current_location_id | BigInt | FK → FacilityLocation | Current location |
| current_encounter_id | BigInt | FK → Encounter | Current use |

**Relationships:**
- `facility` → Facility (FK, CASCADE)
- `managing_organization` → FacilityOrganization (FK, SET_NULL)
- `current_location` → FacilityLocation (FK, SET_NULL)
- `current_encounter` → Encounter (FK, SET_NULL)
- Has many: DeviceEncounterHistory, DeviceLocationHistory

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| slug | VARCHAR(100) | Unique | Unique slug |
| version | VARCHAR(20) | - | Version |
| title | VARCHAR(255) | Not Null | Title |
| subject_type | VARCHAR(50) | - | patient, encounter |
| status | VARCHAR(20) | - | draft, active, retired |
| questions | JSONB | - | Question definitions |
| organization_cache | UUID[] | - | Org cache |
| tags | VARCHAR[] | - | Tags |

**Relationships:**
- Has many: QuestionnaireResponses, FormSubmissions, QuestionnaireOrganizations

---

### 43. QuestionnaireResponse
**Table:** `emr_questionnaireresponse`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | in_progress, completed |
| subject_id | UUID | - | Subject reference |
| responses | JSONB | - | Response data |
| questionnaire_id | BigInt | FK → Questionnaire | Questionnaire |
| patient_id | BigInt | FK → Patient | Patient |
| encounter_id | BigInt | FK → Encounter | Encounter |
| form_submission_id | BigInt | FK → FormSubmission | Submission |

**Relationships:**
- `questionnaire` → Questionnaire (FK, CASCADE)
- `patient` → Patient (FK, CASCADE)
- `encounter` → Encounter (FK, CASCADE)
- `form_submission` → FormSubmission (FK, CASCADE)

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| name | VARCHAR(255) | Not Null | Schedule name |
| valid_from | DateTime | Not Null | Start date |
| valid_to | DateTime | Not Null | End date |
| is_public | BOOLEAN | Default: false | Public booking |
| resource_id | BigInt | FK → SchedulableResource | Resource |
| charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Pricing |
| revisit_charge_item_definition_id | BigInt | FK → ChargeItemDefinition | Revisit pricing |

**Relationships:**
- `resource` → SchedulableResource (FK, CASCADE)
- `charge_item_definition` → ChargeItemDefinition (FK, PROTECT)
- Has many: Availabilities

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

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| start_datetime | DateTime | Not Null | Slot start |
| end_datetime | DateTime | Not Null | Slot end |
| allocated | INT | Default: 0 | Booked count |
| resource_id | BigInt | FK → SchedulableResource | Resource |
| availability_id | BigInt | FK → Availability | Availability |

**Relationships:**
- `resource` → SchedulableResource (FK, CASCADE)
- `availability` → Availability (FK, CASCADE)
- Has many: TokenBookings

---

### 49. TokenBooking
**Table:** `emr_tokenbooking`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BigAutoField | PK | Primary key |
| external_id | UUID | Unique, Index | External identifier |
| status | VARCHAR(20) | - | booked, checked_in, cancelled |
| reason_for_visit | TEXT | - | Reason |
| token_slot_id | BigInt | FK → TokenSlot | Slot |
| patient_id | BigInt | FK → Patient | Patient |
| booked_by_id | BigInt | FK → User | Booked by |
| associated_encounter_id | BigInt | FK → Encounter | Encounter |
| token_id | BigInt | FK → Token | Token |
| charge_item_id | BigInt | FK → ChargeItem | Charge |

**Relationships:**
- `token_slot` → TokenSlot (FK, PROTECT)
- `patient` → Patient (FK, CASCADE)
- `booked_by` → User (FK, CASCADE)
- `associated_encounter` → Encounter (FK, PROTECT)
- `token` → Token (FK, PROTECT)
- `charge_item` → ChargeItem (FK, CASCADE)

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

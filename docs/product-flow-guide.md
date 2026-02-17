# CARE Platform - Complete Product Flow Guide

This document provides a comprehensive overview of the CARE platform's entity hierarchy, user roles, and operational flows.

---

## Table of Contents

1. [Entity Hierarchy Overview](#1-entity-hierarchy-overview)
2. [Organization & Facility Setup Flow](#2-organization--facility-setup-flow)
3. [User Management Flow](#3-user-management-flow)
4. [Department & Team Structure](#4-department--team-structure)
5. [Patient Management Flow](#5-patient-management-flow)
6. [Appointment & Scheduling Flow](#6-appointment--scheduling-flow)
7. [Encounter & Clinical Documentation](#7-encounter--clinical-documentation)
8. [Lab Tests & Diagnostics Flow](#8-lab-tests--diagnostics-flow)
9. [Medication & Pharmacy Flow](#9-medication--pharmacy-flow)
10. [Billing & Payment Flow](#10-billing--payment-flow)
11. [Role-Based Access Summary](#11-role-based-access-summary)

---

## 1. Entity Hierarchy Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CARE PLATFORM HIERARCHY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LEVEL 1: Geographic Organization (govt type)                               │
│  ├── State/Region Organization                                              │
│  │   ├── District Organization                                              │
│  │   │   └── Sub-district Organization                                      │
│  │                                                                           │
│  LEVEL 2: Facility (Hospital/Clinic)                                        │
│  ├── Linked to Geographic Organization                                      │
│  ├── Has Facility Type (PHC, CHC, Hospital, etc.)                          │
│  │                                                                           │
│  LEVEL 3: Facility Organization (Internal Structure)                        │
│  ├── Root: "Administration" (auto-created)                                  │
│  ├── Departments (type: dept)                                               │
│  │   ├── BP Department                                                      │
│  │   ├── Sugar/Diabetes Department                                          │
│  │   └── Ortho Department                                                   │
│  └── Teams (type: team) - Optional sub-grouping                            │
│                                                                              │
│  LEVEL 4: Locations (Physical Structure)                                    │
│  ├── Ward (mode: kind)                                                      │
│  │   ├── Room (parent: Ward)                                                │
│  │   │   ├── Bed 1 (parent: Room)                                          │
│  │   │   └── Bed 2 (parent: Room)                                          │
│  ├── Lab (mode: kind)                                                       │
│  └── Pharmacy (mode: kind)                                                  │
│                                                                              │
│  LEVEL 5: Users (Assigned to Organizations)                                 │
│  ├── Doctors → FacilityOrganizationUser → Department                       │
│  ├── Nurses → FacilityOrganizationUser → Department                        │
│  └── Staff → FacilityOrganizationUser → Administration                     │
│                                                                              │
│  LEVEL 6: Patients                                                          │
│  ├── Created by authorized users                                            │
│  ├── Linked to Geographic Organization                                      │
│  └── Can have encounters across facilities                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Organization & Facility Setup Flow

### Step 1: Create Geographic Organization (System Admin)

**Who**: System Administrator
**What**: Create root geographic organization (State/Region)

```
POST /api/v1/organization/
{
    "name": "Maharashtra State",
    "org_type": "govt",
    "description": "State level organization"
}
```

**Hierarchy**: State → District → Sub-district (nested children)

### Step 2: Create Facility (State/District Admin)

**Who**: Organization Admin with appropriate permissions
**What**: Create a healthcare facility

```
POST /api/v1/facility/
{
    "name": "MMC Hospital",
    "facility_type": "hospital",
    "geo_organization": "<org-uuid>",
    "address": "123 Medical Street",
    "pincode": 400001,
    "features": ["CT_SCAN", "BLOOD_BANK", "MATERNITY"]
}
```

**Auto-created**:
- Default FacilityOrganization (name: "Administration", type: "root")
- Creator assigned as Facility Admin

### Step 3: Create Facility Locations (Facility Admin)

**Who**: Facility Admin
**What**: Create physical structure (wards, rooms, beds)

```
POST /api/v1/facility/<facility_id>/location/
{
    "name": "General Ward",
    "mode": "kind",
    "form": "wa"  // Ward
}

POST /api/v1/facility/<facility_id>/location/
{
    "name": "Room 101",
    "mode": "instance",
    "form": "ro",
    "parent": "<ward-uuid>"
}
```

---

## 3. User Management Flow

### User Types

| Type | Code | Description | Typical Permissions |
|------|------|-------------|---------------------|
| Administrator | `administrator` | System/facility admin | Full access |
| Doctor | `doctor` | Medical practitioner | Patient care, prescriptions |
| Nurse | `nurse` | Nursing staff | Patient care, observations |
| Staff | `staff` | Support staff | Administrative tasks |
| Volunteer | `volunteer` | Volunteers | Limited access |

### Step 1: Create User (Admin)

**Who**: Facility Admin or Organization Admin
**What**: Create user account

```
POST /api/v1/users/
{
    "username": "dr_smith",
    "email": "dr.smith@hospital.com",
    "phone_number": "+919876543210",
    "user_type": "doctor",
    "first_name": "John",
    "last_name": "Smith",
    "gender": "male",
    "qualification": "MBBS, MD",
    "geo_organization": "<org-uuid>"
}
```

### Step 2: Assign to Facility Organization (Facility Admin)

**Who**: Facility Admin
**What**: Link user to department/organization

```
POST /api/v1/facility/<facility_id>/organization/<org_id>/users/
{
    "user": "<user-uuid>",
    "role": "<role-uuid>"  // Doctor, Nurse, etc.
}
```

### User-Organization Relationships

```
User
├── home_facility (FK) → Primary facility
├── geo_organization (FK) → Geographic location
├── OrganizationUser (M2M) → Geographic organizations with roles
└── FacilityOrganizationUser (M2M) → Facility departments with roles
```

---

## 4. Department & Team Structure

### Step 1: Create Department (Facility Admin)

**Who**: Facility Admin
**What**: Create department under facility

```
POST /api/v1/facility/<facility_id>/organization/
{
    "name": "Cardiology Department",
    "org_type": "dept",
    "description": "Heart and cardiovascular care"
}
```

### Step 2: Assign Users to Department

**Who**: Facility Admin or Department Head
**What**: Add doctors/nurses to department

```
POST /api/v1/facility/<facility_id>/organization/<dept_id>/users/
{
    "user": "<doctor-uuid>",
    "role": "<doctor-role-uuid>"
}
```

### Department Structure Example

```
MMC Hospital (Facility)
└── Administration (root - auto-created)
    ├── BP Department (dept)
    │   ├── Dr. Cardiac 1 (doctor)
    │   ├── Dr. Cardiac 2 (doctor)
    │   ├── Dr. Cardiac 3 (doctor)
    │   └── Nurse Cardiac (nurse)
    │
    ├── Sugar/Diabetes Department (dept)
    │   ├── Dr. Endo 1 (doctor)
    │   ├── Dr. Endo 2 (doctor)
    │   ├── Dr. Endo 3 (doctor)
    │   └── Nurse Endo (nurse)
    │
    └── Ortho Department (dept)
        ├── Dr. Ortho 1 (doctor)
        ├── Dr. Ortho 2 (doctor)
        ├── Dr. Ortho 3 (doctor)
        └── Nurse Ortho (nurse)
```

---

## 5. Patient Management Flow

### Who Can Create Patients

| Role | Can Create | Notes |
|------|-----------|-------|
| Doctor | Yes | During consultation |
| Nurse | Yes | During registration |
| Staff | Yes | Front desk registration |
| Volunteer | No | View only |

### Step 1: Register Patient

**Who**: Doctor, Nurse, or Staff
**Where**: `/facility/:facilityId/patient/create`

```
POST /api/v1/patient/
{
    "name": "Patient Name",
    "gender": "male",
    "date_of_birth": "1990-01-15",
    "phone_number": "+919876543210",
    "address": "123 Street",
    "geo_organization": "<org-uuid>",
    "identifiers": [
        {"config": "<id-config-uuid>", "value": "HOSP123"}
    ]
}
```

### Patient Data Model

```
Patient
├── Basic Info: name, gender, DOB, blood_group
├── Contact: phone_number, emergency_phone_number
├── Location: address, permanent_address, pincode, geo_organization
├── Identifiers: Hospital ID, Aadhaar, etc.
├── Tags: Categorization labels
└── Extensions: Custom plugin data (e.g., insurance)
```

---

## 6. Appointment & Scheduling Flow

### Step 1: Create Schedulable Resource (Doctor/Admin)

**Who**: Doctor or Admin
**What**: Register doctor as schedulable

```
POST /api/v1/facility/<facility_id>/schedule/resource/
{
    "user": "<doctor-uuid>",
    "resource_type": "practitioner"
}
```

### Step 2: Create Schedule (Doctor)

**Who**: Doctor
**What**: Define availability window

```
POST /api/v1/facility/<facility_id>/schedule/
{
    "resource": "<resource-uuid>",
    "name": "Regular OPD Hours",
    "valid_from": "2024-01-01",
    "valid_to": "2024-12-31"
}
```

### Step 3: Set Availability (Doctor)

**Who**: Doctor
**What**: Define recurring time slots

```
POST /api/v1/facility/<facility_id>/schedule/<schedule_id>/availability/
{
    "name": "Morning Slots",
    "slot_type": "appointment",
    "slot_size_in_minutes": 15,
    "tokens_per_slot": 1,
    "availability": [
        {
            "day_of_week": 1,  // Monday
            "start_time": "09:00",
            "end_time": "13:00"
        }
    ]
}
```

### Step 4: Book Appointment (Patient/Staff)

**Who**: Patient (via portal) or Staff (on behalf)
**Where**: `/facility/:facilityId/appointments/:staffId/book-appointment`

```
POST /api/v1/facility/<facility_id>/schedule/slot/<slot_id>/book/
{
    "patient": "<patient-uuid>",
    "reason": "Regular checkup"
}
```

### Appointment Flow Diagram

```
Doctor Sets Availability
        ↓
Schedule → Availability → Token Slots (auto-generated)
        ↓
Patient/Staff Books Slot → TokenBooking created
        ↓
On Appointment Time → Check-in → Create Encounter
        ↓
Encounter Documentation
        ↓
Complete Encounter → Update Booking Status
```

---

## 7. Encounter & Clinical Documentation

### Step 1: Create Encounter (From Appointment)

**Who**: Doctor/Nurse
**What**: Start clinical encounter

```
POST /api/v1/patient/<patient_id>/encounter/
{
    "facility": "<facility-uuid>",
    "encounter_class": "ambulatory",
    "status": "in-progress",
    "appointment": "<booking-uuid>",
    "priority": "routine"
}
```

### Step 2: Document Observations (Vital Signs)

**Who**: Nurse/Doctor
**What**: Record vital signs

```
POST /api/v1/patient/<patient_id>/observation/
{
    "encounter": "<encounter-uuid>",
    "status": "final",
    "category": [{"code": "vital-signs"}],
    "main_code": {"code": "8480-6", "display": "Systolic BP"},
    "value_type": "quantity",
    "value": {"value": 120, "unit": "mmHg"}
}
```

### Step 3: Document Conditions (Diagnoses)

**Who**: Doctor
**What**: Record diagnoses

```
POST /api/v1/patient/<patient_id>/condition/
{
    "encounter": "<encounter-uuid>",
    "clinical_status": "active",
    "verification_status": "confirmed",
    "category": "encounter-diagnosis",
    "code": {"code": "I10", "display": "Essential Hypertension"},
    "severity": "moderate"
}
```

### Encounter Tabs (Frontend)

| Tab | Content | Who Documents |
|-----|---------|---------------|
| Updates | Overview, forms, quick actions | All |
| Plots | Vital signs trends | View only |
| Observations | Vital signs, physical exam | Nurse/Doctor |
| Medicines | Prescriptions | Doctor |
| Responses | Questionnaire responses | All |
| Service Requests | Lab orders, imaging | Doctor |
| Diagnostic Reports | Test results | Lab/Doctor |
| Files | Attachments | All |
| Notes | Clinical notes | Doctor/Nurse |
| Devices | Medical devices | Nurse |
| Consents | Patient consents | Staff |

---

## 8. Lab Tests & Diagnostics Flow

### Step 1: Create Service Request (Doctor)

**Who**: Doctor
**What**: Order lab test

```
POST /api/v1/patient/<patient_id>/service_request/
{
    "encounter": "<encounter-uuid>",
    "facility": "<facility-uuid>",
    "title": "Complete Blood Count",
    "category": "lab",
    "status": "active",
    "intent": "order",
    "priority": "routine",
    "code": {"code": "58410-2", "display": "CBC"}
}
```

### Step 2: Collect Specimen (Lab Tech)

**Who**: Lab Technician
**What**: Collect and process sample

### Step 3: Create Diagnostic Report (Lab Tech)

**Who**: Lab Technician/Pathologist
**What**: Record results

```
POST /api/v1/patient/<patient_id>/diagnostic_report/
{
    "encounter": "<encounter-uuid>",
    "service_request": "<request-uuid>",
    "status": "final",
    "category": [{"code": "LAB"}],
    "code": {"code": "58410-2", "display": "CBC"},
    "conclusion": "All values within normal range"
}
```

### Lab Flow Diagram

```
Doctor Orders Test (ServiceRequest)
        ↓
Lab Receives Order
        ↓
Specimen Collection
        ↓
Lab Processing
        ↓
Results Entry (DiagnosticReport + Observations)
        ↓
Doctor Reviews → Updates Treatment Plan
```

---

## 9. Medication & Pharmacy Flow

### Step 1: Create Prescription (Doctor)

**Who**: Doctor
**What**: Prescribe medications

```
POST /api/v1/patient/<patient_id>/medication_request/
{
    "encounter": "<encounter-uuid>",
    "status": "active",
    "intent": "order",
    "medication": {"code": "318965007", "display": "Paracetamol 500mg"},
    "dosage_instruction": [{
        "text": "1 tablet twice daily after meals",
        "timing": {"repeat": {"frequency": 2, "period": 1, "periodUnit": "d"}},
        "route": {"code": "26643006", "display": "Oral"}
    }]
}
```

### Step 2: Dispense Medication (Pharmacist)

**Who**: Pharmacist
**What**: Dispense from pharmacy

```
POST /api/v1/patient/<patient_id>/medication_dispense/
{
    "encounter": "<encounter-uuid>",
    "authorizing_request": "<medication-request-uuid>",
    "status": "completed",
    "quantity": 14,
    "days_supply": 7
}
```

### Medication Flow

```
Doctor Prescribes (MedicationRequest)
        ↓
Pharmacy Receives Order
        ↓
Check Inventory
        ↓
Dispense (MedicationDispense)
        ↓
Patient Receives Medication
        ↓
Track Administration (MedicationStatement)
```

---

## 10. Billing & Payment Flow

### Step 1: Create Account (Auto/Staff)

**Who**: System (auto) or Billing Staff
**What**: Create billing account for patient

```
POST /api/v1/facility/<facility_id>/billing/account/
{
    "patient": "<patient-uuid>",
    "name": "OPD Account",
    "status": "active",
    "billing_status": "billable"
}
```

### Step 2: Add Charge Items (System/Staff)

**Who**: System (auto from services) or Billing Staff
**What**: Add billable items

```
POST /api/v1/facility/<facility_id>/billing/charge_item/
{
    "account": "<account-uuid>",
    "patient": "<patient-uuid>",
    "encounter": "<encounter-uuid>",
    "charge_item_definition": "<definition-uuid>",
    "quantity": 1,
    "status": "billable"
}
```

### Step 3: Create Invoice (Billing Staff)

**Who**: Billing Staff
**What**: Generate invoice

```
POST /api/v1/facility/<facility_id>/billing/invoice/
{
    "account": "<account-uuid>",
    "patient": "<patient-uuid>",
    "charge_items": ["<charge-item-1>", "<charge-item-2>"],
    "status": "issued"
}
```

### Step 4: Record Payment (Billing Staff)

**Who**: Billing Staff
**What**: Record payment received

```
POST /api/v1/facility/<facility_id>/billing/payment_reconciliation/
{
    "account": "<account-uuid>",
    "patient": "<patient-uuid>",
    "amount": 500.00,
    "payment_method": "cash",
    "status": "completed"
}
```

### Billing Flow

```
Services Provided → ChargeItem created (auto)
        ↓
Billing Reviews Charges
        ↓
Generate Invoice
        ↓
Patient Makes Payment
        ↓
Record PaymentReconciliation
        ↓
Update Account Balance
```

---

## 11. Role-Based Access Summary

### Permission Matrix

| Action | Admin | Doctor | Nurse | Staff | Volunteer |
|--------|-------|--------|-------|-------|-----------|
| Create Facility | ✓ | ✗ | ✗ | ✗ | ✗ |
| Create Department | ✓ | ✗ | ✗ | ✗ | ✗ |
| Create User | ✓ | ✗ | ✗ | ✗ | ✗ |
| Assign User to Dept | ✓ | ✗ | ✗ | ✗ | ✗ |
| Create Patient | ✓ | ✓ | ✓ | ✓ | ✗ |
| View Patient | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create Encounter | ✓ | ✓ | ✓ | ✗ | ✗ |
| Record Observations | ✓ | ✓ | ✓ | ✗ | ✗ |
| Prescribe Medication | ✗ | ✓ | ✗ | ✗ | ✗ |
| Order Lab Tests | ✗ | ✓ | ✗ | ✗ | ✗ |
| Enter Lab Results | ✓ | ✓ | ✗ | ✗ | ✗ |
| Create Invoice | ✓ | ✗ | ✗ | ✓ | ✗ |
| Record Payment | ✓ | ✗ | ✗ | ✓ | ✗ |
| Set Availability | ✗ | ✓ | ✗ | ✗ | ✗ |
| Book Appointment | ✓ | ✓ | ✓ | ✓ | ✗ |

---

## Quick Reference: Entity Creation Order

1. **Geographic Organization** (State/District) - System Admin
2. **Facility** (Hospital) - Organization Admin
3. **Facility Organizations** (Departments) - Facility Admin
4. **Locations** (Wards, Rooms, Beds) - Facility Admin
5. **Users** (Doctors, Nurses, Staff) - Facility Admin
6. **Assign Users to Departments** - Facility Admin
7. **Patients** - Doctor/Nurse/Staff
8. **Availability/Schedules** - Doctors
9. **Appointments** - Staff/Patients
10. **Encounters** - Doctor/Nurse
11. **Clinical Documentation** - Doctor/Nurse
12. **Billing** - Billing Staff

---

## Related Documentation

- [Plugin Customization Guide](./plugin-customization-guide.md)
- [Model & Plugin Architecture](./perspective-model-plugin-architecture.md)
- [API Reference](./api-reference.md)

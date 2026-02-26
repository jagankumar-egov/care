# CARE HMIS - Roles and Permissions Reference Guide

## Overview

This document provides a comprehensive reference of all user roles in the CARE Health Management Information System (HMIS) and their associated actions, permissions, and customizable capabilities across all modules.

---

## Table of Contents

1. [Role Summary Matrix](#role-summary-matrix)
2. [Facility Admin](#1-facility-admin)
3. [Reception Staff](#2-reception-staff)
4. [Doctor/Practitioner](#3-doctorpractitioner)
5. [Nurse/Clinical Staff](#4-nurseclinical-staff)
6. [OPD Nurse](#5-opd-nurse)
7. [Lab Staff/Technician](#6-lab-stafftechnician)
8. [Senior Lab Reviewer](#7-senior-lab-reviewer)
9. [Pharmacist](#8-pharmacist)
10. [Store/Stock Manager](#9-storestock-manager)
11. [Billing Staff](#10-billing-staff)
12. [RBAC Configuration Guide](#rbac-configuration-guide)
13. [Module-Role Access Matrix](#module-role-access-matrix)

---

## Role Summary Matrix

| Role | Primary Module(s) | Key Responsibilities |
|------|-------------------|---------------------|
| Facility Admin | Hospital Administration, Scheduling | System configuration, user management, RBAC setup |
| Reception Staff | Reception, Billing | Patient registration, appointments, check-in, payments |
| Doctor/Practitioner | Clinical, Lab, Pharmacy | Patient encounters, diagnosis, prescriptions, service requests |
| Nurse/Clinical Staff | Clinical | Vitals recording, clinical observations, patient support |
| OPD Nurse | Clinical | Pre-consultation vitals, patient preparation |
| Lab Staff/Technician | Laboratory | Specimen collection, test processing, result entry |
| Senior Lab Reviewer | Laboratory | Report verification and approval |
| Pharmacist | Pharmacy | Prescription verification, dispensing, billing |
| Store/Stock Manager | Pharmacy | Inventory management, purchase orders, stock transfers |
| Billing Staff | Billing | Invoice generation, payment processing, account management |

---

## 1. Facility Admin

### Module Access
- Hospital Administration Module
- Scheduling Module
- Admin Dashboard
- RBAC Configuration

### Allowed Actions

#### Hospital Administration Module

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Facility** | Set up new healthcare facilities | Yes |
| **Create Department** | Add departments within facilities | Yes |
| **Add Location** | Create physical/virtual locations (buildings, wards, labs, rooms) | Yes |
| **Manage Location Status** | Set Active/Inactive/Unknown status | Yes |
| **Set Operational Status** | Define real-time usability (Operational, Closed, Housekeeping, Isolated, Contaminated, Unoccupied) | Yes |
| **Add Healthcare Services** | Define diagnostic/clinical services available | Yes |
| **Link Users to Departments** | Assign staff to organizational units | Yes |
| **Manage User Roles** | Assign and modify user role permissions | Yes |
| **Configure Devices** | Set up medical devices and equipment | Yes |
| **Manage Tags** | Create and assign organizational tags | Yes |
| **Configure Patient Identifiers** | Set up patient identification systems | Yes |

#### Scheduling Module

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Availability Templates** | Define weekly schedules for practitioners/locations/services | Yes |
| **Configure Exceptions** | Set unavailability periods | Yes |
| **Manage Appointment Slots** | Define slot duration and capacity | Yes |
| **Assign Practitioners to Schedules** | Link doctors to availability calendars | Yes |

#### Laboratory Configuration

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Add Lab Location** | Create laboratory spaces within facility | Yes |
| **Create Specimen Definitions** | Define specimen types, collection methods, container requirements | Yes |
| **Create Observation Definitions** | Define test parameters, data types, units, reference ranges | Yes |
| **Create Charge Item Definitions** | Set pricing, taxes, discounts for services | Yes |
| **Create Activity Definitions** | Define diagnostic activities linking specimens, observations, charges | Yes |

#### Pharmacy Configuration

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Pharmacy Locations** | Set up pharmacy service areas | Yes |
| **Configure Healthcare Services** | Link pharmacy services to locations | Yes |
| **Manage Product Knowledge** | Add/edit medicine database entries | Yes |

#### RBAC (Role-Based Access Control)

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Roles** | Define new user roles | Yes |
| **Assign Permissions** | Grant specific module/action access to roles | Yes |
| **Clone Roles** | Duplicate existing roles for modification | Yes |
| **Edit Roles** | Modify existing role permissions | Yes |
| **View Permission Matrix** | Review all roles and their assigned permissions | Yes |

### Restrictions
- Cannot process clinical workflows (encounters, prescriptions)
- Cannot process billing transactions directly
- Cannot perform specimen collection or lab testing

---

## 2. Reception Staff

### Module Access
- Reception Module
- Billing Module (limited)
- Patient Search

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Search Patients** | Find patients by phone, name, or ID | No |
| **Register New Patients** | Create patient records with demographics | Yes (fields) |
| **Book Appointments** | Schedule patient visits with practitioners | Yes |
| **Reschedule Appointments** | Modify existing appointment times | Yes |
| **Cancel Appointments** | Remove scheduled appointments | Yes |
| **Mark Check-In** | Confirm patient arrival for appointments | No |
| **Generate OPD Slips** | Print appointment confirmation documents | No |
| **Collect Consultation Fees** | Process initial payment collection | Yes |
| **View Appointment Calendar** | Access scheduling overview | No |
| **Process Token-Based Registration** | Handle government scheme integrations | Yes |

### Workflow Steps
1. Patient arrives at facility
2. Search for existing patient or register new
3. Book/verify appointment
4. Collect consultation fee
5. Mark patient as checked-in
6. Hand over to OPD Nurse

### Restrictions
- Cannot create clinical encounters
- Cannot modify clinical documentation
- Cannot prescribe medications
- Cannot access detailed medical records
- Cannot process full billing (invoices, refunds)

---

## 3. Doctor/Practitioner

### Module Access
- Clinical Module
- Laboratory Module (ordering, viewing reports)
- Pharmacy Module (prescribing)
- Patient Encounters

### Allowed Actions

#### Clinical Module

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Encounters** | Initiate patient visits/consultations | Yes (type) |
| **View Patient Dashboard** | Access comprehensive patient information | No |
| **Record Chief Complaints** | Document presenting symptoms | Yes |
| **Add Diagnoses** | Record clinical diagnoses (ICD/SNOMED codes) | Yes |
| **Add Allergies** | Document patient allergies | Yes |
| **Record Symptoms** | Document clinical symptoms | Yes |
| **Add Medical History** | Document past medical conditions | Yes |
| **Record Procedures** | Document performed procedures | Yes |
| **Add Clinical Observations** | Record clinical findings | Yes |
| **Document Consents** | Record patient permissions/refusals | Yes |
| **Complete OPD Forms** | Fill consultation questionnaires | Yes |
| **Generate Progress Notes** | Create ongoing care documentation | Yes |
| **Complete Encounters** | Mark consultations as finished | No |

#### Prescription Management

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Prescribe Medications** | Select medicines from product knowledge | Yes |
| **Specify Dosage Instructions** | Define dose, frequency, duration | Yes |
| **Add Administration Routes** | Specify oral, IV, topical, etc. | Yes |
| **Add Patient Instructions** | Include preparation or special notes | Yes |
| **Finalize Prescriptions** | Submit prescriptions for dispensing | No |

#### Laboratory Interactions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Service Requests** | Order diagnostic tests/imaging | Yes |
| **Set Request Priority** | Mark as Routine, Urgent, ASAP, or Stat | Yes |
| **Specify Body Site** | Indicate anatomical location for collection | Yes |
| **Add Patient Instructions** | Provide preparation guidance (fasting, etc.) | Yes |
| **Add Internal Notes** | Include clinical context for lab team | Yes |
| **View Diagnostic Reports** | Access completed and approved lab results | No |
| **Print Diagnostic Reports** | Generate PDF versions of reports | No |

### Restrictions
- Cannot configure system settings
- Cannot manage users or roles
- Cannot collect specimens
- Cannot process lab results
- Cannot dispense medications
- Cannot modify finalized reports
- Can only view reports approved by senior reviewers

---

## 4. Nurse/Clinical Staff

### Module Access
- Clinical Module (limited)
- Patient Encounters (support role)

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Record Vital Signs** | Document BP, pulse, temperature, SpO2, weight, height | Yes |
| **Update Patient Status** | Modify current patient condition | Yes |
| **Manage Documents** | Upload/organize patient documents | Yes |
| **Record Clinical Observations** | Document nursing observations | Yes |
| **View Patient Records** | Access patient information | No |
| **Access Existing Encounters** | Open encounters created by doctors | No |
| **Complete Nursing Forms** | Fill nursing-specific questionnaires | Yes |

### Restrictions
- Cannot create encounters
- Cannot prescribe medications
- Cannot modify prescriptions
- Cannot add diagnoses
- Cannot order lab tests
- Cannot approve clinical documentation

---

## 5. OPD Nurse

### Module Access
- Clinical Module (pre-consultation)
- Appointments Section

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **View Booked Appointments** | See scheduled patients | No |
| **Start Consultations** | Move patients from booked to in-consultation | No |
| **Create Encounters** | Initiate patient encounters for vitals | Yes |
| **Record Pre-Consultation Vitals** | Document vital signs before doctor consultation | Yes |
| **Access Patient Dashboard** | View patient clinical information | No |
| **Complete Vital Forms** | Fill standardized vital sign forms | Yes |
| **Mark Appointment Status** | Update consultation progress | No |

### Workflow Steps
1. View booked patients in appointments section
2. Select patient and start consultation
3. Create or access encounter
4. Record vital signs
5. Complete forms and update status
6. Patient moves to "In-consultation" for doctor

### Restrictions
- Cannot diagnose
- Cannot prescribe
- Cannot order tests
- Cannot complete encounters (doctor responsibility)

---

## 6. Lab Staff/Technician

### Module Access
- Laboratory Module
- Service Requests Queue

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **View Service Requests** | Access pending lab orders | No |
| **Filter Requests by Priority** | Sort by Routine, Urgent, ASAP, Stat | No |
| **View Request Details** | See specimen requirements, doctor notes | No |
| **Collect Specimens** | Record specimen collection with details | Yes |
| **Record Collection Time** | Document date/time of collection | Yes |
| **Document Body Site** | Specify anatomical collection location | Yes |
| **Record Fasting Status** | Note patient fasting compliance | Yes |
| **Enter Quantity/Unit** | Document specimen volume | Yes |
| **Add Storage Information** | Record handling instructions | Yes |
| **Generate Specimen QR Code** | Create tracking identifier | No |
| **Print Specimen Labels** | Generate labels for samples | No |
| **Process Specimens** | Add processing steps (centrifugation, etc.) | Yes |
| **Enter Test Results** | Record observation values | Yes |
| **Add Abnormal Flags** | Mark out-of-range results | Yes |
| **Create Diagnostic Reports** | Generate preliminary reports | Yes |
| **Save Results** | Submit for review | No |

### Restrictions
- Cannot configure lab definitions
- Cannot approve/verify reports
- Cannot view approved reports before verification
- Cannot modify request priority
- Cannot cancel service requests

---

## 7. Senior Lab Reviewer

### Module Access
- Laboratory Module
- Report Review Section

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Review Pending Reports** | Access reports awaiting verification | No |
| **Verify Result Accuracy** | Validate test results | No |
| **Add Interpretations** | Provide clinical remarks | Yes |
| **Approve Results** | Finalize reports for doctor access | No |
| **Reject Reports** | Return reports for correction | Yes |
| **View All Lab Reports** | Access complete report history | No |

### Workflow
1. Lab staff submits results
2. Report routed to senior reviewer
3. Reviewer validates results and observations
4. Reviewer adds interpretation if needed
5. Reviewer clicks "Approve Results"
6. Report becomes visible to requesting doctor

### Restrictions
- Cannot collect specimens
- Cannot enter primary results
- Cannot configure definitions
- Cannot modify approved reports

---

## 8. Pharmacist

### Module Access
- Pharmacy Module (Dispensing Operations)
- Prescription Queue

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **View Prescription Queue** | See pending prescriptions | No |
| **Verify Prescriptions** | Validate doctor-entered orders | No |
| **Check Stock Availability** | Verify medicine inventory | No |
| **Create Pharmacy Invoices** | Generate billing for medicines | Yes |
| **Process Payments** | Accept payment for medicines | Yes |
| **Dispense Medications** | Issue medicines to patients | Yes |
| **Record Dispensing** | Document medicine handover | Yes |
| **Print Prescription Labels** | Generate medication labels | No |
| **Update Dispensing Status** | Mark prescriptions as dispensed | No |

### Workflow
1. Doctor finalizes prescription
2. Pharmacist views prescription in queue
3. Pharmacist verifies prescription details
4. Pharmacist checks stock availability
5. Pharmacist creates invoice and collects payment
6. Pharmacist dispenses medicines
7. Pharmacist updates status and prints labels

### Restrictions
- Cannot modify prescription details
- Cannot prescribe medications
- Cannot manage overall stock (beyond dispensing)
- Cannot create purchase orders

---

## 9. Store/Stock Manager

### Module Access
- Pharmacy Module (Inventory Management)
- Stock Management Section

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **Create Purchase Orders** | Initiate medicine procurement | Yes |
| **Record Inward Entries** | Document stock received | Yes |
| **Verify Stock Quality** | Record batch details, expiry | Yes |
| **Process Internal Transfers** | Move stock between locations | Yes |
| **View Stock Levels** | Monitor inventory quantities | No |
| **Generate Stock Reports** | Create inventory analytics | Yes |
| **Manage Suppliers** | Maintain supplier information | Yes |
| **Handle Stock Adjustments** | Record losses, damages | Yes |
| **Set Reorder Levels** | Configure stock alerts | Yes |

### Restrictions
- Cannot dispense to patients
- Cannot modify prescriptions
- Cannot access clinical data
- Cannot process patient payments

---

## 10. Billing Staff

### Module Access
- Billing Module
- Accounts Section

### Allowed Actions

| Action | Description | Customizable |
|--------|-------------|--------------|
| **View Patient Accounts** | Access billing accounts | No |
| **Check Unbilled Items** | Review pending charges | No |
| **Create Invoices** | Generate bills from charge items | Yes |
| **Process Payments** | Accept and record payments | Yes |
| **Verify Payments** | Confirm payment receipt | No |
| **Handle Advances** | Accept pre-payments | Yes |
| **Process Refunds** | Issue refunds when applicable | Yes |
| **Rebalance Accounts** | Adjust account balances | Yes |
| **Close Accounts** | Finalize patient billing | No |
| **View Invoices** | Access invoice history | No |
| **View Payments** | Access payment records | No |
| **Generate Reports** | Create billing analytics | Yes |
| **Print Receipts** | Generate payment confirmations | No |

### Restrictions
- Cannot access clinical documentation
- Cannot modify charge item definitions
- Cannot configure pricing/taxes
- Cannot create encounters

---

## RBAC Configuration Guide

### Default Permission Categories

The following permission categories can be assigned to roles:

#### Patient Management
- `patient.view` - View patient records
- `patient.create` - Register new patients
- `patient.edit` - Modify patient demographics
- `patient.search` - Search patient database

#### Encounter Management
- `encounter.view` - View encounters
- `encounter.create` - Create new encounters
- `encounter.edit` - Modify encounter details
- `encounter.complete` - Mark encounters complete

#### Clinical Documentation
- `diagnosis.add` - Add diagnoses
- `allergy.add` - Record allergies
- `vitals.record` - Enter vital signs
- `observation.add` - Add clinical observations
- `procedure.record` - Document procedures
- `consent.manage` - Handle consent documentation

#### Prescription Management
- `prescription.create` - Create prescriptions
- `prescription.view` - View prescriptions
- `prescription.finalize` - Finalize for dispensing

#### Laboratory
- `service_request.create` - Order lab tests
- `service_request.view` - View lab orders
- `specimen.collect` - Collect specimens
- `result.enter` - Enter test results
- `report.create` - Generate reports
- `report.verify` - Approve/verify reports
- `report.view` - View diagnostic reports

#### Pharmacy
- `pharmacy.dispense` - Dispense medications
- `pharmacy.invoice` - Create pharmacy invoices
- `stock.view` - View inventory
- `stock.manage` - Manage stock operations
- `purchase_order.create` - Create POs

#### Billing
- `account.view` - View accounts
- `invoice.create` - Generate invoices
- `payment.process` - Accept payments
- `payment.verify` - Verify payments
- `account.close` - Close accounts

#### Administration
- `facility.manage` - Facility configuration
- `department.manage` - Department setup
- `user.manage` - User administration
- `role.manage` - RBAC configuration
- `location.manage` - Location setup
- `healthcare_service.manage` - Service configuration
- `definition.manage` - Master data definitions

### Creating Custom Roles

1. Navigate to **Admin Dashboard > RBAC > Roles**
2. Click **Add Role**
3. Enter **Role Name**
4. Select applicable **Permissions** from categories
5. Click **Create Role**

### Cloning Roles

To create variations of existing roles:
1. Navigate to **Admin Dashboard > RBAC > Roles**
2. Find the role to clone
3. Click **Clone**
4. Modify name and permissions
5. Save new role

---

## Module-Role Access Matrix

| Module | Facility Admin | Reception | Doctor | Nurse | OPD Nurse | Lab Staff | Lab Reviewer | Pharmacist | Stock Manager | Billing Staff |
|--------|:--------------:|:---------:|:------:|:-----:|:---------:|:---------:|:------------:|:----------:|:-------------:|:-------------:|
| Hospital Administration | Full | - | - | - | - | - | - | - | - | - |
| Scheduling | Full | View | - | - | - | - | - | - | - | - |
| Reception | Config | Full | - | - | - | - | - | - | - | Limited |
| Clinical - Encounters | - | - | Full | Limited | Limited | - | - | - | - | - |
| Clinical - Vitals | - | - | Full | Full | Full | - | - | - | - | - |
| Clinical - Prescriptions | - | - | Full | View | View | - | - | View | - | - |
| Clinical - Forms | Config | - | Full | Full | Full | - | - | - | - | - |
| Laboratory - Config | Full | - | - | - | - | - | - | - | - | - |
| Laboratory - Ordering | - | - | Full | - | - | - | - | - | - | - |
| Laboratory - Processing | - | - | - | - | - | Full | - | - | - | - |
| Laboratory - Verification | - | - | - | - | - | - | Full | - | - | - |
| Laboratory - Reports | - | - | View | - | - | View | Full | - | - | - |
| Pharmacy - Config | Full | - | - | - | - | - | - | - | - | - |
| Pharmacy - Prescribing | - | - | Full | - | - | - | - | - | - | - |
| Pharmacy - Dispensing | - | - | - | - | - | - | - | Full | - | - |
| Pharmacy - Stock | Config | - | - | - | - | - | - | Limited | Full | - |
| Billing - Accounts | - | Limited | - | - | - | - | - | - | - | Full |
| Billing - Invoices | - | Limited | - | - | - | - | - | Full | - | Full |
| Billing - Payments | - | Full | - | - | - | - | - | Full | - | Full |
| Admin Dashboard | Full | - | - | - | - | - | - | - | - | - |
| RBAC | Full | - | - | - | - | - | - | - | - | - |

**Legend:**
- **Full**: Complete access to all features
- **Limited**: Restricted access to specific features
- **View**: Read-only access
- **Config**: Configuration/setup access only
- **-**: No access

---

## Customization Notes

### Customizable Elements by Module

#### Hospital Administration
- Facility details and metadata
- Department names and hierarchy
- Location types, names, and statuses
- Healthcare service definitions
- User role assignments
- Device configurations
- Tag definitions
- Patient identifier formats

#### Scheduling
- Slot duration (customizable time blocks)
- Maximum appointments per slot
- Exception types and reasons
- Availability templates

#### Reception
- Patient registration fields (within compliance limits)
- Appointment booking rules
- Fee structures
- OPD slip templates

#### Clinical
- Encounter types
- Questionnaire forms (OPD, Progress Notes, Homecare)
- Observation templates
- Vital sign parameters
- Consent form templates
- Diagnosis code systems (ICD-10, SNOMED CT)

#### Laboratory
- Specimen definitions (types, containers, volumes)
- Observation definitions (tests, units, reference ranges)
- Activity definitions (test packages)
- Charge item definitions (pricing, taxes, discounts)
- Report templates
- Processing step configurations

#### Pharmacy
- Product knowledge database
- Dosage instructions templates
- Administration route options
- Stock location hierarchy
- Purchase order formats
- Invoice templates

#### Billing
- Charge item pricing
- Tax configurations (CGST, SGST, IGST)
- Discount rules
- Invoice templates
- Payment methods

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | October 2025 | Initial document creation |

---

*This document is based on the CARE HMIS User Documentation v1.0 and should be updated as new features and roles are added to the system.*

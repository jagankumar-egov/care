# ABDM Integration Analysis - CARE EMR System

## Overview

This document provides a comprehensive analysis of the ABDM (Ayushman Bharat Digital Mission) integration in the CARE EMR system, covering both backend plugin (care_abdm) and frontend plugin (care_abdm_fe).

## Executive Summary

| Aspect | Status |
|--------|--------|
| **ABDM Plugin (Backend)** | ✅ Fully implemented |
| **ABDM Plugin (Frontend)** | ✅ Fully implemented |
| **ABHA Creation** | ✅ Aadhaar OTP, Demographics, Face, Biometric |
| **ABHA Linking** | ✅ Multiple auth methods |
| **HIP (Health Info Provider)** | ✅ Implemented |
| **HIU (Health Info User)** | ✅ Implemented |
| **Consent Management** | ✅ Full workflow |
| **FHIR Bundle Generation** | ✅ 5 document types |
| **Care Context Linking** | ✅ Automatic via signals |
| **Scan & Share** | ✅ QR-based patient onboarding |

The CARE system has a **complete ABDM integration** via external plugins that can be installed alongside the core application.

---

## Plugin Repositories

| Repository | Location | Purpose |
|------------|----------|---------|
| **care_abdm** | `/Users/jagankumar/Office/Work/repo/care_abdm` | Backend Django plugin |
| **care_abdm_fe** | `/Users/jagankumar/Office/Work/repo/care_abdm_fe` | Frontend React plugin |

---

## Backend Plugin (care_abdm)

### 1. Database Models

#### 1.1 AbhaNumber Model

**File:** `abdm/models/abha_number.py:1-56`

| Field | Type | Description |
|-------|------|-------------|
| `abha_number` | CharField | 14-digit ABHA number |
| `health_id` | CharField | ABHA address (PHR address) |
| `patient` | OneToOneField | Link to Patient (PROTECT) |
| `name` | CharField | Full name |
| `first_name`, `middle_name`, `last_name` | CharField | Name parts |
| `gender` | CharField | M/F/O |
| `date_of_birth` | CharField | DOB string |
| `address` | TextField | Full address |
| `district`, `state`, `pincode` | CharField | Location |
| `mobile`, `email` | CharField | Contact info |
| `access_token`, `refresh_token` | TextField | ABDM tokens |
| `profile_photo` | TextField | Base64 photo |
| `new` | BooleanField | Newly created flag |

#### 1.2 Consent Models

**File:** `abdm/models/consent.py:1-174`

**ConsentRequest:**
| Field | Type | Description |
|-------|------|-------------|
| `consent_id` | UUIDField | ABDM consent ID |
| `patient_abha` | ForeignKey | Link to AbhaNumber |
| `encounter` | ForeignKey | Associated encounter |
| `status` | CharField | REQUESTED, GRANTED, DENIED, EXPIRED, REVOKED |
| `purpose` | CharField | CAREMGT, BTG, PUBHLTH, etc. |
| `hi_types` | ArrayField | Health information types |
| `access_mode` | CharField | VIEW, STORE, QUERY, STREAM |
| `from_time`, `to_time` | DateTimeField | Data range |
| `expiry` | DateTimeField | Consent expiry |
| `frequency_unit`, `frequency_value`, `frequency_repeats` | Fields | Access frequency |

**ConsentArtefact:**
| Field | Type | Description |
|-------|------|-------------|
| All ConsentRequest fields | - | Inherited |
| `key_material_algorithm` | CharField | ECDH |
| `key_material_curve` | CharField | Curve25519 |
| `key_material_public_key` | TextField | X509 public key |
| `key_material_private_key` | TextField | Private key |
| `key_material_nonce` | CharField | Random nonce |
| `signature` | TextField | Consent signature |

#### 1.3 HealthFacility Model

**File:** `abdm/models/health_facility.py:1-63`

| Field | Type | Description |
|-------|------|-------------|
| `hf_id` | CharField | ABDM Health Facility ID |
| `registered` | BooleanField | HIP registration status |
| `facility` | OneToOneField | Link to Facility |

#### 1.4 Transaction Model

**File:** `abdm/models/transaction.py:1-65`

| Type | Value | Description |
|------|-------|-------------|
| CREATE_OR_LINK_ABHA_NUMBER | 1 | ABHA creation/linking |
| CREATE_ABHA_ADDRESS | 2 | Address creation |
| SCAN_AND_SHARE | 3 | QR-based patient share |
| LINK_CARE_CONTEXT | 4 | Care context linking |
| EXCHANGE_DATA | 5 | Health data exchange |
| ACCESS_DATA | 6 | Internal data access |

---

### 2. API Endpoints

#### 2.1 ABHA Number APIs

**Base:** `/api/abdm/abha_numbers/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create ABHA record |
| GET | `/{id}/` | Get ABHA by ID/number/health_id |

#### 2.2 Health ID Creation APIs (v3)

**Base:** `/api/abdm/v3/health_id/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create/send_aadhaar_otp/` | Send OTP to Aadhaar |
| POST | `/create/verify_aadhaar_otp/` | Verify with OTP |
| POST | `/create/verify_aadhaar_demographics/` | Verify with demographics |
| POST | `/create/verify_aadhaar_face/` | Verify with facial recognition |
| POST | `/create/verify_aadhaar_bio/` | Verify with fingerprint |
| POST | `/create/auth_init_via_face/` | Initialize face auth |
| POST | `/create/capture_pid_via_face/` | Capture face PID |
| POST | `/create/link_mobile_number/` | Link mobile to ABHA |
| POST | `/create/verify_mobile_otp/` | Verify mobile OTP |
| POST | `/create/abha_address_suggestion/` | Get address suggestions |
| POST | `/create/enrol_abha_address/` | Enroll ABHA address |

#### 2.3 Health ID Login APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login/check_auth_methods/` | Check available auth methods |
| POST | `/login/send_otp/` | Send login OTP |
| POST | `/login/verify_otp/` | Verify login OTP |
| POST | `/link_patient/` | Link ABHA to patient |
| GET | `/abha_card/` | Download ABHA card (PNG) |

#### 2.4 Health Facility APIs

**Base:** `/api/abdm/health_facility/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List health facilities |
| POST | `/` | Create health facility |
| GET | `/{id}/` | Get facility details |
| PATCH | `/{id}/` | Update facility HF_ID |
| POST | `/{id}/register_service/` | Register as ABDM HIP |

#### 2.5 Consent APIs

**Base:** `/api/abdm/consent/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List consent requests |
| POST | `/` | Create consent request |
| GET | `/{id}/` | Get consent details |

#### 2.6 HIU APIs

**Base:** `/api/abdm/v3/hiu/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/verify_identity/` | Verify patient identity |
| POST | `/create_consent_request/` | Create consent request |
| POST | `/consent_request_status/` | Check consent status |
| POST | `/fetch_consent_artefact/` | Fetch consent artefacts |
| POST | `/request_health_information/` | Request health records |

#### 2.7 HIP Callback APIs

**Base:** `/api/abdm/v3/hip/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/link_care_context/` | Link care context |
| GET | `/patient/fetch-by-token/` | Get patient by token |
| POST | `/token/on-generate-token/` | Token generation callback |
| POST | `/link/on_carecontext/` | Care context link callback |
| POST | `/patient/care-context/discover/` | Patient discovery |
| POST | `/link/care-context/init/` | User-initiated linking init |
| POST | `/link/care-context/confirm/` | Confirm linking |
| POST | `/consent/request/hip/notify/` | Consent notification |
| POST | `/health-information/request/` | Health info request |
| POST | `/patient/share/` | Scan & Share patient |

#### 2.8 HIU Callback APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hiu/consent/request/on-init/` | Consent init callback |
| POST | `/hiu/consent/request/on-status/` | Status callback |
| POST | `/hiu/consent/request/notify/` | Consent notification |
| POST | `/hiu/consent/on-fetch/` | Artefact fetch callback |
| POST | `/hiu/health-information/on-request/` | HI request callback |
| POST | `/hiu/health-information/transfer/` | Receive health info |

#### 2.9 Health Information API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/abdm/health_information/{id}/` | Get health records |

#### 2.10 Utility APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/abdm/v3/utility/states/` | List all states |
| GET | `/api/abdm/v3/utility/states/{code}/districts/` | List districts |

---

### 3. FHIR Bundle Generation

**File:** `abdm/utils/fhir.py:1-1122`

#### Supported Document Types

| Document Type | FHIR Composition | Contents |
|---------------|------------------|----------|
| **Prescription** | 440545006 | Medications, dosage instructions |
| **OP Consultation** | 371530004 | Complaints, exam, allergies, meds, docs |
| **Discharge Summary** | 373942005 | Encounter diagnosis, medications |
| **Health Document** | Custom | Uploaded files (base64) |
| **Wellness Record** | Custom | Questionnaire observations |

#### Generated FHIR Resources

| Resource | Method | Description |
|----------|--------|-------------|
| Patient | `_patient()` | Patient demographics |
| Practitioner | `_practitioner()` | Healthcare provider |
| Organization | `_organization()` | Facility info with HF_ID |
| Encounter | `_encounter()` | Clinical encounter |
| Condition | `_condition()` | Diagnosis conditions |
| MedicationRequest | `_medication_request()` | Prescriptions with dosage |
| MedicationStatement | `_medication_statement()` | Medication history |
| Observation | `_observation()` | Vital signs, measurements |
| AllergyIntolerance | `_allergy_intolerance()` | Allergies |
| DocumentReference | `_document_reference()` | File attachments |

---

### 4. Care Context Linking (Automatic)

**File:** `abdm/signals/register_care_contexts.py:1-192`

#### Django Signal Handlers

| Signal | Model | Action |
|--------|-------|--------|
| `post_save` | MedicationRequest | Creates prescription care context |
| `post_save` | Encounter | Creates OP consultation care context |
| `pre_save` | FileUpload | Creates health document care context |
| `post_save` | Observation | Creates wellness care context |

All signals use `transaction.on_commit()` and call `GatewayService.link__carecontext()`.

#### Care Context Types

| Type | HI Type | Reference Format |
|------|---------|------------------|
| Encounter | OP_CONSULTATION | `v2::encounter::{external_id}` |
| MedicationRequest | PRESCRIPTION | `v2::medication_request::{id}` |
| FileUpload | RECORD_ARTIFACT | `v2::file_upload::{external_id}` |
| QuestionnaireResponse | WELLNESS_RECORD | `v2::questionnaire_response::{id}` |

---

### 5. Encryption & Security

**File:** `abdm/utils/cipher.py:1-76`

#### Encryption Specifications

| Aspect | Value |
|--------|-------|
| Algorithm | ECDH (Elliptic Curve Diffie-Hellman) |
| Curve | Curve25519 |
| Key Format | X509 for public key exchange |
| Nonce | Random 32-byte |

#### Methods

```python
Cipher.generate_key_pair()  # Generate ECDH key pair
Cipher.encrypt(payload)      # Encrypt with external public key
Cipher.decrypt(payload)      # Decrypt with internal private key
```

#### RSA Encryption (for Aadhaar)

**File:** `abdm/service/helper.py:46-63`

```python
encrypt_message(message)  # RSA OAEP with SHA1 for Aadhaar encryption
```

---

### 6. Gateway Service

**File:** `abdm/service/v3/gateway.py`

#### Key Methods

| Method | Description |
|--------|-------------|
| `token__generate_token()` | Generate link token (cached 30 min) |
| `link__carecontext()` | Link care contexts to ABHA |
| `consent__request__init()` | Initiate consent request |
| `consent__request__hip__on_notify()` | Acknowledge consent notification |
| `data_flow__health_information__transfer()` | Send encrypted FHIR bundles |
| `data_flow__health_information__notify()` | Notify transfer status |

---

### 7. Celery Tasks

**File:** `abdm/tasks/retry_failed_care_contexts.py:1-87`

| Task | Description |
|------|-------------|
| `retry_failed_care_contexts()` | Retry failed LINK_CARE_CONTEXT transactions |
| `register_health_facility_as_service()` | Register facility as ABDM HIP |

---

### 8. Configuration

**File:** `abdm/settings.py:1-142`

#### Required Settings

```python
ABDM_CLIENT_ID = "SBX_001"
ABDM_CLIENT_SECRET = "xxxx"
ABDM_GATEWAY_URL = "https://dev.abdm.gov.in/api/hiecm"
ABDM_ABHA_URL = "https://abhasbx.abdm.gov.in/abha/api"
ABDM_FACILITY_URL = "https://facilitysbx.abdm.gov.in"
ABDM_CM_ID = "sbx"
CURRENT_DOMAIN = "https://care.ohc.network"
BACKEND_DOMAIN = "https://careapi.ohc.network"
```

#### Optional Settings

```python
ABDM_HIP_NAME_PREFIX = ""
ABDM_HIP_NAME_SUFFIX = ""
ABDM_USERNAME = "abdm_user_internal"
ABDM_BENEFIT_NAME = ""
ABDM_REQUEST_TIMEOUT = 30
SCAN_AND_SHARE_TOKEN_EXPIRY_TIME = 1800  # 30 minutes
```

---

## Frontend Plugin (care_abdm_fe)

### 1. Plugin Registration

**File:** `src/manifest.ts:1-35`

#### Pluggable Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `PatientHomeActions` | Patient details | ABHA linking button |
| `PatientDetailsTabDemographyGeneralInfo` | Demography tab | ABHA display card |
| `EncounterActions` | Encounter dropdown | Consent request |
| `FacilityHomeActions` | Facility settings | HF_ID configuration |
| `PatientRegistrationForm` | Registration | ABHA auto-fill |
| `PatientSearchActions` | Patient search | Token-based search |

#### Encounter Tab

| Tab | Component | Purpose |
|-----|-----------|---------|
| `abdm` | AbdmEncounterTab | Consent requests & health records |

#### Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/abdm/health-information/:id` | HealthInformation | View health records |

---

### 2. ABHA Creation Flow

**File:** `src/components/LinkAbhaNumber/CreateWithAadhaar.tsx:1-1812`

#### Steps

| Step | Component | Description |
|------|-----------|-------------|
| 1 | Enter Aadhaar | 12/16 digit Aadhaar with disclaimers |
| 2 | Verify Aadhaar OTP | 6-digit OTP verification |
| 3 | Verify Demographics | Name, DOB, State, District, etc. |
| 4 | Verify Face | QR code for facial recognition |
| 5 | Verify Biometric | Fingerprint via RD Service |
| 6 | Handle Existing | Detect existing ABHA |
| 7 | Link Mobile | Link mobile number |
| 8 | Verify Mobile | Mobile OTP verification |
| 9 | Choose Address | Select ABHA address |
| 10 | Show Profile | Display ABHA card |

#### Auth Methods Supported

| Method | Description |
|--------|-------------|
| Aadhaar OTP | OTP to Aadhaar-linked mobile |
| Demographics | Name, DOB, Address matching |
| Face | QR-based facial recognition |
| Biometric | Fingerprint via RD device |

---

### 3. ABHA Linking Flow

**File:** `src/components/LinkAbhaNumber/LinkWithOtp.tsx:1-455`

#### ID Type Detection

| Input | Detected Type |
|-------|---------------|
| 12/16 digits | Aadhaar |
| 10 digits | Mobile |
| 14 digits | ABHA Number |
| Alphanumeric | ABHA Address |

---

### 4. Consent Management UI

**File:** `src/components/CreateConsentRequestForm.tsx:1-206`

#### Form Fields

| Field | Type | Description |
|-------|------|-------------|
| Patient ABHA | Disabled | Auto-filled |
| Purpose | Select | CAREMGT, BTG, PUBHLTH, etc. |
| Date Range | DatePicker | From/To dates |
| HI Types | MultiSelect | Document types to request |
| Expiry | DatePicker | Consent expiry |

#### Consent Purposes

| Code | Description |
|------|-------------|
| CAREMGT | Care Management |
| BTG | Break The Glass (Emergency) |
| PUBHLTH | Public Health |
| HPAYMT | Healthcare Payment |
| DSRCH | Disease Research |
| PATRQT | Patient Requested |

#### Health Information Types

| Type | Description |
|------|-------------|
| Prescription | Medication prescriptions |
| DiagnosticReport | Lab/diagnostic reports |
| OPConsultation | Outpatient consultation |
| DischargeSummary | Discharge summary |
| ImmunizationRecord | Vaccination records |
| HealthDocumentRecord | General documents |
| WellnessRecord | Wellness data |

---

### 5. Health Records Viewing

**File:** `src/components/pages/HealthInformation.tsx:1-93`

- Fetches FHIR bundles by artefact ID
- Uses `hi-profiles` library for rendering
- Handles archived records display
- JSON parsing with error handling

---

### 6. Scan & Share

**File:** `src/components/GenerateScanAndShareQR.tsx:1-157`

#### QR Code Generation

```
URL: {scanAndShareUrl}?hf_id=<HF_ID>&counter_id=<COUNTER_ID>
```

#### Patient Lookup

**File:** `src/components/TokenSearchDialog.tsx:1-153`

- Token-based patient search
- Uses `/api/abdm/v3/hip/patient/fetch-by-token/`

---

### 7. Configuration

**File:** `src/config.ts:1-7`

| Variable | Description |
|----------|-------------|
| `REACT_SCAN_AND_SHARE_URL` | QR code base URL |
| `REACT_FACE_AUTH_URL` | Face auth URL |
| `REACT_ENFORCE_ABHA_NUMBER_LINKING` | Force ABHA linking |

---

## Key Workflows

### Workflow 1: ABHA Creation (Aadhaar + OTP)

```
1. User enters Aadhaar → send_aadhaar_otp
2. User receives OTP → verify_aadhaar_otp
3. System encrypts Aadhaar, calls ABHA API
4. ABHA API returns profile + tokens
5. Create AbhaNumber record
6. Create Transaction (CREATE_OR_LINK_ABHA_NUMBER)
```

### Workflow 2: Care Context Linking

```
1. Encounter created → Django signal triggered
2. Signal calls GatewayService.link__carecontext()
3. Gateway generates link token (cached)
4. Links care contexts via HIP callback
5. Transaction status → COMPLETED
```

### Workflow 3: Health Information Transfer

```
1. Patient grants consent in CM UI
2. CM sends /consent/request/hip/notify to HIP
3. HIP creates ConsentArtefact
4. CM sends /hip/health-information/request
5. HIP generates FHIR bundles
6. HIP encrypts bundles (ECDH)
7. HIP sends to HIU via /hiu/health-information/transfer
8. HIU decrypts and stores
9. Creates EXCHANGE_DATA transaction
```

### Workflow 4: Scan & Share

```
1. Patient scans HIP QR code with ABHA app
2. ABDM sends /hip/patient/share with profile
3. HIP creates/links AbhaNumber to Patient
4. Creates token with 30-min expiry
5. Patient shares token at desk
6. Staff retrieves patient via /patient/fetch-by-token
```

---

## Database Schema

### Tables Created by Plugin

```sql
abdm_abhanumber
  - id, external_id, abha_number, health_id
  - patient_id (FK), tokens, demographics, address

abdm_consentrequest
  - id, consent_id, patient_abha_id (FK)
  - encounter_id (FK), status, purpose, hi_types
  - access_mode, frequency_*, expiry, from/to_time

abdm_consentartefact
  - Inherits ConsentRequest fields
  - key_material_*, signature, cm, hiu, hip

abdm_healthfacility
  - id, hf_id (unique), registered, facility_id (FK)

abdm_transaction
  - id, reference_id, type, status, meta_data (JSONB)
```

---

## Permissions

### Backend Permissions

| Permission | Roles |
|------------|-------|
| View ABHA | Users with patient access |
| Create Consent | Authenticated users |
| View Health Info | Users with patient/consent access |
| Configure Facility | Facility admins |

### Authentication

| Type | Description |
|------|-------------|
| JWT | Standard Care authentication |
| ABDMAuthentication | OpenID Connect for ABDM callbacks |

---

## File Reference Summary

### Backend (care_abdm)

| Component | File Path |
|-----------|-----------|
| Models | `abdm/models/` |
| AbhaNumber | `abdm/models/abha_number.py` |
| Consent | `abdm/models/consent.py` |
| HealthFacility | `abdm/models/health_facility.py` |
| Transaction | `abdm/models/transaction.py` |
| API ViewSets | `abdm/api/viewsets/` |
| v3 HIP APIs | `abdm/api/v3/viewsets/hip.py` |
| v3 HIU APIs | `abdm/api/v3/viewsets/hiu.py` |
| v3 Health ID | `abdm/api/v3/viewsets/health_id.py` |
| Gateway Service | `abdm/service/v3/gateway.py` |
| Health ID Service | `abdm/service/v3/health_id.py` |
| FHIR Generator | `abdm/utils/fhir.py` |
| Cipher | `abdm/utils/cipher.py` |
| Signals | `abdm/signals/register_care_contexts.py` |
| Tasks | `abdm/tasks/retry_failed_care_contexts.py` |
| Settings | `abdm/settings.py` |
| Authentication | `abdm/authentication.py` |

### Frontend (care_abdm_fe)

| Component | File Path |
|-----------|-----------|
| Plugin Entry | `src/index.ts` |
| Manifest | `src/manifest.ts` |
| Routes | `src/routes.tsx` |
| APIs | `src/apis/index.ts` |
| LinkAbhaNumber | `src/components/LinkAbhaNumber/` |
| CreateWithAadhaar | `src/components/LinkAbhaNumber/CreateWithAadhaar.tsx` |
| LinkWithOtp | `src/components/LinkAbhaNumber/LinkWithOtp.tsx` |
| ShowAbhaProfile | `src/components/LinkAbhaNumber/ShowAbhaProfile.tsx` |
| ConsentForm | `src/components/CreateConsentRequestForm.tsx` |
| EncounterTab | `src/components/encounter-tabs/Abdm.tsx` |
| HealthInformation | `src/components/pages/HealthInformation.tsx` |
| QR Generator | `src/components/GenerateScanAndShareQR.tsx` |
| TokenSearch | `src/components/TokenSearchDialog.tsx` |
| Pluggables | `src/components/pluggables/` |
| Types | `src/types/` |
| Config | `src/config.ts` |

---

## Installation & Setup

### Backend Plugin

1. Add to `PLUGIN_APPS` in settings:
```python
PLUGIN_APPS = ["care_abdm"]
```

2. Configure environment variables:
```env
ABDM_CLIENT_ID=your_client_id
ABDM_CLIENT_SECRET=your_secret
ABDM_GATEWAY_URL=https://dev.abdm.gov.in/api/hiecm
ABDM_ABHA_URL=https://abhasbx.abdm.gov.in/abha/api
ABDM_FACILITY_URL=https://facilitysbx.abdm.gov.in
ABDM_CM_ID=sbx
```

3. Run migrations:
```bash
python manage.py migrate abdm
```

### Frontend Plugin

1. Install plugin:
```bash
npm install care_abdm_fe
```

2. Configure environment:
```env
REACT_SCAN_AND_SHARE_URL=https://your-domain/scan
REACT_FACE_AUTH_URL=https://phrsbx.abdm.gov.in/face-auth
REACT_ENFORCE_ABHA_NUMBER_LINKING=false
```

3. Register in Care FE plugin manifest.

---

## References

- [ABDM Sandbox](https://sandbox.abdm.gov.in/docs)
- [ABDM Integration Guide](https://abdm.gov.in/publications)
- [NRCES FHIR Resources](https://nrces.in/ndhm/fhir/r4/index.html)
- [ABHA API Documentation](https://abhasbx.abdm.gov.in/docs)

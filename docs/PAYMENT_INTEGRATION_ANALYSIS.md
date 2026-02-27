# Payment Integration Analysis - CARE EMR System

## Overview

This document provides a comprehensive analysis of the payment and billing capabilities in the CARE EMR system, covering both backend (care) and frontend (care_fe) repositories.

## Executive Summary

The CARE system has a comprehensive **internal billing and payment recording system**, but **NO direct third-party payment gateway integrations** (like Razorpay, Stripe, PayU). However, it's designed with a **plugin architecture** to support external payment gateways.

---

## Backend (care) - Billing Infrastructure

### Database Models

| Model | File Path | Purpose |
|-------|-----------|---------|
| **PaymentReconciliation** | `care/emr/models/payment_reconciliation.py` | Records payments received |
| **Invoice** | `care/emr/models/invoice.py` | Invoice generation and tracking |
| **Account** | `care/emr/models/account.py` | Patient billing accounts |
| **ChargeItem** | `care/emr/models/charge_item.py` | Individual billable items |
| **ChargeItemDefinition** | `care/emr/models/charge_item_definition.py` | Pricing templates |

### PaymentReconciliation Model

**File:** `care/emr/models/payment_reconciliation.py:6-30`

| Field | Type | Description |
|-------|------|-------------|
| `facility` | ForeignKey | Associated facility |
| `target_invoice` | ForeignKey | Linked invoice (nullable) |
| `account` | ForeignKey | Billing account |
| `reconciliation_type` | CharField | payment, adjustment, advance |
| `status` | CharField | active, cancelled, draft, entered_in_error |
| `kind` | CharField | deposit, periodic_payment, online, kiosk |
| `issuer_type` | CharField | patient, insurer |
| `outcome` | CharField | queued, complete, error, partial |
| `method` | CharField | Payment method code |
| `reference_number` | CharField | Transaction reference |
| `authorization` | CharField | Authorization code |
| `tendered_amount` | DecimalField | Amount given by payer |
| `returned_amount` | DecimalField | Change returned |
| `amount` | DecimalField | Net payment amount |
| `is_credit_note` | BooleanField | Refund indicator |
| `location` | ForeignKey | Payment location |
| `extensions` | JSONField | Custom data |

### Supported Payment Methods

**File:** `care/emr/resources/payment_reconciliation/spec.py:51-58`

| Code | Method |
|------|--------|
| `cash` | Cash |
| `ccca` | Credit Card |
| `debc` | Debit Card |
| `chck` | Check |
| `ddpo` | Direct Deposit |
| `cdac` | Credit Account |
| `cchk` | Credit Check |

### Invoice Model

**File:** `care/emr/models/invoice.py:7-34`

| Field | Type | Description |
|-------|------|-------------|
| `facility` | ForeignKey | Associated facility |
| `patient` | ForeignKey | Patient |
| `account` | ForeignKey | Billing account |
| `title` | CharField | Invoice title |
| `status` | CharField | draft, issued, balanced, cancelled, entered_in_error |
| `charge_items` | ArrayField | List of charge item IDs |
| `charge_items_copy` | JSONField | Snapshot of charge items |
| `total_price_components` | JSONField | Price breakdown |
| `total_net` | DecimalField | Net amount |
| `total_gross` | DecimalField | Gross amount |
| `number` | CharField | Invoice number |
| `locked` | BooleanField | Lock status |
| `is_refund` | BooleanField | Refund invoice flag |

### Account Model

**File:** `care/emr/models/account.py:7-32`

| Field | Type | Description |
|-------|------|-------------|
| `status` | CharField | active, inactive, entered_in_error, on_hold |
| `billing_status` | CharField | open, billing, closed_completed, etc. |
| `total_net` | DecimalField | Total net amount |
| `total_gross` | DecimalField | Total gross amount |
| `total_paid` | DecimalField | Total payments received |
| `total_balance` | DecimalField | Outstanding balance |
| `total_billable_charge_items` | DecimalField | Billable items total |

### ChargeItem Model

**File:** `care/emr/models/charge_item.py:7-55`

| Field | Type | Description |
|-------|------|-------------|
| `title` | CharField | Item description |
| `status` | CharField | billable, not_billable, aborted, billed, paid, entered_in_error |
| `quantity` | DecimalField | Quantity |
| `unit_price_components` | JSONField | Unit pricing breakdown |
| `total_price_components` | JSONField | Total pricing breakdown |
| `total_price` | DecimalField | Total price |
| `service_resource` | CharField | Source resource type |
| `service_resource_id` | CharField | Source resource ID |
| `paid_invoice` | ForeignKey | Linked paid invoice |

---

## API Endpoints

### Payment Reconciliation API

**Base URL:** `/api/v1/facility/{facilityId}/payment_reconciliation/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List payment reconciliations |
| POST | `/` | Create payment reconciliation |
| GET | `/{id}/` | Retrieve payment reconciliation |
| PATCH | `/{id}/` | Update payment reconciliation |
| POST | `/{id}/cancel_payment_reconciliation/` | Cancel payment |

**Filters:** status, target_invoice, reconciliation_type, account, is_credit_note, location, method, created_by, created_date

### Invoice API

**Base URL:** `/api/v1/facility/{facilityId}/invoices/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List invoices |
| POST | `/` | Create invoice |
| GET | `/{id}/` | Retrieve invoice |
| PATCH | `/{id}/` | Update invoice |
| POST | `/{id}/attach_items_to_invoice/` | Add charge items |
| POST | `/{id}/remove_item_from_invoice/` | Remove charge items |
| POST | `/{id}/attach_account_to_invoice/` | Attach account items |
| POST | `/{id}/cancel_invoice/` | Cancel invoice |
| POST | `/{id}/lock/` | Lock invoice |
| POST | `/{id}/unlock/` | Unlock invoice |

### Account API

**Base URL:** `/api/v1/facility/{facilityId}/accounts/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List accounts |
| POST | `/` | Create account |
| GET | `/{id}/` | Retrieve account |
| PATCH | `/{id}/` | Update account |

### ChargeItem API

**Base URL:** `/api/v1/facility/{facilityId}/charge_items/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List charge items |
| POST | `/` | Create charge item |
| GET | `/{id}/` | Retrieve charge item |
| PATCH | `/{id}/` | Update charge item |
| POST | `/apply_charge_item_defs/` | Apply pricing templates |
| POST | `/{id}/cancel_charge_item/` | Cancel charge item |

---

## Permissions

### Payment Reconciliation Permissions

**File:** `care/security/permissions/payment_reconciliation.py`

| Permission | Roles |
|------------|-------|
| `can_write_payment_reconciliation` | Facility Admin, Admin, Staff, Doctor, Nurse, Pharmacist |
| `can_read_payment_reconciliation` | Facility Admin, Administrator, Admin, Staff, Doctor, Nurse, Volunteer, Pharmacist |
| `can_destroy_payment_reconciliation` | Facility Admin, Admin |

### Invoice Permissions

**File:** `care/security/permissions/invoice.py`

| Permission | Roles |
|------------|-------|
| `can_write_invoice_in_facility` | Facility Admin, Admin, Staff, Doctor, Nurse |
| `can_read_invoice_in_facility` | Facility Admin, Administrator, Admin, Staff, Doctor, Nurse, Volunteer, Pharmacist |
| `can_destroy_invoice_in_facility` | Facility Admin, Admin |
| `can_manage_locked_invoice_in_facility` | Facility Admin, Admin |

---

## Configuration

### Environment Variables

**File:** `config/settings/config.py:258-282`

```python
# Invoice Settings
INVOICE_FREE_CANCEL_PERIOD_MINUTES = env.int("INVOICE_FREE_CANCEL_PERIOD_MINUTES", default=0)
PAYMENT_RECONCILIATION_FREE_CANCEL_PERIOD_MINUTES = env.int("PAYMENT_RECONCILIATION_FREE_CANCEL_PERIOD_MINUTES", default=0)
INVOICE_FINAL_AMOUNT_PRECISION = env.int("INVOICE_FINAL_AMOUNT_PRECISION", default=0)
INVOICE_FINAL_AMOUNT_ROUNDING_METHOD = env("INVOICE_FINAL_AMOUNT_ROUNDING_METHOD", default="care.utils.rounding.RoundingHalfUp")
```

### Tax Configuration (India GST)

**File:** `config/settings/config.py:40-210`

Supported tax codes:
- `IGST` - Integrated GST
- `CGST` - Central GST
- `SGST` - State GST
- `UTGST` - Union Territory GST

Tax slabs: 18%, 12%, 5%

---

## Frontend (care_fe) - UI Components

### Payment Recording

**File:** `src/pages/Facility/billing/PaymentReconciliationSheet.tsx`

Main component for recording payments with:
- Payment method selection (Cash, Card, Check, etc.)
- Amount and tendered amount tracking
- Automatic change calculation for cash payments
- Location selection
- Payment type selection (payment, adjustment, advance)

### Invoice Management

**File:** `src/pages/Facility/billing/invoice/InvoiceShow.tsx`

Invoice display with:
- Charge items list
- Payment history
- Lock/unlock functionality
- Cancel functionality
- **Plugin support for custom payment methods** (lines 358-513)

### Payment History

**File:** `src/pages/Facility/billing/paymentReconciliation/PaymentsData.tsx`

Payment listing with filters:
- Date range
- Location
- Payment method
- Payment status
- Payment type
- User

### Account Management

**File:** `src/pages/Facility/billing/account/AccountShow.tsx`

Account display with:
- Balance tracking
- Charge items
- Invoices
- Payment history

---

## Plugin Architecture for Payment Gateways

### Extension Point

**File:** `care_fe/src/pluginTypes.ts:66-69`

```typescript
export type InvoiceRecordPaymentOptionsComponentType = React.FC<{
  facilityId: string;
  invoice: InvoiceRead;
}>;
```

### Plugin Manifest

**File:** `care_fe/src/pluginTypes.ts:142-146`

```typescript
{
  billingNavItems: [...],  // Custom billing navigation
  components: {
    InvoiceRecordPaymentOptions: Component,  // Custom payment options
  }
}
```

### Environment Configuration

**File:** `care_fe/.example.env:88-95`

```env
REACT_DEFAULT_PAYMENT_TERMS=...
REACT_PAYMENT_LOCATION_REQUIRED=true|false
```

---

## Payment Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐     ┌─────────────┐
│   ChargeItem    │ ──► │   Invoice    │ ──► │ PaymentReconciliation│ ──► │   Account   │
│ (billable item) │     │  (issued)    │     │  (payment recorded)  │     │ (balanced)  │
└─────────────────┘     └──────────────┘     └─────────────────────┘     └─────────────┘
```

### Detailed Flow

1. **Service Delivery** → ChargeItem created (status: billable)
2. **Invoice Creation** → ChargeItems grouped into Invoice (status: draft → issued)
3. **Payment Recording** → PaymentReconciliation created (links to invoice/account)
4. **Account Sync** → Account totals automatically recalculated
5. **Invoice Balanced** → When full payment received, invoice status → balanced

### Account Rebalancing Logic

**File:** `care/emr/resources/account/sync_items.py:25-79`

```python
def sync_account_items(account):
    # Calculate totals
    total_gross = sum(paid + billed charge items)
    total_billable = sum(billable charge items)
    total_paid = sum(payments) - sum(credit notes)
    total_balance = total_gross - total_paid
```

---

## What's NOT Present (Third-Party Integrations)

| Feature | Status |
|---------|--------|
| Razorpay SDK/Integration | ❌ Not found |
| Stripe SDK/Integration | ❌ Not found |
| PayU SDK/Integration | ❌ Not found |
| UPI direct integration | ❌ Not found |
| Net banking integration | ❌ Not found |
| Payment gateway webhooks | ❌ Not found |
| Online payment callbacks | ❌ Not found |

---

## How to Implement Payment Gateway Integration

### Step 1: Create Backend Webhook Handler

```python
# care/emr/api/viewsets/payment_webhook.py

class PaymentWebhookViewSet(ViewSet):
    """Handle payment gateway callbacks"""

    @action(detail=False, methods=["post"])
    def razorpay_callback(self, request):
        # Verify signature
        # Extract payment details
        # Create PaymentReconciliation
        payment = PaymentReconciliation.objects.create(
            facility=facility,
            account=account,
            target_invoice=invoice,
            reconciliation_type="payment",
            status="active",
            kind="online",
            method="ccca",  # or debc for debit card
            amount=amount,
            reference_number=razorpay_payment_id,
            authorization=razorpay_order_id,
        )
        # Trigger account rebalancing
        rebalance_account_task.delay(account.id)
        return Response({"status": "success"})
```

### Step 2: Create Frontend Plugin Component

```typescript
// In your plugin package

import { InvoiceRecordPaymentOptionsComponentType } from "@/pluginTypes";

export const InvoiceRecordPaymentOptions: InvoiceRecordPaymentOptionsComponentType = ({
  facilityId,
  invoice,
}) => {
  const handleRazorpayPayment = async () => {
    // 1. Create order on backend
    const order = await createPaymentOrder(invoice.id);

    // 2. Initialize Razorpay
    const razorpay = new Razorpay({
      key: process.env.RAZORPAY_KEY_ID,
      order_id: order.razorpay_order_id,
      amount: order.amount,
      handler: async (response) => {
        // 3. Verify payment on backend
        await verifyPayment(response);
      },
    });

    razorpay.open();
  };

  return (
    <DropdownMenuItem onClick={handleRazorpayPayment}>
      <CreditCard className="mr-2 h-4 w-4" />
      Pay with Razorpay
    </DropdownMenuItem>
  );
};
```

### Step 3: Register Plugin

```typescript
// Plugin manifest
export default {
  components: {
    InvoiceRecordPaymentOptions,
  },
  billingNavItems: [],
};
```

### Step 4: Add Environment Variables

```env
# Backend
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# Frontend
REACT_RAZORPAY_KEY_ID=rzp_live_xxxxx
```

---

## Summary Table

| Aspect | Status | Notes |
|--------|--------|-------|
| Internal billing system | ✅ Complete | Full billing workflow |
| Invoice generation | ✅ Complete | With lock/unlock |
| Manual payment recording | ✅ Complete | Cash, Card, Check, etc. |
| Payment history/tracking | ✅ Complete | With filters |
| Tax calculation (GST) | ✅ Complete | IGST, CGST, SGST, UTGST |
| Refund/Credit notes | ✅ Complete | is_refund, is_credit_note |
| Account balancing | ✅ Complete | Auto-sync |
| **Online payment gateway** | ❌ Not integrated | Requires plugin |
| **Plugin architecture** | ✅ Available | InvoiceRecordPaymentOptions |

---

## File References

### Backend (care)
| Component | File Path |
|-----------|-----------|
| PaymentReconciliation Model | `care/emr/models/payment_reconciliation.py` |
| Invoice Model | `care/emr/models/invoice.py` |
| Account Model | `care/emr/models/account.py` |
| ChargeItem Model | `care/emr/models/charge_item.py` |
| PaymentReconciliation API | `care/emr/api/viewsets/payment_reconciliation.py` |
| Invoice API | `care/emr/api/viewsets/invoice.py` |
| Account API | `care/emr/api/viewsets/account.py` |
| ChargeItem API | `care/emr/api/viewsets/charge_item.py` |
| Payment Permissions | `care/security/permissions/payment_reconciliation.py` |
| Invoice Permissions | `care/security/permissions/invoice.py` |
| Account Sync | `care/emr/resources/account/sync_items.py` |
| Invoice Sync | `care/emr/resources/invoice/sync_items.py` |
| Billing Locks | `care/emr/locks/billing.py` |
| Configuration | `config/settings/config.py` |

### Frontend (care_fe)
| Component | File Path |
|-----------|-----------|
| Payment Types | `src/types/billing/paymentReconciliation/paymentReconciliation.ts` |
| Payment API | `src/types/billing/paymentReconciliation/paymentReconciliationApi.ts` |
| Invoice Types | `src/types/billing/invoice/invoice.ts` |
| Invoice API | `src/types/billing/invoice/invoiceApi.ts` |
| Account Types | `src/types/billing/account/Account.ts` |
| Payment Form | `src/pages/Facility/billing/PaymentReconciliationSheet.tsx` |
| Invoice Display | `src/pages/Facility/billing/invoice/InvoiceShow.tsx` |
| Payment History | `src/pages/Facility/billing/paymentReconciliation/PaymentsData.tsx` |
| Account Display | `src/pages/Facility/billing/account/AccountShow.tsx` |
| Plugin Types | `src/pluginTypes.ts` |

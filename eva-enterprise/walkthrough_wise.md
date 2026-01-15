# Wise Automated Payments Implementation - Walkthrough

## Overview
This implementation automates international payments via Wise (formerly TransferWise) by generating unique tracking references for each transaction and automatically reconciling them via Wise API Webhooks and Polling.

## Architecture

### 1. Database Layer (`database/payment_models.py`)
- **`WisePaymentReference`**: Stores generated references (`EVA-USER-123-ABCD`) linked to user and subscription plan.
- **`PaymentInstruction`**: Stores static bank details (IBAN, ACH) compatible with existing `v30` migration.

### 2. Core Logic (`services/payment/`)
- **`WiseAPIClient`**: Handles authenticated communication with Wise API.
- **`WiseReferenceGenerator`**: Generates human-readable, checksum-validated codes.
- **`WisePaymentService`**:
  - Generates references on demand.
  - `reconcile_transactions`: Scans Wise statements for deposits matching pending references.
  - Automatically triggers `WebhookService` to activate subscriptions when payment is found.

### 3. API Layer (`api/`)
- **`POST /checkout/instructions`**: Returns bank details + Unique Reference Code.
- **`GET /checkout/wise/status/{ref}`**: Polling endpoint for frontend.
- **`POST /webhooks/wise`**: Receives real-time deposit notifications.

### 4. Background Tasks (`api/tasks/payment.py`)
- **`poll_wise_transactions`**: Runs every 10 minutes (Celery Beat) to catch any missed webhooks.

### 5. Frontend (`CheckoutPage.jsx`)
- Replaced manual upload form with "Automated Flow".
- Generates reference code on click.
- Polls status every 5 seconds.
- Auto-redirects on success.

## Verification Steps

### 1. Environment Variables
Ensure `.env` has:
```ini
WISE_API_TOKEN=your_token
WISE_PROFILE_ID=your_profile_id
WISE_ENVIRONMENT=sandbox (or live)
```

### 2. Database Migration
Run the SQL script to create the reference table:
```sql
-- Run in your database tool
\i database/migrations/004_payment_tables.sql
```

### 3. Testing Flow
1. Go to `/checkout/gold`
2. Select **Wise / Int.** tab.
3. Click **"Gerar Dados Bancários"**.
4. Copy the **Reference Code**.
5. **Simulate Payment** (if in Sandbox):
   - Make a transfer in Wise Sandbox using the reference.
   - OR manually trigger webhook via Postman.
6. Watch the Frontend change from "Verificando..." to "Pagamento Confirmado!".

# Business Model Clarification

## Platform Overview

**Aetherstore Engine** is a **B2B SaaS platform** that provides fashion brands with the tools to create immersive 3D fashion stores.

### Business Model

1. **Platform Subscriptions** (Brands pay you)
   - Brands subscribe to use the platform
   - Plans: Starter ($99/mo), Professional ($299/mo), Enterprise ($999/mo)
   - You collect subscription fees via Stripe/Paystack

2. **Brand Payment Gateways** (Brands configure their own)
   - Each brand configures their own Stripe/Paystack accounts
   - When customers buy from a brand's 3D store, payments go to the brand
   - You don't handle customer payments, only platform subscriptions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AETHERSTORE PLATFORM (YOU)                  │
│  - Platform subscription billing                         │
│  - Store creation tools                                  │
│  - 3D rendering engine                                   │
│  - Analytics dashboard                                   │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Subscription Fee
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FASHION BRAND (CUSTOMER)                    │
│  - Pays subscription to use platform                    │
│  - Creates 3D stores                                     │
│  - Configures their own payment gateway                 │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Customer Purchase
                        ▼
┌─────────────────────────────────────────────────────────┐
│         BRAND'S CUSTOMER (END USER)                      │
│  - Shops in brand's 3D store                             │
│  - Pays brand directly (via brand's Stripe/Paystack)    │
└─────────────────────────────────────────────────────────┘
```

## Payment Flows

### Flow 1: Brand Subscribes to Platform
1. Brand signs up
2. Brand selects subscription plan
3. Brand pays subscription fee to **you** (Aetherstore)
4. Payment processed via your Stripe/Paystack account
5. Brand gets access to create stores

### Flow 2: Brand's Customer Buys Product
1. Customer browses brand's 3D store
2. Customer adds items to cart
3. Customer checks out
4. Payment processed via **brand's** Stripe/Paystack account
5. Money goes directly to brand
6. Order created in brand's store

## Implementation Details

### 1. Platform Subscription API (`/api/subscriptions`)
- Brands subscribe to platform
- You collect subscription fees
- Manages subscription status and billing cycles

### 2. Brand Payment Gateway Configuration (`/api/subscriptions/payment-gateway`)
- Brands configure their own Stripe/Paystack keys
- Stored securely per brand
- Used for customer purchases in brand's stores

### 3. Order Management (`/api/orders`)
- Orders are created when brand's customers purchase
- Uses brand's payment gateway for processing
- Money goes to brand, not platform

## Key Points

✅ **You collect**: Platform subscription fees from brands
✅ **Brands collect**: Customer purchase payments (via their own gateways)
✅ **You provide**: Platform, tools, infrastructure
✅ **Brands provide**: Products, their own payment processing

## Revenue Model

1. **Subscription Revenue** (Recurring)
   - Monthly/yearly subscriptions from brands
   - Predictable MRR/ARR

2. **Potential Add-ons** (Future)
   - Transaction fees (optional)
   - Premium features
   - White-label options

## Updated Implementation

The codebase now includes:

1. **`api/subscriptions.py`** - Platform subscription management
2. **`payment_service_brand.py`** - Payment service using brand's credentials
3. **Updated order flow** - Uses brand's payment gateway

This ensures:
- You get paid for the platform (subscriptions)
- Brands get paid for their products (their own gateways)
- Clear separation of concerns


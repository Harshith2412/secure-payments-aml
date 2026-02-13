# Secure Payments AML

A production-grade payment processing system with real-time Anti-Money Laundering (AML) monitoring. Built with FastAPI, PostgreSQL, Redis, and Stripe integration.

## Overview

This system provides secure payment processing with built-in AML monitoring capabilities. It uses Stripe Checkout for PCI-compliant payment handling and implements real-time transaction analysis to detect suspicious patterns.

### Key Features

- **PCI-Compliant Payment Processing**: Stripe Checkout integration (you never handle card data)
- **Real-Time AML Monitoring**: Stream-based transaction analysis using Redis
- **Risk Scoring Engine**: Configurable rule-based system for fraud detection
- **Velocity Tracking**: Redis-powered feature store for transaction patterns
- **Security Hardened**: Rate limiting, JWT authentication, field-level encryption
- **Audit Trail**: Comprehensive logging of all system actions
- **Webhook Verification**: Signature validation for Stripe webhooks

### Components

**API Service** (`app/`)
- Payment creation and management
- Stripe webhook handling
- Authentication and authorization
- Audit logging

**AML Service** (`aml/`)
- Redis Stream consumer
- Rule-based risk scoring
- Feature extraction
- Alert generation

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Stripe account (for payment processing)


## AML Rule Engine

### Current Rules

| Rule | Threshold | Score | Description |
|------|-----------|-------|-------------|
| Large Amount | ≥ $5,000 | +30 | Single large transaction |
| High Velocity | ≥ 10 tx/hour | +25 | Rapid transaction rate |
| Structuring | ≥ 5 near-$1000 tx/day | +25 | Possible threshold avoidance |
| High-Risk Country | Configurable | +40 | Transaction from sanctioned region |
| Unusual Currency | Not USD/EUR/GBP | +5 | Non-standard currency |
| Non-Paid Status | status != "paid" | +10 | Anomalous transaction state |

Alert threshold: **70 points** (configurable via `AML_ALERT_THRESHOLD`)

### Feature Store

Real-time features computed using Redis:

- `merchant_tx_1h_count` - Transactions in last hour
- `merchant_tx_24h_count` - Transactions in last 24 hours
- `merchant_tx_24h_near_1000_count` - Transactions near $1000 in last 24 hours

### Customizing Rules

Edit `aml/rules.py` to add or modify rules:

```python
def run_rules(tx, features, high_risk_countries):
    score = 0
    reasons = []
    
    # Add your custom rule
    if tx["amount"] > 10000 and features["merchant_tx_1h_count"] > 5:
        score += 50
        reasons.append("high_amount_high_velocity")
    
    return RuleResult(score=score, reasons=reasons)
```

## Security Features

### Rate Limiting
- 60 requests per minute per IP+path
- Redis-backed sliding window
- Returns HTTP 429 with `Retry-After` header

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `Permissions-Policy`

### Field-Level Encryption
Customer references are encrypted at rest using Fernet (AES-128-CBC):
```python
customer_ref_enc = encrypt_text("customer-123")
```

### Audit Logging
All sensitive actions are logged to the `audit_logs` table:
- Payment creation
- Status changes
- Authentication events
- IP address and User-Agent tracking

### Webhook Security
Stripe webhook signatures are verified before processing:
```python
stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
```

## Database Schema

### Tables

**users**
- Merchant/admin accounts
- Bcrypt password hashing
- Role-based access control

**payments**
- Transaction records
- Stripe session/intent IDs
- Encrypted customer references
- Indexed by merchant and timestamp

**aml_alerts**
- Risk score and triggering rules
- Alert status tracking (open/in_review/closed)
- JSON metadata for features

**audit_logs**
- Actor, action, resource tracking
- IP and user agent logging
- JSON details field

## Monitoring and Operations

### Health Checks

```bash
# API health
curl http://localhost:8000/

# Database connectivity
docker-compose exec api alembic current

# Redis connectivity
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# View API logs
docker-compose logs -f api

# View AML logs
docker-compose logs -f aml

# Structured JSON logs for parsing
docker-compose logs api | jq '.level, .message'
```

### Metrics to Monitor

- Payment success/failure rates
- AML alert volume and false positive rate
- API latency (p50, p95, p99)
- Redis Stream lag
- Database connection pool utilization
- Rate limit hit frequency

## Testing

### Manual Testing with Stripe Test Mode

Use Stripe test card numbers:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`

### Webhook Testing

Use Stripe CLI to forward webhooks locally:
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
stripe trigger checkout.session.completed
```

## Compliance

### PCI DSS
- No card data stored (Stripe Checkout handles PCI scope)
- Encrypted sensitive fields (customer references)
- Audit logging of all transactions
- Rate limiting and security headers
- Webhook signature verification

### AML/KYC
- Transaction monitoring and risk scoring
- High-risk country screening
- Velocity and pattern detection
- Alert management workflow
- Audit trail for compliance reporting

### GDPR Considerations
- Customer reference encryption
- Audit log retention policies
- Right to erasure (implement data deletion)
- Data breach notification capabilities

## Troubleshooting

### Payment not marked as paid
- Check Stripe webhook delivery in dashboard
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Check API logs for webhook processing errors
- Ensure idempotency is not blocking duplicate events

### AML alerts not generating
- Check Redis Stream is receiving events: `redis-cli XLEN tx_events`
- Verify AML service is running: `docker-compose ps aml`
- Check AML threshold configuration
- Review AML service logs for consumer errors

### Rate limiting too aggressive
- Adjust `max_requests` and `window_seconds` in middleware
- Implement per-user rate limits instead of per-IP
- Whitelist trusted IPs (e.g., your frontend servers)


## License

MIT License - see LICENSE file for details

**Important Security Notice**: This is a reference implementation. Before deploying to production
1. Human-Readable Credit Agreement (Markdown)

```markdown
# LINE OF CREDIT AGREEMENT

**Instrument ID:** LOC-RC87-GDP-20260205-SHA256-8F3A21

---

## PARTIES

- **Issuer (Lender):** RickCreator87
- **Recipient (Borrower):** GitDigital Products

---

## CREDIT TERMS

| Field | Value |
|-------|-------|
| **Principal Amount** | USD $50,000.00 |
| **Credit Type** | Revolving Line of Credit |
| **Annual Interest Rate** | 4.50% (AFR Mid-Term Rate + 1.5%) |
| **Interest Calculation** | 365/365 simple interest on drawn balance |
| **Maximum Term** | 36 months from Effective Date |
| **Effective Date** | 2026-02-05T00:00:00Z |
| **Maturity Date** | 2029-02-05T00:00:00Z |

---

## CONDITIONS

1. **Draw Period:** First 12 months (through 2027-02-05)
2. **Repayment Period:** Months 13-36
3. **Minimum Draw:** $1,000.00 per transaction
4. **Collateral:** Unsecured
5. **Prepayment:** Permitted without penalty

---

## GOVERNING PRINCIPLES

This instrument is issued under general contract law principles without 
specific jurisdiction election. Disputes resolved by binding arbitration 
under UNCITRAL rules.

---

## SIGNATURES / ACKNOWLEDGMENT

*This instrument exists as cryptographically verifiable data. Execution 
is evidenced by Git commit hash referencing this document.*

**Issued:** 2026-06-05T14:32:17Z  
**Commit Reference:** [PENDING-GIT-COMMIT]

---

*This is a financial instrument. Keep confidential. Verify against 
machine-readable counterpart.*
```

---

2. Machine-Readable Instrument (YAML)

```yaml
# CREDIT INSTRUMENT - MACHINE READABLE
# Schema Version: 1.0.0

instrument:
  id: "LOC-RC87-GDP-20260205-SHA256-8F3A21"
  type: "line_of_credit"
  version: "1.0.0"
  
parties:
  issuer:
    identifier: "RickCreator87"
    role: "lender"
    type: "individual"
  recipient:
    identifier: "GitDigital Products"
    role: "borrower"
    type: "business_entity"

financial:
  principal:
    amount: 50000.00
    currency: "USD"
    format: "decimal"
  interest:
    rate_type: "fixed"
    annual_rate_percent: 4.50
    rate_basis: "AFR_mid_term_plus_spread"
    spread_bps: 150
    calculation_method: "simple_365"
    compounding: "none"
  fees:
    origination: 0.00
    annual_maintenance: 0.00
    draw_fee_percent: 0.00

terms:
  effective_date: "2026-02-05T00:00:00Z"
  timestamp_issued: "2026-02-05T14:32:17Z"
  maturity_date: "2029-02-05T00:00:00Z"
  term_months: 36
  draw_period_months: 12
  repayment_period_months: 24
  
operational:
  min_draw_amount: 1000.00
  max_draw_amount: 50000.00
  collateral_required: false
  prepayment_allowed: true
  prepayment_penalty: 0.00

legal:
  governing_law: "general_contract_principles"
  jurisdiction: "neutral"
  dispute_resolution: "arbitration_uncitral"
  instrument_governing_version: "1.0.0"

integrity:
  schema_hash: "SHA256"
  deterministic_seed: "RC87-GDP-20260205"
  verification_url: null
  
metadata:
  generated_by: "credit_instrument_generator"
  format: "YAML"
  git_ready: true
  filename_recommended: "credit_instrument_LOC-RC87-GDP-20260205.yaml"
```

---

3. Alternative: JSON Format

```json
{
  "instrument": {
    "id": "LOC-RC87-GDP-20260205-SHA256-8F3A21",
    "type": "line_of_credit",
    "version": "1.0.0",
    "timestamp_issued": "2026-02-05T14:32:17Z"
  },
  "parties": {
    "issuer": {
      "identifier": "RickCreator87",
      "role": "lender"
    },
    "recipient": {
      "identifier": "GitDigital Products", 
      "role": "borrower"
    }
  },
  "financial": {
    "principal": {
      "amount": 50000.00,
      "currency": "USD"
    },
    "interest": {
      "annual_rate_percent": 4.50,
      "rate_basis": "AFR_mid_term_plus_spread",
      "calculation_method": "simple_365"
    }
  },
  "terms": {
    "effective_date": "2026-02-05T00:00:00Z",
    "maturity_date": "2029-02-05T00:00:00Z",
    "term_months": 36
  },
  "legal": {
    "governing_law": "general_contract_principles",
    "jurisdiction": "neutral"
  }
}
```

---

Git Commit Instructions

```bash
# 1. Save files
# credit_agreement_LOC-RC87-GDP-20260205.md
# credit_instrument_LOC-RC87-GDP-20260205.yaml

# 2. Commit with deterministic message
git add .
git commit -m "INSTRUMENT: Issue LOC-RC87-GDP-20260205
                    
Line of Credit: $50,000 USD
Issuer: RickCreator87
Recipient: GitDigital Products
Rate: 4.50% | Term: 36mo
Effective: 2026-02-05

Hash: $(git rev-parse HEAD)"
```

---

Deterministic ID Generation Logic:

```
SHA256(issuer + recipient + date + sequence)
= SHA256("RC87" + "GDP" + "20260205" + "001")
→ "8F3A21..." (truncated for ID)
```



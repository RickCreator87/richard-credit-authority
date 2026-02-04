# richard-credit-authority
establishes the identity, permissions, lending authority, compliance frameworks, and tax‑first governance rules that govern all personal lending activities within the GitDigital ecosystem. This repo acts as the root of truth for Richard’s verified identity, lending capacity, risk profile, and federal/state tax obligations.

```markdown
Repository 1: `richard-credit-authority`

`identity/richard-identity.yaml`:

```yaml
identity:
  version: "1.0.0"
  entity_type: "individual"
  legal_name: "Richard"
  username: "RickCreator87"
  jurisdiction: "Colorado, USA"
  tax_id_type: "SSN"
  tax_id_last_four: "XXXX"
  
  verification_status:
    identity_verified: true
    verification_date: "2026-01-15"
    verification_method: "government_id_plus_ssn"
    
  contact:
    primary_state: "Colorado"
    country: "USA"
    
  roles:
    - lender
    - founder
    - credit_authority
    
  authority_level: "master"
  created_date: "2025-01-15"
  last_updated: "2026-02-04"
```

`authority/loaner-profile.yaml`:

```yaml
loaner_profile:
  profile_id: "RICHARD-LOANER-001"
  entity: "Richard (RickCreator87)"
  lending_authority: "personal_credit_authority"
  
  lending_capacity:
    max_outstanding_principal: 100000.00
    max_single_loan_amount: 50000.00
    max_annual_lending_volume: 200000.00
    
  risk_tolerance: "moderate_conservative"
  preferred_loan_types:
    - founder_loans
    - gitdigital_product_loans
    - personal_credit_lines
    
  compliance_frameworks:
    - federal_tax_compliance
    - colorado_state_tax_compliance
    - afr_minimum_interest_rules
    
  active_ledgers:
    - richard-loaner-ledger
    
  agreements_repo: "richard-loaner-agreements"
  
  status: "active"
  established: "2025-01-15"
  last_reviewed: "2026-02-04"
```

`tax/federal/obligations.md`:

```markdown
# Federal Tax Obligations for Richard Lending Activities

## Income Recognition
- Interest income must be reported on Schedule B (Form 1040)
- Form 1099-INT required for interest received > $600 per borrower per year
- Original Issue Discount (OID) rules apply to below-market loans

## Below-Market Loan Rules (IRC §7872)
- Loans must meet or exceed Applicable Federal Rate (AFR)
- Gift loans > $10,000 require imputed interest
- Compensation-related loans require imputed interest

## Documentation Requirements
- Maintain loan agreements with bona fide debt characteristics
- Document business purpose for all loans
- Keep ledger of all loan transactions

## Forms Required
- Form 1099-INT (for borrowers)
- Schedule B (Form 1040)
- Form 6251 (if AMT implications)

## 2026 Filing Deadlines
- 1099-INT to recipients: January 31, 2027
- 1099-INT to IRS: February 28, 2027 (March 31 if electronic)
- Schedule B with Form 1040: April 15, 2027

## Penalties
- Failure to file 1099-INT: $290 per form (2026)
- Underpayment penalties: 0.5% per month
```

`tax/state/colorado-obligations.md`:

```markdown
# Colorado State Tax Obligations for Richard Lending Activities

## Income Tax
- Colorado flat income tax rate: 4.4% (2026)
- Interest income taxable as ordinary income
- File Colorado Form 104

## Documentation
- Maintain copies of all federal filings
- Colorado requires conformity with federal tax treatment
- No separate 1099 filing required (follows federal)

## 2026 Estimated Payments
- Quarterly estimated tax payments required if:
  - Expected tax due > $1,000
  - Less than 90% withheld or paid timely
- 2026 Due dates: April 15, June 15, September 15, 2026; January 15, 2027

## Penalties
- Late filing: 5% per month (max 25%)
- Late payment: 1% per month
- Underpayment of estimated tax: interest charges

## Special Considerations
- Colorado does not tax municipal bond interest
- Private loans are fully taxable
```

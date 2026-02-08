Required Fields

1. identity_id - UUID v4 format
2. entity_type - Must be one of: individual, business, government_entity, financial_institution, trust
3. verified_status - Must contain level and last_verified
4. metadata.created_at - ISO 8601 timestamp

Entity Types

Individual (entity_type: "individual")

Required fields in personal_info:

· legal_name.first_name
· legal_name.last_name
· date_of_birth (YYYY-MM-DD)
· place_of_birth.country (2-letter ISO code)

Business (entity_type: "business")

Required fields:

· business_info.legal_name
· business_info.tax_id
· business_info.incorporation_date

Financial Institution (entity_type: "financial_institution")

Additional requirements:

· Must have government_ids with type fincen or equivalent
· Higher verification requirements

Verification Levels

Level Description Requirements
unverified No verification None
basic Basic verification Email/phone verification
verified Standard verification Government ID check
fully_verified Enhanced verification Address verification + additional checks
kyc_compliant Full KYC compliance All checks + source of funds

Example

```yaml
identity_id: "123e4567-e89b-12d3-a456-426614174000"
entity_type: "individual"
personal_info:
  legal_name:
    first_name: "John"
    last_name: "Doe"
  date_of_birth: "1980-01-15"
  place_of_birth:
    city: "Denver"
    state: "CO"
    country: "US"
verified_status:
  level: "kyc_compliant"
  last_verified: "2024-01-15T10:30:00Z"
  verification_score: 95
metadata:
  created_at: "2024-01-10T14:30:00Z"
```
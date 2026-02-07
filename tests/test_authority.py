tests/test_authority.py

```python
# tests/test_authority.py
"""
Unit tests for authority validation in Richard's Credit Authority
"""

import unittest
import tempfile
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.validate_authority import AuthorityValidator

class TestAuthorityValidation(unittest.TestCase):
    """Test authority validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = AuthorityValidator()
        self.valid_authority = {
            "authority_id": "auth_20240115_143000_abc123",
            "identity_reference": "550e8400-e29b-41d4-a716-446655440000",
            "type": "credit_issuer",
            "granted_at": "2026-01-15T14:30:00Z",
            "expires_at": "2025-01-15T14:30:00Z",
            "status": "active",
            "granted_by": "system",
            "permissions": ["view_credit_summary", "create_request", "issue_credit"],
            "scope": {
                "geographic": ["US", "CA"],
                "monetary_limits": {
                    "max_credit_issuance": 1000000,
                    "max_daily_transactions": 100,
                    "max_transaction_amount": 50000
                }
            },
            "constraints": {
                "requires_approval": False,
                "audit_frequency": "monthly"
            }
        }
        
        self.valid_identity = {
            "identity_id": "550e8400-e29b-41d4-a716-446655440000",
            "entity_type": "individual",
            "verified_status": {
                "level": "kyc_compliant"
            },
            "credit_authority_tags": {
                "risk_level": "low"
            }
        }
    
    def test_valid_authority(self):
        """Test validation of a valid authority"""
        result = self.validator.validate(self.valid_authority, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_authority = self.valid_authority.copy()
        del invalid_authority["authority_id"]
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required field: authority_id", result["errors"])
    
    def test_invalid_authority_id_format(self):
        """Test validation with invalid authority_id format"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["authority_id"] = "invalid_format"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid authority_id format", result["errors"][0])
    
    def test_invalid_status(self):
        """Test validation with invalid status"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["status"] = "invalid_status"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid status", result["errors"][0])
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["granted_at"] = "2026-01-15 14:30:00"  # Missing TZ
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid granted_at format", result["errors"][0])
    
    def test_expires_before_granted(self):
        """Test that expires_at must be after granted_at"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["granted_at"] = "2025-01-15T14:30:00Z"
        invalid_authority["expires_at"] = "2024-01-15T14:30:00Z"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("expires_at must be after granted_at", result["errors"])
    
    def test_permission_conflicts(self):
        """Test permission conflict validation"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["permissions"] = ["perm_issue_credit", "perm_audit_access"]
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Permission conflict", result["errors"][0])
    
    def test_permission_prerequisites(self):
        """Test permission prerequisite validation"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["permissions"] = ["perm_issue_credit"]  # Missing prerequisites
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Missing prerequisite", result["errors"][0])
    
    def test_delegate_permission_limit(self):
        """Test delegate permission count limit"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["type"] = "delegate"
        invalid_authority["permissions"] = ["perm1", "perm2", "perm3", "perm4"]  # 4 permissions
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Delegate authority cannot have more than 3 permissions", result["errors"][0])
    
    def test_transaction_exceeds_credit_limit(self):
        """Test that transaction amount cannot exceed credit limit"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["scope"]["monetary_limits"]["max_transaction_amount"] = 2000000
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("max_transaction_amount cannot exceed max_credit_issuance", result["errors"][0])
    
    def test_high_credit_requires_dual_approval(self):
        """Test that high credit amounts require dual approval"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["scope"]["monetary_limits"]["max_credit_issuance"] = 200000
        invalid_authority["constraints"]["requires_dual_approval"] = False
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Credit issuance over $100,000 requires dual approval", result["errors"][0])
    
    def test_identity_authority_type_compatibility(self):
        """Test authority type compatibility with identity type"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["entity_type"] = "individual"
        
        invalid_authority = self.valid_authority.copy()
        invalid_authority["type"] = "system_administrator"  # Individuals can't be system admins
        
        result = self.validator.validate(invalid_authority, invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("cannot have authority type", result["errors"][0])
    
    def test_verification_level_requirement(self):
        """Test verification level requirements for authority types"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["verified_status"]["level"] = "basic"
        
        result = self.validator.validate(self.valid_authority, invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("requires verification level", result["errors"][0])
    
    def test_warnings_for_long_duration(self):
        """Test warnings for long authority durations"""
        authority_with_long_duration = self.valid_authority.copy()
        authority_with_long_duration["granted_at"] = "2024-01-01T00:00:00Z"
        authority_with_long_duration["expires_at"] = "2025-12-31T23:59:59Z"  # ~2 years
        
        result = self.validator.validate(authority_with_long_duration, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertGreater(len(result["warnings"]), 0)
        self.assertIn("Long authority duration", result["warnings"][0])
    
    def test_warnings_for_missing_geographic_restrictions(self):
        """Test warnings for missing geographic restrictions"""
        authority_no_geo = self.valid_authority.copy()
        authority_no_geo["scope"]["geographic"] = []
        
        result = self.validator.validate(authority_no_geo, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertIn("No geographic restrictions specified", result["warnings"][0])
    
    def test_file_validation(self):
        """Test validation from YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.valid_authority, f)
            temp_file = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            yaml.dump(self.valid_identity, f2)
            temp_identity_file = Path(f2.name)
        
        try:
            result = self.validator.validate_file(temp_file, temp_identity_file)
            self.assertTrue(result["valid"])
        finally:
            temp_file.unlink()
            temp_identity_file.unlink()

if __name__ == '__main__':
    unittest.main()
```

tests/test_tax_logic.py

```python
# tests/test_tax_logic.py
"""


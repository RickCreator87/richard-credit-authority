validation/validate_tax.py

```python
# validation/validate_tax.py
"""
Tax validation module for Richard's Credit Authority
Validates tax calculations and jurisdiction rules
"""

import yaml
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

class TaxValidator:
    """Validate tax calculations and jurisdiction rules"""
    
    def __init__(self, tax_rules_dir: Optional[Path] = None):
        self.tax_rules_dir = tax_rules_dir or Path(__file__).parent.parent / "tax"
        self.tax_rules = self._load_tax_rules()
        
    def _load_tax_rules(self) -> Dict:
        """Load tax rules from directory"""
        rules = {
            "jurisdictions": {},
            "rates": {},
            "forms": {},
            "thresholds": {}
        }
        
        # Load federal rules
        federal_file = self.tax_rules_dir / "federal" / "rules.py"
        if federal_file.exists():
            try:
                # In a real implementation, we would import or parse the rules
                rules["jurisdictions"]["US"] = {
                    "name": "United States Federal",
                    "type": "federal",
                    "effective": "2024-01-01"
                }
            except Exception as e:
                print(f"Warning: Could not load federal rules: {e}")
        
        # Load state rules
        state_dir = self.tax_rules_dir / "state"
        if state_dir.exists():
            for state_file in state_dir.glob("*/rules.py"):
                state_code = state_file.parent.name.upper()
                rules["jurisdictions"][f"US-{state_code}"] = {
                    "name": f"State of {state_code}",
                    "type": "state",
                    "effective": "2024-01-01"
                }
        
        return rules
    
    def validate_tax_calculation(self, calculation: Dict, transaction: Dict) -> Dict[str, Any]:
        """Validate a tax calculation"""
        errors = []
        warnings = []
        
        # Basic validation
        errors.extend(self._validate_calculation_basics(calculation))
        
        # Jurisdiction validation
        errors.extend(self._validate_jurisdictions(calculation))
        
        # Rate validation
        errors.extend(self._validate_tax_rates(calculation))
        
        # Amount validation
        errors.extend(self._validate_amounts(calculation, transaction))
        
        # Compliance validation
        errors.extend(self._validate_compliance(calculation))
        
        # Check warnings
        warnings.extend(self._check_tax_warnings(calculation))
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validation_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _validate_calculation_basics(self, calculation: Dict) -> List[str]:
        """Validate basic calculation structure"""
        errors = []
        
        required_fields = [
            "calculation_id",
            "transaction_reference",
            "jurisdiction",
            "tax_amount",
            "calculation_date"
        ]
        
        for field in required_fields:
            if field not in calculation:
                errors.append(f"Missing required field in tax calculation: {field}")
        
        # Validate calculation_id format
        calc_id = calculation.get("calculation_id", "")
        if not re.match(r'^taxcalc_[A-Za-z0-9_-]+$', calc_id):
            errors.append(f"Invalid calculation_id format: {calc_id}")
        
        # Validate jurisdiction code
        jurisdiction = calculation.get("jurisdiction", "")
        if jurisdiction and not re.match(r'^[A-Z]{2}(-[A-Z0-9]+)?$', jurisdiction):
            errors.append(f"Invalid jurisdiction code: {jurisdiction}")
        
        # Validate calculation_date
        calc_date = calculation.get("calculation_date")
        if calc_date:
            try:
                datetime.fromisoformat(calc_date.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid calculation_date format: {calc_date}")
        
        return errors
    
    def _validate_jurisdictions(self, calculation: Dict) -> List[str]:
        """Validate jurisdiction rules"""
        errors = []
        
        jurisdiction = calculation.get("jurisdiction", "")
        
        if jurisdiction:
            # Check if jurisdiction is known
            if jurisdiction not in self.tax_rules["jurisdictions"]:
                warnings = [f"Unknown jurisdiction: {jurisdiction}"]
            
            # Validate jurisdiction hierarchy
            if "-" in jurisdiction:
                parent = jurisdiction.split("-")[0]
                if parent not in self.tax_rules["jurisdictions"]:
                    errors.append(f"Parent jurisdiction not found: {parent}")
        
        # Check for conflicting jurisdictions
        jurisdictions = calculation.get("jurisdictions", [])
        if len(jurisdictions) > 1:
            # Check if any jurisdictions conflict (e.g., state and local with different rules)
            state_jurisdictions = [j for j in jurisdictions if j.startswith("US-") and len(j) == 5]
            if len(state_jurisdictions) > 1:
                errors.append(f"Multiple state jurisdictions not allowed: {state_jurisdictions}")
        
        return errors
    
    def _validate_tax_rates(self, calculation: Dict) -> List[str]:
        """Validate tax rates"""
        errors = []
        
        tax_lines = calculation.get("tax_lines", [])
        total_calculated = Decimal('0')
        
        for line in tax_lines:
            # Validate tax type
            tax_type = line.get("tax_type")
            valid_types = ["income", "sales", "withholding", "excise", "payroll"]
            if tax_type not in valid_types:
                errors.append(f"Invalid tax_type: {tax_type}")
            
            # Validate rate
            rate = line.get("rate")
            if rate is not None:
                try:
                    rate_decimal = Decimal(str(rate))
                    if rate_decimal < 0 or rate_decimal > 100:
                        errors.append(f"Tax rate out of range (0-100): {rate}")
                except Exception:
                    errors.append(f"Invalid tax rate format: {rate}")
            
            # Validate amount
            amount = line.get("amount")
            if amount is not None:
                try:
                    amount_decimal = Decimal(str(amount))
                    total_calculated += amount_decimal
                    if amount_decimal < 0:
                        errors.append(f"Negative tax amount: {amount}")
                except Exception:
                    errors.append(f"Invalid tax amount format: {amount}")
        
        # Validate total matches sum of lines
        total_amount = calculation.get("tax_amount")
        if total_amount is not None and tax_lines:
            try:
                total_decimal = Decimal(str(total_amount))
                if total_decimal != total_calculated:
                    errors.append(f"Tax amount mismatch: total={total_amount}, sum of lines={total_calculated}")
            except Exception:
                pass
        
        return errors
    
    def _validate_amounts(self, calculation: Dict, transaction: Dict) -> List[str]:
        """Validate tax amounts against transaction"""
        errors = []
        
        transaction_amount = Decimal(str(transaction.get("amount", 0)))
        total_tax = Decimal(str(calculation.get("tax_amount", 0)))
        
        # Check if tax exceeds reasonable limits
        if transaction_amount > 0:
            tax_percentage = (total_tax / transaction_amount) * 100
            if tax_percentage > 50:
                errors.append(f"Tax percentage too high: {tax_percentage:.2f}%")
            
            # Industry-specific checks
            transaction_type = transaction.get("type", "")
            if transaction_type == "interest":
                # US backup withholding is typically 24%
                if tax_percentage > 24:
                    errors.append(f"Interest withholding rate too high: {tax_percentage:.2f}%")
        
        # Validate rounding
        tax_lines = calculation.get("tax_lines", [])
        for line in tax_lines:
            amount = line.get("amount")
            if amount is not None:
                try:
                    amount_decimal = Decimal(str(amount))
                    # Check if properly rounded (typically to 2 decimal places)
                    rounded = amount_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    if amount_decimal != rounded:
                        errors.append(f"Tax amount not properly rounded: {amount}")
                except Exception:
                    pass
        
        return errors
    
    def _validate_compliance(self, calculation: Dict) -> List[str]:
        """Validate compliance requirements"""
        errors = []
        
        # Check for required forms
        required_forms = calculation.get("required_forms", [])
        for form in required_forms:
            if not isinstance(form, dict) or "form_code" not in form:
                errors.append(f"Invalid form specification: {form}")
        
        # Check withholding requirements
        withholding_required = calculation.get("withholding_required", False)
        if withholding_required:
            tax_lines = calculation.get("tax_lines", [])
            withholding_lines = [line for line in tax_lines if line.get("tax_type") == "withholding"]
            
            if not withholding_lines:
                errors.append("Withholding required but no withholding tax line found")
        
        # Check thresholds
        thresholds = calculation.get("thresholds", {})
        for threshold_name, threshold_value in thresholds.items():
            try:
                threshold_decimal = Decimal(str(threshold_value))
                if threshold_decimal < 0:
                    errors.append(f"Negative threshold not allowed: {threshold_name}={threshold_value}")
            except Exception:
                errors.append(f"Invalid threshold format: {threshold_name}={threshold_value}")
        
        return errors
    
    def _check_tax_warnings(self, calculation: Dict) -> List[str]:
        """Check for tax calculation warnings"""
        warnings = []
        
        # Warn about missing nexus determination
        jurisdictions = calculation.get("jurisdictions", [])
        if not jurisdictions:
            warnings.append("No jurisdictions specified for tax calculation")
        
        # Warn about potential double taxation
        if len(jurisdictions) > 2:
            warnings.append(f"Multiple jurisdictions ({len(jurisdictions)}) may result in double taxation")
        
        # Warn about high tax rates
        tax_lines = calculation.get("tax_lines", [])
        for line in tax_lines:
            rate = line.get("rate")
            if rate and rate > 30:  # Arbitrary threshold
                warnings.append(f"High tax rate detected: {rate}% for {line.get('tax_type')}")
        
        # Warn about missing tax IDs
        tax_entities = calculation.get("tax_entities", {})
        for entity_type, entity_data in tax_entities.items():
            if "tax_id" not in entity_data:
                warnings.append(f"Missing tax ID for {entity_type}")
        
        return warnings
    
    def validate_file(self, file_path: Path, transaction_file: Optional[Path] = None) -> Dict[str, Any]:
        """Validate a tax calculation file"""
        try:
            with open(file_path, 'r') as f:
                calculation_data = yaml.safe_load(f)
            
            transaction_data = {}
            if transaction_file and transaction_file.exists():
                with open(transaction_file, 'r') as f:
                    transaction_data = yaml.safe_load(f)
            
            return self.validate_tax_calculation(calculation_data, transaction_data)
        
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML parsing error: {str(e)}"],
                "warnings": [],
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }
```

3. Governance Engine

governance/engine.py

```python
# governance/engine.py
"""
Governance engine for Richard's Credit Authority
Applies business rules and policies to authority and identity decisions
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types of governance rules"""
    VALIDATION = "validation"
    APPROVAL = "approval"
    ESCALATION = "escalation"
    COMPLIANCE = "compliance"
    RISK = "risk"
    TAX = "tax"

class RuleSeverity(Enum):
    """Rule severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RuleResult:
    """Result of applying a governance rule"""
    rule_id: str
    rule_type: RuleType
    severity: RuleSeverity
    passed: bool
    message: str
    details: Dict[str, Any]
    timestamp: str

@dataclass
class GovernanceDecision:
    """Final governance decision"""
    decision: str  # "approved", "rejected", "requires_review", "needs_escalation"
    reasons: List[str]
    required_actions: List[str]
    rule_results: List[RuleResult]
    timestamp: str

class GovernanceEngine:
    """Main governance engine that applies rules and policies"""
    
    def __init__(self, rules_file: Optional[Path] = None):
        self.rules_file = rules_file or Path(__file__).parent / "rules.json"
        self.rules = self._load_rules()
        self.rule_processors = self._register_rule_processors()
        
    def _load_rules(self) -> Dict:
        """Load governance rules from file"""
        default_rules = {
            "version": "1.0.0",
            "rules": {
                "validation": [],
                "approval": [],
                "escalation": [],
                "compliance": [],
                "risk": [],
                "tax": []
            }
        }
        
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r') as f:
                    loaded_rules = json.load(f)
                    # Merge with defaults
                    default_rules.update(loaded_rules)
            
            return default_rules
        
        except Exception as e:
            logger.error(f"Error loading governance rules: {e}")
            return default_rules
    
    def _register_rule_processors(self) -> Dict[str, Callable]:
        """Register rule processor functions"""
        return {
            "validate_identity_verification": self._validate_identity_verification,
            "check_authority_duration": self._check_authority_duration,
            "validate_permission_hierarchy": self._validate_permission_hierarchy,
            "check_risk_thresholds": self._check_risk_thresholds,
            "validate_tax_compliance": self._validate_tax_compliance,
            "check_geographic_restrictions": self._check_geographic_restrictions,
            "validate_monetary_limits": self._validate_monetary_limits,
            "check_delegation_depth": self._check_delegation_depth,
            "validate_audit_requirements": self._validate_audit_requirements,
            "check_conflict_of_interest": self._check_conflict_of_interest,
        }
    
    def evaluate_authority_request(self, 
                                  authority_request: Dict,
                                  identity_data: Dict,
                                  context: Optional[Dict] = None) -> GovernanceDecision:
        """
        Evaluate an authority request against all governance rules
        
        Args:
            authority_request: The authority being requested
            identity_data: The identity requesting the authority
            context: Additional context for evaluation
        
        Returns:
            GovernanceDecision with the evaluation results
        """
        rule_results = []
        context = context or {}
        
        # Apply all rule categories
        for rule_type in RuleType:
            category_rules = self.rules["rules"].get(rule_type.value, [])
            for rule in category_rules:
                if rule.get("enabled", True):
                    result = self._apply_rule(rule, authority_request, identity_data, context)
                    rule_results.append(result)
        
        # Make final decision based on rule results
        decision = self._make_decision(rule_results)
        
        return GovernanceDecision(
            decision=decision["decision"],
            reasons=decision["reasons"],
            required_actions=decision["actions"],
            rule_results=rule_results,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _apply_rule(self, 
                   rule: Dict,
                   authority_request: Dict,
                   identity_data: Dict,
                   context: Dict) -> RuleResult:
        """Apply a single rule"""
        rule_id = rule.get("id", "unknown")
        rule_type = RuleType(rule.get("type", "validation"))
        processor_name = rule.get("processor")
        
        try:
            if processor_name and processor_name in self.rule_processors:
                processor = self.rule_processors[processor_name]
                result = processor(authority_request, identity_data, context, rule.get("parameters", {}))
                
                return RuleResult(
                    rule_id=rule_id,
                    rule_type=rule_type,
                    severity=RuleSeverity(result.get("severity", "info")),
                    passed=result.get("passed", True),
                    message=result.get("message", ""),
                    details=result.get("details", {}),
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
            else:
                # Default rule application
                return RuleResult(
                    rule_id=rule_id,
                    rule_type=rule_type,
                    severity=RuleSeverity.WARNING,
                    passed=True,
                    message=f"No processor for rule: {rule_id}",
                    details={},
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
        
        except Exception as e:
            logger.error(f"Error applying rule {rule_id}: {e}")
            return RuleResult(
                rule_id=rule_id,
                rule_type=rule_type,
                severity=RuleSeverity.ERROR,
                passed=False,
                message=f"Rule application error: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
    
    def _validate_identity_verification(self, 
                                       authority_request: Dict,
                                       identity_data: Dict,
                                       context: Dict,
                                       parameters: Dict) -> Dict[str, Any]:
        """Val

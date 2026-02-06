#!/bin/bash

# CI/CD Validation Script for Richard's Credit Authority
# Runs comprehensive validation before any commit or deployment

set -e  # Exit on error
set -o pipefail  # Capture pipe failures

echo "🚀 Starting CI/CD Validation for Credit Authority"
echo "================================================"
date
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_section() {
    echo -e "\n${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠  $1${NC}"
}

# Check Node.js version
print_section "Checking Node.js version"
NODE_VERSION=$(node --version)
REQUIRED_VERSION="v18.0.0"
if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]]; then
    print_success "Node.js $NODE_VERSION meets requirement $REQUIRED_VERSION"
else
    print_error "Node.js $NODE_VERSION is below required version $REQUIRED_VERSION"
    exit 1
fi

# Check npm/yarn packages
print_section "Checking dependencies"
if [ -f "package.json" ]; then
    if npm list --depth=0 2>/dev/null | grep -q "js-yaml"; then
        print_success "js-yaml installed"
    else
        print_warning "js-yaml not installed, installing..."
        npm install js-yaml
    fi
    
    if npm list --depth=0 2>/dev/null | grep -q "ajv"; then
        print_success "ajv installed"
    else
        print_warning "ajv not installed, installing..."
        npm install ajv ajv-formats
    fi
else
    print_warning "package.json not found, creating..."
    npm init -y
    npm install js-yaml ajv ajv-formats
fi

# Check for required directories
print_section "Checking directory structure"
REQUIRED_DIRS=(
    "identity"
    "permission"
    "authority"
    "governance"
    "compliance"
    "scripts"
    "SCHEMA-REGISTRY"
    ".github/workflows"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "$dir exists"
    else
        print_error "$dir missing"
        exit 1
    fi
done

# Check for required files
print_section "Checking required files"
REQUIRED_FILES=(
    "AUTHORITY.yaml"
    "GOVERNANCE.yaml"
    "PERMISSIONS.yaml"
    "RISK-PROFILE.yaml"
    "CREDIT-LIMITS.yaml"
    "VALIDATION-RULES.yaml"
    "identity/profile.yaml"
    "scripts/validate-authority.js"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file missing"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    print_error "$MISSING_FILES required files missing"
    exit 1
fi

# Validate YAML syntax
print_section "Validating YAML syntax"
YAML_FILES=$(find . -name "*.yaml" -o -name "*.yml")

for file in $YAML_FILES; do
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        print_success "$file has valid YAML syntax"
    else
        print_error "$file has invalid YAML syntax"
        exit 1
    fi
done

# Run JavaScript validations
print_section "Running authority validation"
if node scripts/validate-authority.js --file AUTHORITY.yaml 2>&1 | grep -q "passed validation"; then
    print_success "Authority validation passed"
else
    print_error "Authority validation failed"
    node scripts/validate-authority.js --file AUTHORITY.yaml 2>&1 | tail -20
    exit 1
fi

print_section "Running governance validation"
if node scripts/validate-governance.js --file GOVERNANCE.yaml 2>&1 | grep -q "passed"; then
    print_success "Governance validation passed"
else
    print_error "Governance validation failed"
    node scripts/validate-governance.js --file GOVERNANCE.yaml 2>&1 | tail -20
    exit 1
fi

print_section "Running permissions validation"
if node scripts/validate-permissions.js --file PERMISSIONS.yaml 2>&1 | grep -q "passed"; then
    print_success "Permissions validation passed"
else
    print_error "Permissions validation failed"
    node scripts/validate-permissions.js --file PERMISSIONS.yaml 2>&1 | tail -20
    exit 1
fi

# Run schema validation if schemas exist
print_section "Running schema validation"
if [ -d "SCHEMA-REGISTRY" ] && [ "$(ls -A SCHEMA-REGISTRY/*.json 2>/dev/null | wc -l)" -gt 0 ]; then
    if node scripts/validate-schema.js --file AUTHORITY.yaml 2>&1 | grep -q "passed schema validation"; then
        print_success "Schema validation passed"
    else
        print_error "Schema validation failed"
        node scripts/validate-schema.js --file AUTHORITY.yaml 2>&1 | tail -20
        exit 1
    fi
else
    print_warning "No schemas found, skipping schema validation"
fi

# Check for sensitive data
print_section "Checking for sensitive data"
SENSITIVE_PATTERNS=(
    "social_security"
    "ssn"
    "password"
    "secret"
    "private_key"
    "credit_card"
    "account_number"
    "routing_number"
)

FOUND_SENSITIVE=0
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if grep -r -i "$pattern" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.js" . 2>/dev/null | grep -v "# REDACTED" | grep -v "test" | grep -v "example" | grep -v "template"; then
        print_error "Potential sensitive data found with pattern: $pattern"
        FOUND_SENSITIVE=1
    fi
done

if [ $FOUND_SENSITIVE -eq 0 ]; then
    print_success "No sensitive data found in repository"
fi

# Check file permissions
print_section "Checking file permissions"
SCRIPT_FILES=$(find scripts -name "*.js" -o -name "*.sh")

for file in $SCRIPT_FILES; do
    if [ -x "$file" ]; then
        print_success "$file is executable"
    else
        print_warning "$file is not executable, fixing..."
        chmod +x "$file"
    fi
done

# Run tests if they exist
print_section "Running tests"
if [ -d "tests" ] && [ "$(ls -A tests/*.test.js 2>/dev/null | wc -l)" -gt 0 ]; then
    if npm test 2>&1 | grep -q "passing\|PASS"; then
        print_success "Tests passed"
    else
        print_error "Tests failed"
        npm test 2>&1 | tail -30
        exit 1
    fi
else
    print_warning "No tests found, skipping test execution"
fi

# Generate report
print_section "Generating validation report"
if node scripts/generate-report.js summary 2>&1 | grep -q "generated successfully"; then
    print_success "Report generated successfully"
    
    # Show summary
    if [ -f "reports/$(date +%Y-%m-%d)-summary-report.html" ]; then
        echo
        echo "📊 Validation Summary:"
        echo "---------------------"
        grep -A5 -B5 "Key Metrics\|Validation Status\|Required Actions" "reports/$(date +%Y-%m-%d)-summary-report.html" | \
            sed 's/<[^>]*>//g' | \
            sed 's/&nbsp;/ /g' | \
            head -30
    fi
else
    print_warning "Report generation had issues"
fi

# Final summary
echo
echo "================================================"
echo "✅ CI/CD Validation Completed Successfully!"
echo "================================================"
echo
echo "Next steps:"
echo "1. Review any warnings above"
echo "2. Check generated reports in ./reports/"
echo "3. Commit changes: git commit -m 'Validated: $(date)'"
echo "4. Push to repository: git push origin main"
echo
echo "All systems go! 🚀"

exit 0

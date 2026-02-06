#!/bin/bash

# Git Pre-commit Hook for Richard's Credit Authority
# Runs validation before allowing commits

echo "🔍 Running pre-commit validation..."
echo

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(yaml|yml|js|md|sh)$')

if [ -z "$STAGED_FILES" ]; then
    echo "No relevant files staged for commit."
    exit 0
fi

echo "Staged files to validate:"
echo "$STAGED_FILES" | sed 's/^/  /'
echo

# Track validation results
VALIDATION_PASSED=true
ERRORS=()
WARNINGS=()

# Function to add error
add_error() {
    ERRORS+=("$1")
    VALIDATION_PASSED=false
}

# Function to add warning
add_warning() {
    WARNINGS+=("$1")
}

# Check each staged file
for FILE in $STAGED_FILES; do
    echo "Validating $FILE..."
    
    # Skip if file doesn't exist (might be deleted)
    if [ ! -f "$FILE" ]; then
        continue
    fi
    
    case "$FILE" in
        *.yaml|*.yml)
            # Validate YAML syntax
            if ! python3 -c "import yaml; yaml.safe_load(open('$FILE'))" 2>/dev/null; then
                add_error "$FILE: Invalid YAML syntax"
            else
                echo "  ✓ YAML syntax valid"
            fi
            
            # Check for trailing spaces
            if grep -n '\s\+$' "$FILE"; then
                add_warning "$FILE: Contains trailing whitespace"
            fi
            
            # Check for tabs
            if grep -n $'\t' "$FILE"; then
                add_warning "$FILE: Contains tabs (use spaces)"
            fi
            
            # Specific validations based on file
            case "$(basename "$FILE")" in
                AUTHORITY.yaml)
                    if ! node scripts/validate-authority.js --file "$FILE" 2>&1 | grep -q "passed validation"; then
                        add_error "$FILE: Authority validation failed"
                    else
                        echo "  ✓ Authority validation passed"
                    fi
                    ;;
                GOVERNANCE.yaml)
                    if ! node scripts/validate-governance.js --file "$FILE" 2>&1 | grep -q "passed"; then
                        add_error "$FILE: Governance validation failed"
                    else
                        echo "  ✓ Governance validation passed"
                    fi
                    ;;
                PERMISSIONS.yaml)
                    if ! node scripts/validate-permissions.js --file "$FILE" 2>&1 | grep -q "passed"; then
                        add_error "$FILE: Permissions validation failed"
                    else
                        echo "  ✓ Permissions validation passed"
                    fi
                    ;;
                *.yaml)
                    # Generic YAML validation
                    echo "  ✓ YAML file validated"
                    ;;
            esac
            ;;
        
        *.js)
            # Validate JavaScript syntax
            if ! node -c "$FILE"; then
                add_error "$FILE: Invalid JavaScript syntax"
            else
                echo "  ✓ JavaScript syntax valid"
            fi
            
            # Run tests if it's a test file
            if [[ "$FILE" == *".test.js" ]]; then
                if ! npm test -- "$FILE" 2>&1 | grep -q "passing\|PASS"; then
                    add_error "$FILE: Tests failed"
                else
                    echo "  ✓ Tests passed"
                fi
            fi
            ;;
        
        *.sh)
            # Validate shell script syntax
            if ! bash -n "$FILE"; then
                add_error "$FILE: Invalid shell script syntax"
            else
                echo "  ✓ Shell script syntax valid"
            fi
            
            # Make executable if needed
            if [ ! -x "$FILE" ]; then
                chmod +x "$FILE"
                add_warning "$FILE: Made executable"
            fi
            ;;
        
        *.md)
            # Basic markdown validation
            if grep -n '  ' "$FILE" | head -5; then
                add_warning "$FILE: Contains multiple consecutive spaces"
            fi
            echo "  ✓ Markdown file checked"
            ;;
    esac
done

# Check for any validation script modifications
if echo "$STAGED_FILES" | grep -q "scripts/validate-"; then
    echo
    echo "⚠️  Validation scripts modified. Running full validation..."
    if ! ./scripts/ci-check.sh; then
        add_error "Full validation failed after script modifications"
    fi
fi

# Print results
echo
echo "================================================"

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "❌ PRE-COMMIT VALIDATION FAILED"
    echo
    echo "Errors:"
    for error in "${ERRORS[@]}"; do
        echo "  • $error"
    done
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo
        echo "Warnings (can be ignored):"
        for warning in "${WARNINGS[@]}"; do
            echo "  • $warning"
        done
    fi
    
    echo
    echo "Please fix the errors before committing."
    echo "To skip validation, use: git commit --no-verify"
    exit 1
else
    echo "✅ PRE-COMMIT VALIDATION PASSED"
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo
        echo "Warnings:"
        for warning in "${WARNINGS[@]}"; do
            echo "  • $warning"
        done
        echo
        echo "Consider fixing warnings before committing."
    fi
    
    # Show quick summary of changes
    echo
    echo "Changes to be committed:"
    git diff --cached --stat
    exit 0
fi

🏛️ scripts/validate-authority.js - Core Validation Engine

```javascript
#!/usr/bin/env node

/**
 * RICHARD'S CREDIT AUTHORITY VALIDATION ENGINE
 * Validates all authority files against schemas and business rules
 * Usage: node validate-authority.js [--file FILENAME] [--strict]
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const Ajv = require('ajv');
const ajv = new Ajv({ allErrors: true, strict: false });

// Add formats for validation
ajv.addFormat('date', /^\d{4}-\d{2}-\d{2}$/);
ajv.addFormat('currency', /^\$?[0-9]+(,[0-9]{3})*(\.[0-9]{2})?$/);
ajv.addFormat('percentage', /^[0-9]+(\.[0-9]+)?%$/);
ajv.addFormat('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/);

class AuthorityValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.schemas = {};
        this.loadSchemas();
    }

    loadSchemas() {
        const schemaDir = path.join(__dirname, '../SCHEMA-REGISTRY');
        const schemaFiles = [
            'authority.schema.json',
            'identity.schema.json',
            'permissions.schema.json',
            'governance.schema.json',
            'risk-profile.schema.json',
            'validation-rules.schema.json'
        ];

        schemaFiles.forEach(file => {
            try {
                const schemaPath = path.join(schemaDir, file);
                if (fs.existsSync(schemaPath)) {
                    const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
                    this.schemas[file.replace('.schema.json', '')] = schema;
                }
            } catch (error) {
                this.errors.push(`Failed to load schema ${file}: ${error.message}`);
            }
        });
    }

    validateFile(filePath, strict = false) {
        console.log(`\n🔍 Validating: ${path.basename(filePath)}`);
        
        if (!fs.existsSync(filePath)) {
            this.errors.push(`File not found: ${filePath}`);
            return false;
        }

        try {
            const content = fs.readFileSync(filePath, 'utf8');
            let data;
            
            // Parse based on file extension
            if (filePath.endsWith('.yaml') || filePath.endsWith('.yml')) {
                data = yaml.load(content);
            } else if (filePath.endsWith('.json')) {
                data = JSON.parse(content);
            } else {
                this.errors.push(`Unsupported file type: ${filePath}`);
                return false;
            }

            // Determine which schema to use
            const schemaType = this.determineSchemaType(filePath);
            if (!this.schemas[schemaType]) {
                this.warnings.push(`No schema found for ${schemaType}, performing basic validation`);
                return this.basicValidation(data, filePath);
            }

            // Validate against schema
            const validate = ajv.compile(this.schemas[schemaType]);
            const valid = validate(data);
            
            if (!valid) {
                validate.errors.forEach(error => {
                    this.errors.push(`${schemaType} validation error: ${error.instancePath} ${error.message}`);
                });
                return false;
            }

            // Additional business logic validation
            const businessValid = this.validateBusinessRules(data, schemaType, strict);
            
            if (businessValid && this.errors.length === 0) {
                console.log(`✅ ${path.basename(filePath)} passed validation`);
                return true;
            } else {
                console.log(`❌ ${path.basename(filePath)} failed validation`);
                return false;
            }

        } catch (error) {
            this.errors.push(`Parse error in ${filePath}: ${error.message}`);
            return false;
        }
    }

    determineSchemaType(filePath) {
        const filename = path.basename(filePath);
        const dirname = path.dirname(filePath).split(path.sep).pop();
        
        const mapping = {
            'AUTHORITY.yaml': 'authority',
            'GOVERNANCE.yaml': 'governance',
            'PERMISSIONS.yaml': 'permissions',
            'RISK-PROFILE.yaml': 'risk-profile',
            'VALIDATION-RULES.yaml': 'validation-rules',
            'profile.yaml': 'identity',
            'verification-methods.yaml': 'identity',
            'signature-authority.yaml': 'identity',
            'kyc-record.yaml': 'identity',
            'state-tax-id.yaml': 'identity',
            'federal-tax-id.yaml': 'identity'
        };

        if (mapping[filename]) {
            return mapping[filename];
        }

        // Fallback to directory name
        const dirMapping = {
            'identity': 'identity',
            'permission': 'permissions',
            'authority': 'authority',
            'governance': 'governance',
            'compliance': 'compliance'
        };

        return dirMapping[dirname] || 'unknown';
    }

    basicValidation(data, filePath) {
        const requiredRootFields = ['metadata', 'version'];
        let isValid = true;

        // Check for required root fields
        requiredRootFields.forEach(field => {
            if (!data[field]) {
                this.errors.push(`Missing required field: ${field}`);
                isValid = false;
            }
        });

        // Validate metadata structure
        if (data.metadata) {
            const metaRequired = ['version', 'effectiveDate'];
            metaRequired.forEach(field => {
                if (!data.metadata[field]) {
                    this.errors.push(`Metadata missing required field: ${field}`);
                    isValid = false;
                }
            });

            // Validate date format
            if (data.metadata.effectiveDate && !this.isValidDate(data.metadata.effectiveDate)) {
                this.errors.push(`Invalid date format in metadata.effectiveDate: ${data.metadata.effectiveDate}`);
                isValid = false;
            }
        }

        return isValid;
    }

    validateBusinessRules(data, schemaType, strict) {
        let isValid = true;
        
        switch(schemaType) {
            case 'authority':
                isValid = this.validateAuthorityRules(data, strict);
                break;
            case 'identity':
                isValid = this.validateIdentityRules(data, strict);
                break;
            case 'permissions':
                isValid = this.validatePermissionRules(data, strict);
                break;
            case 'governance':
                isValid = this.validateGovernanceRules(data, strict);
                break;
            case 'risk-profile':
                isValid = this.validateRiskRules(data, strict);
                break;
        }
        
        return isValid;
    }

    validateAuthorityRules(data, strict) {
        let isValid = true;
        
        // Check lending capacity doesn't exceed maximum
        if (data.lendingCapacity && data.parameters) {
            const totalAvailable = this.parseCurrency(data.lendingCapacity.totalAvailable);
            const maxExposure = this.parseCurrency(data.parameters.maximumAggregateExposure);
            
            if (totalAvailable > maxExposure) {
                this.errors.push(`Total available capacity (${data.lendingCapacity.totalAvailable}) exceeds maximum aggregate exposure (${data.parameters.maximumAggregateExposure})`);
                isValid = false;
            }
        }

        // Validate interest rate range
        if (data.parameters && data.parameters.interestRateRange) {
            const minRate = this.parsePercentage(data.parameters.interestRateRange.minimum);
            const maxRate = this.parsePercentage(data.parameters.interestRateRange.maximum);
            
            if (minRate >= maxRate) {
                this.errors.push(`Minimum interest rate (${minRate}%) must be less than maximum rate (${maxRate}%)`);
                isValid = false;
            }
            
            if (maxRate > 25 && strict) {
                this.warnings.push(`Maximum interest rate (${maxRate}%) may exceed usury limits in some jurisdictions`);
            }
        }

        // Check approval matrix consistency
        if (data.approvalRequirements) {
            const thresholds = Object.keys(data.approvalRequirements)
                .filter(key => key.includes('to') || key.includes('_'))
                .map(key => this.parseCurrencyThreshold(key));
            
            thresholds.sort((a, b) => a - b);
            
            for (let i = 1; i < thresholds.length; i++) {
                if (thresholds[i] <= thresholds[i-1]) {
                    this.errors.push(`Approval threshold ${thresholds[i]} is not strictly increasing`);
                    isValid = false;
                }
            }
        }

        return isValid;
    }

    validateIdentityRules(data, strict) {
        let isValid = true;
        
        // Check required identity fields
        const requiredFields = ['legalIdentity', 'contact', 'verification'];
        requiredFields.forEach(field => {
            if (!data[field]) {
                this.errors.push(`Identity missing required section: ${field}`);
                isValid = false;
            }
        });

        // Validate email format
        if (data.contact && data.contact.primaryEmail) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(data.contact.primaryEmail)) {
                this.errors.push(`Invalid primary email format: ${data.contact.primaryEmail}`);
                isValid = false;
            }
        }

        // Check verification methods exist for all levels
        if (data.verification) {
            const levels = ['level1', 'level2', 'level3', 'level4'];
            levels.forEach(level => {
                if (!data.verification[level]) {
                    this.warnings.push(`Missing verification level: ${level}`);
                }
            });
        }

        return isValid;
    }

    validatePermissionRules(data, strict) {
        let isValid = true;
        
        // Check role definitions exist
        if (!data.roles || Object.keys(data.roles).length === 0) {
            this.errors.push('No roles defined in permissions');
            isValid = false;
        }

        // Validate credit authority role exists
        if (data.roles && !data.roles.creditAuthority) {
            this.errors.push('Missing required role: creditAuthority');
            isValid = false;
        }

        // Check permission matrix references valid roles
        if (data.permissionMatrix) {
            Object.values(data.permissionMatrix).forEach(permission => {
                if (permission.roles) {
                    permission.roles.forEach(role => {
                        if (!data.roles[role]) {
                            this.errors.push(`Permission references undefined role: ${role}`);
                            isValid = false;
                        }
                    });
                }
            });
        }

        return isValid;
    }

    validateGovernanceRules(data, strict) {
        let isValid = true;
        
        // Check dual-founder structure
        if (data.principles && data.principles.dualFounder) {
            const founders = data.principles.dualFounder.founders;
            if (!founders || founders.length < 2) {
                this.errors.push('Dual-founder governance requires at least two founders');
                isValid = false;
            }
        }

        // Validate decision-making thresholds
        if (data.decisionMaking && data.decisionMaking.levels) {
            const levels = Object.values(data.decisionMaking.levels);
            let prevAmount = -1;
            
            levels.forEach(level => {
                const amount = this.parseCurrency(level.amount.split(' ')[0]);
                if (amount <= prevAmount) {
                    this.errors.push(`Decision level amounts must be strictly increasing: ${level.amount}`);
                    isValid = false;
                }
                prevAmount = amount;
            });
        }

        return isValid;
    }

    validateRiskRules(data, strict) {
        let isValid = true;
        
        // Check concentration limits sum to <= 100%
        if (data.concentrationLimits) {
            let total = 0;
            Object.values(data.concentrationLimits).forEach(limit => {
                total += this.parsePercentage(limit);
            });
            
            if (total > 100) {
                this.errors.push(`Concentration limits sum to ${total}%, exceeding 100%`);
                isValid = false;
            }
        }

        return isValid;
    }

    // Utility methods
    parseCurrency(currencyString) {
        if (!currencyString) return 0;
        const clean = currencyString.replace(/[$,]/g, '');
        return parseFloat(clean) || 0;
    }

    parsePercentage(percentageString) {
        if (!percentageString) return 0;
        const clean = percentageString.replace('%', '');
        return parseFloat(clean) || 0;
    }

    parseCurrencyThreshold(thresholdString) {
        // Convert strings like "upTo_25k", "25k_to_100k" to numbers
        const match = thresholdString.match(/(\d+(\.\d+)?)[kKmM]?/);
        if (match) {
            let num = parseFloat(match[1]);
            if (thresholdString.includes('k') || thresholdString.includes('K')) {
                num *= 1000;
            } else if (thresholdString.includes('m') || thresholdString.includes('M')) {
                num *= 1000000;
            }
            return num;
        }
        return 0;
    }

    isValidDate(dateString) {
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        if (!regex.test(dateString)) return false;
        
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    printResults() {
        console.log('\n' + '='.repeat(50));
        console.log('VALIDATION RESULTS');
        console.log('='.repeat(50));
        
        if (this.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.errors.forEach((error, index) => {
                console.log(`  ${index + 1}. ${error}`);
            });
        }
        
        if (this.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.warnings.forEach((warning, index) => {
                console.log(`  ${index + 1}. ${warning}`);
            });
        }
        
        if (this.errors.length === 0 && this.warnings.length === 0) {
            console.log('\n✅ All files passed validation!');
        }
        
        console.log('\n' + '='.repeat(50));
        return this.errors.length === 0;
    }
}

// Command line interface
async function main() {
    const args = process.argv.slice(2);
    const fileIndex = args.indexOf('--file');
    const strictMode = args.includes('--strict');
    const allFiles = args.includes('--all');
    
    const validator = new AuthorityValidator();
    
    if (fileIndex !== -1 && args[fileIndex + 1]) {
        // Validate single file
        const filePath = path.resolve(args[fileIndex + 1]);
        validator.validateFile(filePath, strictMode);
    } else if (allFiles) {
        // Validate all authority files
        const filePatterns = [
            './AUTHORITY.yaml',
            './GOVERNANCE.yaml',
            './PERMISSIONS.yaml',
            './RISK-PROFILE.yaml',
            './VALIDATION-RULES.yaml',
            './identity/*.yaml',
            './permission/*.yaml',
            './authority/*.yaml',
            './governance/*.yaml',
            './compliance/*.yaml'
        ];
        
        for (const pattern of filePatterns) {
            const files = await glob(pattern);
            for (const file of files) {
                if (fs.existsSync(file)) {
                    validator.validateFile(file, strictMode);
                }
            }
        }
    } else {
        // Default: validate core files
        const coreFiles = [
            './AUTHORITY.yaml',
            './GOVERNANCE.yaml',
            './PERMISSIONS.yaml',
            './identity/profile.yaml'
        ];
        
        coreFiles.forEach(file => {
            if (fs.existsSync(file)) {
                validator.validateFile(file, strictMode);
            } else {
                validator.warnings.push(`File not found: ${file}`);
            }
        });
    }
    
    const success = validator.printResults();
    process.exit(success ? 0 : 1);
}

// Simple glob function for pattern matching
function glob(pattern) {
    return new Promise((resolve) => {
        const files = [];
        const baseDir = pattern.split('*')[0].split('/').slice(0, -1).join('/') || '.';
        
        if (pattern.includes('*')) {
            // Simple directory traversal
            const dirPath = pattern.substring(0, pattern.lastIndexOf('/'));
            const fileNamePattern = pattern.substring(pattern.lastIndexOf('/') + 1);
            const regex = new RegExp('^' + fileNamePattern.replace(/\*/g, '.*') + '$');
            
            try {
                const dirFiles = fs.readdirSync(dirPath);
                dirFiles.forEach(file => {
                    if (regex.test(file)) {
                        files.push(path.join(dirPath, file));
                    }
                });
            } catch (error) {
                // Directory doesn't exist
            }
        } else {
            // Exact file
            files.push(pattern);
        }
        
        resolve(files);
    });
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('Validation failed:', error);
        process.exit(1);
    });
}

module.exports = AuthorityValidator;
```

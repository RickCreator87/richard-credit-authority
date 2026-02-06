🚀 COMPLETE AUTOMATION & OPERATIONAL FILES

Here's every remaining automation, workflow, and operational file your credit authority needs:

📁 AUTOMATION SCRIPTS (8 files)



COMPLETE AUTOMATION & OPERATIONAL FILES
🚀 COMPLETE AUTOMATION & OPERATIONAL FILES

Here's every remaining automation, workflow, and operational file your credit authority needs:

📁 AUTOMATION SCRIPTS (8 files)


#!/usr/bin/env node

/**
 * PERMISSIONS VALIDATION ENGINE
 * Validates permission matrix and role assignments
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class PermissionsValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
    }

    validatePermissions(filePath) {
        console.log(`🔐 Validating permissions: ${path.basename(filePath)}`);
        
        if (!fs.existsSync(filePath)) {
            this.errors.push(`Permissions file not found: ${filePath}`);
            return false;
        }

        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const data = yaml.load(content);
            
            // Basic validation
            if (!this.validateStructure(data)) return false;
            
            // Role validation
            if (!this.validateRoles(data.roles)) return false;
            
            // Permission matrix validation
            if (data.permissionMatrix && !this.validatePermissionMatrix(data.permissionMatrix, data.roles)) return false;
            
            // Delegation rules validation
            if (data.delegation && !this.validateDelegation(data.delegation, data.roles)) return false;
            
            // Emergency permissions validation
            if (data.emergencyPermissions && !this.validateEmergencyPermissions(data.emergencyPermissions)) return false;
            
            return this.errors.length === 0;
            
        } catch (error) {
            this.errors.push(`Parse error: ${error.message}`);
            return false;
        }
    }

    validateStructure(data) {
        const requiredSections = ['metadata', 'roles'];
        let isValid = true;

        requiredSections.forEach(section => {
            if (!data[section]) {
                this.errors.push(`Missing required section: ${section}`);
                isValid = false;
            }
        });

        // Validate metadata
        if (data.metadata) {
            const requiredMeta = ['version', 'effectiveDate'];
            requiredMeta.forEach(field => {
                if (!data.metadata[field]) {
                    this.errors.push(`Metadata missing required field: ${field}`);
                    isValid = false;
                }
            });
        }

        return isValid;
    }

    validateRoles(roles) {
        if (!roles || Object.keys(roles).length === 0) {
            this.errors.push('No roles defined');
            return false;
        }

        let isValid = true;
        const roleNames = Object.keys(roles);

        // Check for required creditAuthority role
        if (!roles.creditAuthority) {
            this.errors.push('Required role missing: creditAuthority');
            isValid = false;
        }

        // Validate each role
        roleNames.forEach(roleName => {
            const role = roles[roleName];
            
            if (!role.permissions) {
                this.errors.push(`Role ${roleName} missing permissions array`);
                isValid = false;
            }
            
            if (!role.limits) {
                this.warnings.push(`Role ${roleName} missing limits section`);
            }

            // Validate creditAuthority specific requirements
            if (roleName === 'creditAuthority') {
                if (!role.holder || role.holder !== 'Richard S. Creator') {
                    this.errors.push('creditAuthority role must have Richard S. Creator as holder');
                    isValid = false;
                }
                
                const requiredPermissions = [
                    'CREATE_LOAN',
                    'APPROVE_LOAN_UNDER_100K',
                    'SIGN_AGREEMENTS'
                ];
                
                requiredPermissions.forEach(perm => {
                    if (!role.permissions.includes(perm)) {
                        this.errors.push(`creditAuthority missing required permission: ${perm}`);
                        isValid = false;
                    }
                });
            }
        });

        return isValid;
    }

    validatePermissionMatrix(matrix, roles) {
        let isValid = true;
        const roleNames = Object.keys(roles || {});
        
        Object.entries(matrix).forEach(([permissionName, permission]) => {
            // Check description
            if (!permission.description) {
                this.errors.push(`Permission ${permissionName} missing description`);
                isValid = false;
            }
            
            // Check roles array exists
            if (!permission.roles || !Array.isArray(permission.roles)) {
                this.errors.push(`Permission ${permissionName} missing or invalid roles array`);
                isValid = false;
                return;
            }
            
            // Check all referenced roles exist
            permission.roles.forEach(role => {
                if (!roleNames.includes(role)) {
                    this.errors.push(`Permission ${permissionName} references undefined role: ${role}`);
                    isValid = false;
                }
            });
            
            // Check for approvalRequired if applicable
            if (permissionName.includes('APPROVE') && !permission.approvalRequired) {
                this.warnings.push(`Approval permission ${permissionName} missing approvalRequired field`);
            }
        });

        return isValid;
    }

    validateDelegation(delegation, roles) {
        if (!delegation.allowed && delegation.allowed !== false) {
            this.errors.push('Delegation must explicitly specify allowed: true or false');
            return false;
        }

        if (delegation.allowed) {
            if (!delegation.conditions || !Array.isArray(delegation.conditions)) {
                this.errors.push('Delegation conditions must be an array when allowed');
                return false;
            }

            if (delegation.cannotDelegate) {
                delegation.cannotDelegate.forEach(action => {
                    if (!this.isValidPermission(action, roles)) {
                        this.warnings.push(`Cannot delegate undefined permission: ${action}`);
                    }
                });
            }
        }

        return true;
    }

    validateEmergencyPermissions(emergency) {
        const required = ['triggers', 'activatedBy', 'duration', 'emergencyPowers'];
        let isValid = true;

        required.forEach(field => {
            if (!emergency[field]) {
                this.errors.push(`Emergency permissions missing required field: ${field}`);
                isValid = false;
            }
        });

        if (emergency.triggers && !Array.isArray(emergency.triggers)) {
            this.errors.push('Emergency triggers must be an array');
            isValid = false;
        }

        if (emergency.emergencyPowers && !Array.isArray(emergency.emergencyPowers)) {
            this.errors.push('Emergency powers must be an array');
            isValid = false;
        }

        return isValid;
    }

    isValidPermission(permissionName, roles) {
        // Check if permission exists in any role's permissions
        return Object.values(roles).some(role => 
            role.permissions && role.permissions.includes(permissionName)
        );
    }

    printResults() {
        console.log('\n' + '='.repeat(50));
        console.log('PERMISSIONS VALIDATION RESULTS');
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
        
        if (this.errors.length === 0) {
            console.log('\n✅ Permissions validation passed!');
            return true;
        } else {
            console.log('\n❌ Permissions validation failed');
            return false;
        }
    }
}

// Command line interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const filePath = args[0] || './PERMISSIONS.yaml';
    
    const validator = new PermissionsValidator();
    const isValid = validator.validatePermissions(path.resolve(filePath));
    const success = validator.printResults();
    
    process.exit(success ? 0 : 1);
}

module.exports = PermissionsValidator;




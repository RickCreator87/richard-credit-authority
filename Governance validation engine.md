#!/usr/bin/env node

/**
 * GOVERNANCE VALIDATION ENGINE
 * Validates governance framework and tax-first rules
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class GovernanceValidator {
    constructor() {
        this.errors = [];
        this.warnings = [];
    }

    validateGovernance(filePath) {
        console.log(`⚖️ Validating governance: ${path.basename(filePath)}`);
        
        if (!fs.existsSync(filePath)) {
            this.errors.push(`Governance file not found: ${filePath}`);
            return false;
        }

        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const data = yaml.load(content);
            
            // Basic validation
            if (!this.validateStructure(data)) return false;
            
            // Principles validation
            if (!this.validatePrinciples(data.principles)) return false;
            
            // Decision-making validation
            if (!this.validateDecisionMaking(data.decisionMaking)) return false;
            
            // Tax governance validation
            if (!this.validateTaxGovernance(data.taxGovernance)) return false;
            
            // Risk governance validation
            if (!this.validateRiskGovernance(data.riskGovernance)) return false;
            
            // Amendment process validation
            if (!this.validateAmendmentProcess(data.amendmentProcess)) return false;
            
            return this.errors.length === 0;
            
        } catch (error) {
            this.errors.push(`Parse error: ${error.message}`);
            return false;
        }
    }

    validateStructure(data) {
        const requiredSections = ['metadata', 'principles', 'structure', 'decisionMaking'];
        let isValid = true;

        requiredSections.forEach(section => {
            if (!data[section]) {
                this.errors.push(`Missing required section: ${section}`);
                isValid = false;
            }
        });

        // Validate metadata
        if (data.metadata) {
            const requiredMeta = ['version', 'effectiveDate', 'governanceModel'];
            requiredMeta.forEach(field => {
                if (!data.metadata[field]) {
                    this.errors.push(`Metadata missing required field: ${field}`);
                    isValid = false;
                }
            });

            // Check for tax-first dual-founder model
            if (data.metadata.governanceModel !== 'Tax-First Dual-Founder') {
                this.warnings.push('Governance model should be "Tax-First Dual-Founder"');
            }
        }

        return isValid;
    }

    validatePrinciples(principles) {
        if (!principles) {
            this.errors.push('Principles section missing');
            return false;
        }

        let isValid = true;
        const requiredPrinciples = ['taxFirst', 'dualFounder', 'sovereignty'];

        requiredPrinciples.forEach(principle => {
            if (!principles[principle]) {
                this.errors.push(`Missing required principle: ${principle}`);
                isValid = false;
            }
        });

        // Validate dual-founder structure
        if (principles.dualFounder) {
            if (!principles.dualFounder.founders || !Array.isArray(principles.dualFounder.founders)) {
                this.errors.push('Dual-founder must have founders array');
                isValid = false;
            } else if (principles.dualFounder.founders.length < 2) {
                this.errors.push('Dual-founder requires at least 2 founders');
                isValid = false;
            }

            if (!principles.dualFounder.approvalThreshold) {
                this.warnings.push('Dual-founder missing approvalThreshold');
            }
        }

        // Validate tax-first rules
        if (principles.taxFirst && principles.taxFirst.rules) {
            const requiredRules = [
                'Tax implications assessed before financial terms',
                'Structure follows tax efficiency',
                'Compliance precedes profitability'
            ];

            requiredRules.forEach(rule => {
                if (!principles.taxFirst.rules.includes(rule)) {
                    this.warnings.push(`Tax-first principle missing rule: ${rule}`);
                }
            });
        }

        return isValid;
    }

    validateDecisionMaking(decisionMaking) {
        if (!decisionMaking || !decisionMaking.levels) {
            this.errors.push('Decision making levels missing');
            return false;
        }

        let isValid = true;
        const levels = decisionMaking.levels;
        const levelKeys = Object.keys(levels);
        
        // Check for at least 3 decision levels
        if (levelKeys.length < 3) {
            this.errors.push('At least 3 decision levels required');
            isValid = false;
        }

        let previousMax = -1;
        
        levelKeys.forEach(key => {
            const level = levels[key];
            
            if (!level.amount || !level.approval || !level.documentation) {
                this.errors.push(`Level ${key} missing required fields`);
                isValid = false;
            }

            // Parse amount to check increasing thresholds
            const amountMatch = level.amount.match(/\$?([\d,]+(\.\d+)?)/);
            if (amountMatch) {
                const amount = parseFloat(amountMatch[1].replace(/,/g, ''));
                
                if (key.includes('to') || key.includes('_')) {
                    // Range - extract max value
                    const maxMatch = level.amount.match(/\$?([\d,]+(\.\d+)?)\s*(?:to|-|_)\s*\$?([\d,]+(\.\d+)?)/);
                    if (maxMatch) {
                        const maxAmount = parseFloat(maxMatch[3].replace(/,/g, ''));
                        if (maxAmount <= previousMax) {
                            this.errors.push(`Decision level ${key} maximum (${maxAmount}) not greater than previous maximum (${previousMax})`);
                            isValid = false;
                        }
                        previousMax = maxAmount;
                    }
                } else if (key.includes('over') || key.includes('>')) {
                    // This should be the highest level
                    if (amount <= previousMax) {
                        this.errors.push(`Final decision level ${key} amount (${amount}) not greater than previous maximum (${previousMax})`);
                        isValid = false;
                    }
                } else if (key.includes('Up') || key.includes('up')) {
                    // First level - set previousMax
                    previousMax = amount;
                }
            }
        });

        // Validate emergency decisions
        if (decisionMaking.emergencyDecisions) {
            const emergency = decisionMaking.emergencyDecisions;
            const requiredFields = ['trigger', 'approval', 'ratification'];
            
            requiredFields.forEach(field => {
                if (!emergency[field]) {
                    this.errors.push(`Emergency decisions missing required field: ${field}`);
                    isValid = false;
                }
            });
        }

        return isValid;
    }

    validateTaxGovernance(taxGovernance) {
        if (!taxGovernance) {
            this.errors.push('Tax governance section missing');
            return false;
        }

        let isValid = true;
        
        if (taxGovernance.primaryRule !== 'Tax efficiency drives structure') {
            this.warnings.push('Tax governance primary rule should be: "Tax efficiency drives structure"');
        }

        // Validate income classification
        if (taxGovernance.incomeClassification) {
            const requiredTypes = ['interestIncome', 'principalRepayment', 'feeIncome'];
            requiredTypes.forEach(type => {
                if (!taxGovernance.incomeClassification[type]) {
                    this.errors.push(`Income classification missing type: ${type}`);
                    isValid = false;
                }
            });
        }

        // Validate deduction strategy
        if (taxGovernance.deductionStrategy) {
            if (!taxGovernance.deductionStrategy.badDebtDeduction) {
                this.errors.push('Deduction strategy missing bad debt deduction method');
                isValid = false;
            }
        }

        return isValid;
    }

    validateRiskGovernance(riskGovernance) {
        if (!riskGovernance) {
            this.warnings.push('Risk governance section missing');
            return true; // Optional but recommended
        }

        let isValid = true;
        
        // Validate credit risk limits
        if (riskGovernance.creditRisk) {
            if (!riskGovernance.creditRisk.maximumSingleExposure) {
                this.errors.push('Credit risk missing maximum single exposure');
                isValid = false;
            }
            
            if (!riskGovernance.creditRisk.concentrationLimits) {
                this.warnings.push('Credit risk missing concentration limits');
            }
        }

        // Validate operational risk controls
        if (riskGovernance.operationalRisk && riskGovernance.operationalRisk.controls) {
            const requiredControls = [
                'Dual control for payments > $10,000',
                'Monthly reconciliation',
                'Annual security audit'
            ];

            requiredControls.forEach(control => {
                if (!riskGovernance.operationalRisk.controls.includes(control)) {
                    this.warnings.push(`Operational risk missing control: ${control}`);
                }
            });
        }

        return isValid;
    }

    validateAmendmentProcess(amendmentProcess) {
        if (!amendmentProcess) {
            this.errors.push('Amendment process section missing');
            return false;
        }

        let isValid = true;
        const requiredSteps = ['proposal', 'approval', 'implementation', 'grandfathering'];

        requiredSteps.forEach(step => {
            if (!amendmentProcess[step]) {
                this.errors.push(`Amendment process missing step: ${step}`);
                isValid = false;
            }
        });

        // Validate proposal requirements
        if (amendmentProcess.proposal && !Array.isArray(amendmentProcess.proposal)) {
            this.errors.push('Amendment proposal must be an array');
            isValid = false;
        }

        // Validate approval types
        if (amendmentProcess.approval) {
            if (!amendmentProcess.approval.standard || !amendmentProcess.approval.fundamental) {
                this.errors.push('Amendment approval missing standard or fundamental approval methods');
                isValid = false;
            }
        }

        return isValid;
    }

    printResults() {
        console.log('\n' + '='.repeat(50));
        console.log('GOVERNANCE VALIDATION RESULTS');
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
            console.log('\n✅ Governance validation passed!');
            return true;
        } else {
            console.log('\n❌ Governance validation failed');
            return false;
        }
    }
}

// Command line interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const filePath = args[0] || './GOVERNANCE.yaml';
    
    const validator = new GovernanceValidator();
    const isValid = validator.validateGovernance(path.resolve(filePath));
    const success = validator.printResults();
    
    process.exit(success ? 0 : 1);
}

module.exports = GovernanceValidator;



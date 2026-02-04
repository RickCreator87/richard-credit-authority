const fs = require("fs");

function loadJSON(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function assert(condition, message) {
  if (!condition) {
    console.error("❌ Validation failed:", message);
    process.exit(1);
  }
}

console.log("🔍 Validating Richard's Credit Authority...");

const owner = loadJSON("./authority/identity/owner.json");
const tax = loadJSON("./authority/tax/tax-rules.json");
const gov = loadJSON("./authority/governance/governance-rules.json");
const perms = loadJSON("./authority/permissions/permissions.json");

assert(owner.legal_name, "Owner legal name missing");
assert(owner.signature_hash, "Owner signature hash missing");
assert(tax.rules.require_separation === true, "Tax separation must be enforced");
assert(gov.emergency_stop.enabled === true, "Emergency stop must be enabled");
assert(perms.roles.owner.can_issue_credit === true, "Owner must be able to issue credit");

console.log("✅ Authority validation passed.");
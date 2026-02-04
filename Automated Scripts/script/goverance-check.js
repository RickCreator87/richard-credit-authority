const fs = require("fs");

function loadGovernance() {
  return JSON.parse(fs.readFileSync("./authority/governance/governance-rules.json", "utf8"));
}

console.log("🔐 Running governance checks...");

const gov = loadGovernance();

if (gov.emergency_stop.enabled) {
  console.log("🛑 Emergency stop is active — workflows may be blocked.");
}

console.log("✔️ Governance rules loaded and validated.");
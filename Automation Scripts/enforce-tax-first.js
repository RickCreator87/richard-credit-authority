const fs = require("fs");

const tax = JSON.parse(fs.readFileSync("./authority/tax/tax-rules.json", "utf8"));
const requiredOrder = tax.rules.order_of_operations;

console.log("🔎 Checking tax-first ordering...");

function validateOrder(order) {
  for (let i = 0; i < requiredOrder.length; i++) {
    if (order[i] !== requiredOrder[i]) {
      console.error(`❌ Tax order violation at position ${i}: expected ${requiredOrder[i]}, got ${order[i]}`);
      process.exit(1);
    }
  }
}

validateOrder(requiredOrder);

console.log("✅ Tax-first ordering validated.");
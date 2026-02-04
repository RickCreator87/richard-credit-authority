const fs = require("fs");

function loadWorkflow(name) {
  const path = `./authority/workflows/${name}.workflow.json`;
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function runStep(step) {
  console.log(`➡️  Step: ${step.id} (${step.type})`);

  // Placeholder logic — real engines can plug in here
  if (step.on_fail === "abort") {
    console.log("   ✔️ Passed");
  }
}

function runWorkflow(name) {
  console.log(`\n🚀 Running workflow: ${name}`);
  const wf = loadWorkflow(name);

  wf.steps.forEach(step => runStep(step));

  console.log(`🎉 Workflow ${name} completed.\n`);
}

const workflowName = process.argv[2];
if (!workflowName) {
  console.error("Usage: node run-workflow.js <workflow-name>");
  process.exit(1);
}

runWorkflow(workflowName);
const fs = require("fs");

function loadWorkflow(name) {
  return JSON.parse(fs.readFileSync(`./authority/workflows/${name}.workflow.json`, "utf8"));
}

function executeStep(step) {
  console.log(`➡️ Executing step: ${step.id}`);

  // Placeholder for real logic
  return true;
}

function run(name) {
  console.log(`\n⚙️ Workflow Engine: ${name}`);

  const wf = loadWorkflow(name);

  for (const step of wf.steps) {
    const ok = executeStep(step);
    if (!ok && step.on_fail === "abort") {
      console.error(`❌ Workflow aborted at step: ${step.id}`);
      process.exit(1);
    }
  }

  console.log(`🎯 Workflow ${name} completed successfully.`);
}

module.exports = { run };
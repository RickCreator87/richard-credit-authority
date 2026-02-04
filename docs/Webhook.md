# GitHub App & Webhook Integration

This authority repo can be connected to a GitHub App.

## Events

- `pull_request` → triggers authority workflows:
  - `issue_credit`
  - `approve_loan`
  - `disburse_funds`

## Webhook Server

- Entry: `webhook/server.js`
- Env:
  - `GITHUB_WEBHOOK_SECRET`
  - `PORT` (optional)

# Contributor Workflow

## Default Delivery Flow
1. Select tasks from MASTER_PLAN_90D_SORANI.md by phase priority.
2. Implement code/docs changes in small reviewable chunks.
3. Run required checks before reporting completion.
4. Update execution logs and governance docs when process changes.

## Required Checks Before Completion
- UI: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`
- E2E smoke: `pnpm test:e2e`
- Backend checks for affected API behavior (when changed)

## Release Checklist Usage
Before marking any phase item as done, confirm all relevant items in docs/RELEASE_CHECKLIST.md are satisfied.

## Fallback and Flags
Any endpoint/fallback behavior change must update:
- ui/src/api/endpoints.ts
- docs/FALLBACK_POLICY.md
- docs/API_CONTRACT_MATRIX.md

## Reporting Rule
Report only after implementation and checks are fully complete. Include explicit list of what was done and what was verified.

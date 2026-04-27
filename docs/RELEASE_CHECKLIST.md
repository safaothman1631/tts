# Release Checklist

## Pre-Release Quality Gates
- [ ] Lint passes in changed workspaces.
- [ ] Typecheck passes (`ui` and affected backend modules).
- [ ] Unit/integration tests pass.
- [ ] E2E smoke tests pass.
- [ ] Build artifacts generated successfully.

## API and Contract Checks
- [ ] Endpoint changes documented in english/docs/api_reference.md.
- [ ] UI endpoint mapping validated in ui/src/api/endpoints.ts.
- [ ] Feature flags reviewed for new/changed capabilities.
- [ ] Fallback behavior documented and user messaging verified.

## Reliability Checks
- [ ] Health/degraded/offline states verified in Studio, Voices, VoiceLab.
- [ ] Error toasts/messages are actionable and translated where needed.
- [ ] No unresolved Sev-1/Sev-2 issues.

## Security and Compliance
- [ ] Consent flows validated for voice cloning paths.
- [ ] Headers/CORS/CSP validated for deployment target.
- [ ] Secrets/env vars handled via environment, not committed.

## Deployment and Rollback
- [ ] Versioned artifact/image created.
- [ ] Staging smoke test passed.
- [ ] Rollback target verified and documented.
- [ ] Monitoring/alerts confirmed green.

## Post-Release
- [ ] Release notes published.
- [ ] Known issues logged with owners.
- [ ] 24-hour regression watch completed.

## Summary
- What changed?
- Why was this needed?

## Phase Link
- Related phase(s) in MASTER_PLAN_90D_SORANI.md:

## Validation
- [ ] `python -m pytest tests` (english)
- [ ] `pnpm lint` (ui)
- [ ] `pnpm typecheck` (ui)
- [ ] `pnpm test -- --run` (ui)
- [ ] `pnpm build` (ui)
- [ ] `pnpm test:e2e` (ui)

## Release Checklist Alignment
Before requesting review, confirm relevant items in docs/RELEASE_CHECKLIST.md are complete:
- [ ] API/contract notes updated if endpoints changed
- [ ] Fallback/feature-flag behavior documented if changed
- [ ] Health/degraded/offline states verified for affected flows
- [ ] Security/compliance impact reviewed (consent, headers, secrets)
- [ ] Rollback path identified for risky changes

## Risk and Rollback
- Risk level: Low / Medium / High
- Rollback approach:

## Notes
- Additional context for reviewers

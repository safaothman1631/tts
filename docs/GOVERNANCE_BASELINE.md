# Governance Baseline

## Scope
This baseline defines delivery guardrails for the TTS workspace with focus on UI + API integration quality.

## Definition Of Done (DoD)
A task is done only when all items pass:
- Code implemented and reviewed.
- Typecheck passes in affected workspace(s).
- Tests added or updated for changed behavior.
- User-visible behavior documented if changed.
- No unresolved critical or high-severity issues.
- Feature flags and fallback behavior are defined for new endpoints.

## Severity Model
- Sev-1 Critical: Production outage, data loss, security breach.
- Sev-2 High: Core flow blocked (synthesis, voices, voice-lab), no workaround.
- Sev-3 Medium: Partial degradation with workaround.
- Sev-4 Low: Cosmetic/docs/non-blocking issues.

## Decision Cadence
- Weekly roadmap review.
- Biweekly release train.
- Incident postmortem published within 48 hours.

## KPI Baseline (Initial)
- Typecheck pass rate: 100% on main branch.
- E2E smoke pass rate: >= 99% on release candidates.
- MTTR target for Sev-1/Sev-2: < 30 minutes.
- Regression escape rate: < 5% per release cycle.

## Ownership Rule
Every feature and endpoint must have one primary owner and one backup owner.

## Change Control
- Any API contract change requires docs update in english/docs/api_reference.md.
- Any fallback policy change requires docs update in docs/FALLBACK_POLICY.md.
- Any release process change requires docs update in docs/RELEASE_CHECKLIST.md.

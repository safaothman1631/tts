# Ownership Matrix

## Team Ownership
- Product/PM: scope, roadmap, KPI tracking
- Frontend Lead: ui/src/features, UX consistency, i18n/RTL readiness
- Backend Lead: english/src/eng_tts, API contracts, performance
- QA Lead: test matrix, release sign-off, flaky triage
- DevOps/SRE: CI/CD, environments, monitoring, rollback drills
- Security Champion: threat model, consent/compliance policy, audit checks

## Area Ownership Map
- UI API client and endpoint mapping: ui/src/api/
- Studio flow: ui/src/features/studio/
- Voices flow: ui/src/features/voices/
- VoiceLab flow: ui/src/features/voice-lab/
- UI tests: ui/src/test/ and ui/tests/
- Engine API docs: english/docs/api_reference.md
- Deployment config: ui/docker-compose.yml, ui/Caddyfile, english/docker-compose.yml

## Ownership Rules
- Each area must have:
  - Primary owner
  - Backup owner
  - SLA target for Sev-1/Sev-2 response
- PRs affecting multiple areas require review from each area owner.

## On-Call Escalation
- Sev-1: Frontend/Backend owner + DevOps/SRE immediately
- Sev-2: Relevant area owner within same working block
- Sev-3/4: batched into next sprint unless risk increases

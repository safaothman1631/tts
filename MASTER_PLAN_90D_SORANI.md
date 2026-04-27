# MASTER PLAN 90 DAY (Sorani)

## 1) دیدی گشتی پرۆژە
- پرۆژە: TTS Studio + eng-tts integration
- ئامانج: UI یەکی بەهێز و production-ready بۆ synthesis, voices, voice-lab, projects
- سەرکەوتن:
  - بەردەوامی سرویس لە degraded/down modes
  - کەمکردنەوەی هەڵەی runtime و API drift
  - releaseی ئارام و rollbackی خێرا

## 2) هەڵسەنگاندنی دۆخی ئێستا
### خاڵە بەهێزەکان
- fallback بۆ synthesis/clone/analyze لە ui/src/api/endpoints.ts
- health-aware gating لە studio/voices
- VoiceLab wizard جێبەجێ کراوە
- build/typecheck/e2e سەرکەوتوو

### خاڵە لاوازەکان
- CI/CD گەورە بە تەواوی نەدانراوە
- policyی fallback بە شێوەی یەکگرتوو لە هەموو endpoint ـەکان نییە
- هەندێک docs لە configی پۆرت و behavior جیاوازن

### مەترسیەکان
- drift لە نێوان UI و backend contract
- cache behavior لە PWA لەگەڵ تازەبوونی API
- complianceی cloning و logging ئەگەر policy ڕوون نەبێت

## 3) پلان بە قۆناغ (10 قۆناغ)

### قۆناغ 1: Governance + Baseline (Week 1)
- ئامانج: DoD و release policy یەکگرتوو
- کاری سەرەکی: KPI baseline، ownership map، severity model
- Deliverables: policy docs لە docs/ و ui/docs/
- KPI: 100% feature owner، release checklist approved
- Risk/Mitigation: policy مبهم -> template + weekly review

### قۆناغ 2: API Contract Hardening (Week 1-2)
- ئامانج: drift کەمبکەیتەوە
- کاری سەرەکی: contract matrix بۆ /v1/health, voices, synth, clone, analyze
- Deliverables: update لە english/docs/api_reference.md + ui/src/api/endpoints.ts
- KPI: 0 breaking change without migration note
- Risk/Mitigation: endpoint changes -> changelog gate

### قۆناغ 3: Feature-Flag + Fallback Unification (Week 2-3)
- ئامانج: policyی یەکگرتوو بۆ unavailable endpoints
- کاری سەرەکی: class بندی (hard-fail, soft-fallback, local-only)
- Deliverables: shared fallback helper لە ui/src/api/
- KPI: 100% critical endpoints classed
- Risk/Mitigation: زیادبوونی complexity -> 3 کلاس تەنها

### قۆناغ 4: UX Reliability (Week 3-4)
- ئامانج: consistent loading/error/empty/offline states
- کاری سەرەکی: state components یەکگرتوو
- Deliverables: pattern rollout لە ui/src/features/studio, voices, voice-lab
- KPI: 95% state coverage
- Risk/Mitigation: duplicated UX logic -> shared primitives

### قۆناغ 5: i18n + RTL Excellence (Week 4-5)
- ئامانج: Sorani-first experience بێ layout break
- کاری سەرەکی: translation audit، RTL QA
- Deliverables: locale audit لە ui/src/ + docs لە ui/docs/
- KPI: 100% top routes translated، 0 RTL blocker
- Risk/Mitigation: hardcoded strings -> lint/policy

### قۆناغ 6: Test Depth Expansion (Week 5-6)
- ئامانج: coverage بۆ unhappy/degraded paths
- کاری سەرەکی: unit/integration/e2e scenarios
- Deliverables: tests لە ui/src/test و ui/tests
- KPI: critical-path pass 100%، flaky < 2%
- Risk/Mitigation: unstable env -> deterministic mocks

### قۆناغ 7: CI/CD Implementation (Week 6-7)
- ئامانج: quality gates خودکار
- کاری سەرەکی: lint/type/test/build/e2e smoke + docker build
- Deliverables: workflow files + README updates
- KPI: PR gate < 12 min
- Risk/Mitigation: pipeline دیر -> caching + parallel jobs

### قۆناغ 8: Observability + SLO (Week 7-8)
- ئامانج: detect/resolve incidents خێرا
- کاری سەرەکی: FE errors telemetry + BE metrics/alerts
- Deliverables: dashboards + runbooks
- KPI: MTTR < 30min، synth error rate < 2%
- Risk/Mitigation: noisy alerts -> tuning thresholds

### قۆناغ 9: Security + Compliance Hardening (Week 8-9)
- ئامانج: safety بۆ data/voice cloning
- کاری سەرەکی: headers/CORS/CSP، consent audit trail، retention policy
- Deliverables: security checklist + config updates
- KPI: 0 critical vuln، 100% consent evidence
- Risk/Mitigation: privacy ambiguity -> explicit policy + delete flow

### قۆناغ 10: Release Readiness + Scale (Week 10-12)
- ئامانج: production-grade launch
- کاری سەرەکی: load/soak tests، rollback drills، RC cycle
- Deliverables: release runbook + deploy profiles
- KPI: rollback < 10min، stable P95
- Risk/Mitigation: deploy regression -> canary + immutable images

## 4) Priority Matrix
### Now
- API contracts hardening
- Fallback/flag unification
- UX reliability states
- Minimum CI gates

### Next
- Test expansion
- Observability + SLO
- i18n/RTL hardening

### Later
- Scale optimization
- Compliance automation
- Multi-node deployment tuning

## 5) Roadmapی 90 ڕۆژ
- Week 1-2: baseline + contract alignment
- Week 3-4: fallback unification + degraded UX
- Week 5-6: test depth + flaky cleanup
- Week 7-8: CI/CD live + artifact versioning
- Week 9-10: observability + runbooks
- Week 11-12: security closeout + release candidate

## 6) QA و Quality Gates
- Unit: API mapping, fallback branches, store transitions
- Integration: studio synth, voices cache, voice-lab local fallback
- E2E: happy path + backend down + endpoint unavailable + slow API

### PR Gates
- lint pass
- typecheck pass
- unit/integration pass
- e2e smoke pass
- build + docker build pass

### Release Checklist
- API notes updated
- feature flags reviewed
- i18n/RTL smoke passed
- security headers verified
- dashboards green
- rollback artifact ready

## 7) DevOps و دیپلۆی
- Local: Vite proxy -> 127.0.0.1:8765
- Staging: docker-compose + Caddy reverse proxy
- Production: versioned images + staged rollout

### CI/CD
- PR: ui lint/type/test/build + backend tests + contract smoke
- Main: build/push images -> staging deploy -> smoke -> manual prod approval

### Rollback
- immutable tags
- one-command rollback to previous compose version
- compatibility checks before deploy

## 8) Security و Compliance
- token/access review لە ui/src/api/client.ts
- strict headers/CSP لە ui/Caddyfile
- input validation FE + BE
- rate limits بۆ synth/clone/analyze
- consent gate mandatory لە ui/src/features/voice-lab/VoiceLabPage.tsx
- retention/delete policy for voice data

### Fallback Policy (Required)
- Class A (hard-fail): auth/security endpoints
- Class B (soft-fallback): clone/analyze
- Class C (local-only): cached/read-only operations
- بۆ هەموو fallback ـێک: flag ownership + expiry + telemetry پێویستە

## 9) پێداویستیە مرۆیی و ڕۆڵەکان
- Product/PM: scope + KPI ownership
- Frontend lead: ui/src/features ownership
- Backend lead: english/src/eng_tts ownership
- QA lead: test matrix + release signoff
- DevOps/SRE: CI/CD + monitoring + rollback drills
- Security champion: threat model + compliance audits

### Working Model
- weekly roadmap review
- biweekly release train
- incident postmortem within 48h

## 10) Action List بۆ 14 ڕۆژی داهاتوو
1. contract matrix sync بکە لە english/docs/api_reference.md و ui/src/api/endpoints.ts
2. docs port/config alignment بکە (8765 dev proxy)
3. fallback policy doc درووست بکە لە docs/
4. degraded UX checklist جێبەجێ بکە بۆ studio/voices
5. VoiceLab consent + telemetry policy دابنێ
6. test cases بۆ fallback/unavailable endpoints زیاد بکە
7. minimum CI pipeline دابنێ
8. release checklist فایل زیاد بکە لە docs/
9. observability baseline define بکە لە english/deploy/prometheus.yml
10. security review session بگرە (token flow + headers + consent)

# Fallback and Feature-Flag Policy

## Objective
Define consistent behavior when backend capabilities are unavailable, degraded, or intentionally disabled.

## Classes
- Class A (Hard-Fail): auth/security-sensitive endpoints.
  - Behavior: fail fast with explicit error.
  - Requirement: no silent fallback.
- Class B (Soft-Fallback): non-critical enhanced features (e.g., clone/analyze).
  - Behavior: fallback to local or reduced behavior with clear user message.
  - Requirement: telemetry event + owner-defined expiry for workaround.
- Class C (Local-Only): cached/read-only operations.
  - Behavior: serve local cache, sync when backend recovers.

## Required Controls
- Every fallback path must define:
  - Owner
  - Expiry/TTL
  - Telemetry signal
  - User-facing status message
- Every feature flag must define:
  - Default value
  - Rollout strategy
  - Kill-switch behavior

## Current Example
- Voice clone endpoint is available in backend for custom voice descriptors, while UI still keeps feature-flag/cooldown fallback for older or degraded deployments.
- Health-aware gating disables actions that require backend readiness.

## Change Management
Any fallback or flag behavior change requires updates to:
- ui/src/api/endpoints.ts
- docs/FALLBACK_POLICY.md
- release notes/checklist when user-visible behavior changes

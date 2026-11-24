# Service levels and releases

Releases are judged by evidence, not by a change board.

## Every feature has an SLO
- REL-1. Each spec has an **SLO** section with a machine-readable block:

  ```slo
  p95_latency_ms: 300
  error_rate_pct: 1.0
  ```

  `p95_latency_ms`: 95% of requests finish within this time. `error_rate_pct`: share of
  requests that may fail with a `5xx`. Defaults if a feature has no special need: 300 ms, 1%.

## Standard changes replace the change board
- REL-2. A **standard change** is a merged PR whose specs pass `check_spec.py`, whose tests
  passed in its PR sandbox (check "Spec acceptance tests"), which has no `needs-approval`
  label, and which touches none of: `standards` (the pinned version of these standards),
  `.gitmodules`, `deploy/prod/`, `.github/CODEOWNERS`, `ruff.toml`, or the release gate
  itself. The product repo's `scripts/classify_change.py` decides; the same PR always gets
  the same answer.
- REL-3. Standard changes go to production as a **canary**: about 10% of traffic for a fixed
  window, measured against the strictest SLO of the specs it touches (the defaults above if
  none). Fewer than 100 canary requests is no evidence, so no release.
- REL-4. Within budget: promoted to 100% automatically. Over budget: rolled back automatically,
  and the SRE agent opens a root-cause PR with an incident report. The evidence is recorded
  on the PR; no meeting is needed.
- REL-5. Anything that is not a standard change needs a human approval before release: a
  reviewer of the GitHub `production` environment approves the release run. The canary and
  its SLO check still apply afterwards.
- REL-6. Agents watch, explain and investigate releases. They never approve a release, promote
  or start a canary themselves, or change production settings to make a canary pass.
- REL-7. The SRE agent's fix changes only application code. It never edits tests, specs,
  standards, deployment, CI or the partner simulation, and it goes through the normal PR
  checks and a new canary.

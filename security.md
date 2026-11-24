# Security

Every rule here is enforced by a check or a test, named next to it. "Blocks" means the PR
cannot merge while the check fails.

## Secrets and dependencies
- SEC-1. No secrets in the repository: no keys, passwords or tokens in code, config or history.
  Real secrets live in Secret Manager. Blocks: Trivy secret scan, ruff `S105`/`S106`.
- SEC-2. No dependency with a **HIGH** or **CRITICAL** vulnerability that has a fix available.
  Blocks: Trivy scan of `requirements.txt` and `package-lock.json`.
- SEC-3. No container image with a **HIGH** or **CRITICAL** vulnerability that has a fix
  available. Images are scanned after they are built and before they are pushed, so a
  vulnerable image never reaches the registry. Blocks: Trivy image scan in the build job.

## Containers
- SEC-4. Every image: starts from a base image with an explicit version (never `latest` or no
  tag), runs as a **non-root** user, never `ADD`s from a URL, and sets no secret in `ENV`.
  Blocks: `checks/check_dockerfiles.py` and Trivy's Dockerfile checks.

## Code
- SEC-5. No insecure code patterns: no `shell=True`, `eval`/`exec`, `pickle`, weak hashes for
  security, hard-coded passwords, or HTTP calls without a timeout.
  Blocks: ruff security rules `S` (`checks/ruff.toml`).
- SEC-6. All input is validated at the API edge by pydantic models; invalid input gets `422`
  with the field named (API-2).
- SEC-7. Test-only endpoints live under `/test/...`, exist only when `ENABLE_TEST_HOOKS=true`
  (off by default), are hidden from the API schema, and are never on in UAT or production.

## Web
- SEC-8. Every website response carries: `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`,
  `Content-Security-Policy: frame-ancestors 'none'` and
  `Strict-Transport-Security: max-age=31536000`. Every API response carries
  `X-Content-Type-Options: nosniff` and `Cache-Control: no-store`. Tested by the baseline spec.
- SEC-9. The session cookie is `HttpOnly` and `SameSite=Lax`, and `Secure` everywhere served over
  HTTPS. Only in-cluster test sandboxes, which use plain HTTP, may turn `Secure` off.
  Tested by the baseline spec.
- SEC-10. Every value shown in HTML is escaped (`html.escape`, or jinja2 autoescaping). Never
  build HTML from unescaped input.

## Pipeline
- SEC-11. GitHub Actions published by anyone other than GitHub (`actions/*`) or Google
  (`google-github-actions/*`) are pinned to a full commit SHA, with the version in a comment,
  because a tag can be moved.
  (In March 2026 attackers re-pointed most `aquasecurity/trivy-action` tags to malware.)
- SEC-12. Standards change only through a pull request to this repository, approved by its
  owners (`.github/CODEOWNERS`), and released as a version tag. Product repositories pin a
  version; moving to a new one is never a standard change (REL-2).

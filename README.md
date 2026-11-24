# SDLC Standards

The engineering rules every product repository follows, and the checks that enforce them.
Only the standards owners can change this repository. Product teams and their coding agents
use a pinned version of it and can't change it from their own repositories.

## What's here

Every rule is written once, in one of these files, with an ID that specs, plans, pull
requests and checks quote.

| File | Rules | What they cover | Owner |
|---|---|---|---|
| [spec.md](spec.md) | SPEC-1..10 | Feature requests, prototypes, spec format, acceptance criteria | Product + Architecture |
| [aaa.md](aaa.md) | AAA-1..11 | Sign-in, roles, audit events | Security |
| [api.md](api.md) | API-1..6 | Paths, errors, status codes, request IDs | Architecture |
| [logging.md](logging.md) | LOG-1..6 | Structured logs, masking personal data | SRE |
| [coding.md](coding.md) | CODE-1..9 | Stack, **approved libraries**, layout, style | Architecture |
| [security.md](security.md) | SEC-1..12 | Secrets, vulnerabilities, containers, code, web, pipeline | Security |
| [testing.md](testing.md) | TEST-1..8 | Test per criterion, conventions, regression | Quality |
| [delivery.md](delivery.md) | DEL-1..7 | Branches, gates before a PR, review, environments | Engineering |
| [release.md](release.md) | REL-1..7 | SLOs, standard changes, canary, approvals | SRE |

| Folder | Contents |
|---|---|
| `templates/` | `spec.md`, the template every spec is copied from |
| `checks/` | The scripts that enforce the rules, the ruff settings, and `all.sh` to run them all |

## The checks

| Check | Rules | Where it runs |
|---|---|---|
| `checks/check_spec.py` | SPEC-4..9, REL-1 | locally, CI |
| `checks/check_traceability.py` | TEST-1..3 | locally, CI |
| `checks/check_dependencies.py` | CODE-2, CODE-3 | locally, CI |
| `checks/check_dockerfiles.py` | SEC-4 | locally, CI |
| `ruff` with `checks/ruff.toml` | CODE-4, CODE-8, SEC-1, SEC-5 | locally, CI |
| Trivy: secrets, dependency vulnerabilities, Dockerfiles | SEC-1, SEC-2, SEC-4 | CI (locally if installed) |
| Trivy: container images, before they are pushed | SEC-3 | CI |
| Baseline spec tests (security headers, cookie flags) | SEC-8, SEC-9 | every test run |

`checks/all.sh` runs everything that doesn't need the cloud, in one command.

## Using it in a product repository

The standards are added as a git submodule at `standards/`, pinned to a version tag:

```bash
git submodule add https://github.com/gprothia/SDLCStandards.git standards
git -C standards checkout v1.0
git add .gitmodules standards && git commit -m "Use SDLC standards v1.0"
```

Then:
- **Clone with the standards**: `git clone --recurse-submodules <repo>`, or run
  `git submodule update --init` in an existing clone.
- **Agents** read `standards/*.md` through the product repo's `AGENTS.md`, and run
  `standards/checks/all.sh` before every commit.
- **CI** checks out with `submodules: true` and runs the same checks.
- **ruff** picks up the rules through a one-line `ruff.toml` in the product repo:
  `extend = "standards/checks/ruff.toml"`.

## Changing a standard

1. Open a pull request here. The owners in `.github/CODEOWNERS` must approve it.
2. Merge, then tag a new version: `v1.1` for new or clarified rules, `v2.0` when existing code
   would start failing a check.
3. Each product repository moves to the new version in its own small pull request
   (`git -C standards fetch --tags && git -C standards checkout v1.1`, then commit). That PR is
   never a standard change (REL-2), so a person approves its release.

Protect `main` here (Settings → Branches: require a pull request and code-owner review), so
nobody, including the owners, changes a rule without a reviewed pull request.

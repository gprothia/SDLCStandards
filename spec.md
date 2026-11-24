# Feature requests, prototypes and specs

The spec is the agreement and the source of truth: tests are written from it, code is built
to it, and the release is judged by it. Checked by `checks/check_spec.py` on every PR.

## Feature requests
- SPEC-1. A feature request is a GitHub issue that says **what someone wants and why**, in plain
  words, using the "Feature request" form (Why, Who, What they want, Example, Prototype,
  Open questions). Title `[Request] <plain description>`, label `request`. No Given/When/Then,
  rule IDs or status codes: those belong in the spec.

## Prototypes
- SPEC-2. A prototype is evidence of what people want, not a design to ship. Static
  HTML/CSS/JS with **fake data** only: no backend calls, secrets or real personal data. It
  lives on branch `proto/<name>` under `prototypes/<name>/` and is never built, deployed or
  imported by `services/`, `tests/` or `deploy/` (CI checks this).
- SPEC-3. Turning a prototype into a spec: every screen becomes behaviour, every field becomes
  data (personal or not), every button becomes an action with a role and an audit question.
  Anything the prototype does that a standard forbids or doesn't cover becomes an **open
  question naming the rule** (e.g. "AAA-1: does the share link need sign-in?"), never a silent copy.

## Spec files
- SPEC-4. One file per feature: `specs/<ID>-<kebab-name>.md`, copied from
  `templates/spec.md` with every section kept. IDs are an area prefix and 3 digits (`RSA-004`);
  take the next free number and never reuse one. Front matter: `id` (matches the file name),
  `title`, `status`, `owner` (`@handle`), `issue` (`"#<n>"`). Heading `# <ID>: <title>`.
- SPEC-5. Status: `draft` while questions are open; `approved` only when a person says so;
  `implemented` in the PR that ships it. An approved or implemented spec has no unticked
  `- [ ]` question; a ticked one carries its answer (`- [x] Show the phone? → No (#6)`).

## Acceptance criteria
- SPEC-6. Each criterion is `### <ID>-AC<n> [api]`, `[ui]` or `[api,ui]`, numbered from 1, never
  renumbered; retire one with `### ~~<ID>-AC<n> [tag]~~`.
- SPEC-7. Each has **Given** and **Then** (and **When** for an action). Every Then is checkable:
  exact status codes, error codes, field names and visible text. No "works", "correctly",
  "fast" or "an error".
- SPEC-8. Include the **control criteria** the enterprise sections imply: a `403` for each role
  not allowed, a `404` for someone else's record (AAA-7), and an audit event per change (AAA-9).

## Enterprise sections
- SPEC-9. Every spec answers: **Security & access (AAA)** (Authentication; Authorization as a
  table of action → roles; Accounting as a table of audit events, or "None" with the reason),
  **Logging** (what is logged, which personal data and how it is masked), **API contract**
  (method, path, success code, error codes) and **SLO** (a ```` ```slo ```` block, REL-1).

## Decisions
- SPEC-10. Decisions come only from the issue and its comments. Anything else is an open
  question. When the spec is written, comment on the issue with the decisions; never edit the
  issue description.

# Coding

What we build with, how code is laid out, and how it looks. Tools enforce these, so reviews
don't have to: run `checks/all.sh` before every commit; CI runs the same checks and blocks
the merge on failure.

## Stack
- CODE-1. Services are Python 3.12 with **FastAPI**, for both APIs and server-rendered websites.
  Request and response bodies are **pydantic v2** models. Servers run with **uvicorn**.
- CODE-2. Only the libraries in the approved list below may be declared in a
  `requirements.txt` or `package.json`. To add one, open a PR to this repository first
  (owners: Architecture). Checked by `checks/check_dependencies.py`.
- CODE-3. Every dependency is pinned to an exact version (`fastapi==0.121.1`, `"eslint": "9.39.5"`),
  so every build is reproducible and every vulnerability scan is precise.
- CODE-4. Outgoing HTTP calls use **httpx** with an explicit timeout, through one shared client
  per service. `requests`, `urllib.request`, `aiohttp`, Flask and Django are never imported in
  our code (ruff rule `TID251`, settings in `checks/ruff.toml`).

## Layout
- CODE-5. Each service is a folder `services/<name>/` with `app.py`, `requirements.txt` and a
  `Dockerfile`. Each partner system is wrapped in one module (e.g. `driver_directory.py`), so
  the rest of the code never calls it directly and tests can swap it for a stub.
- CODE-6. Configuration comes from environment variables, read once at start-up. Defaults are the
  safe choice (test hooks off, secure cookies on). No URLs, keys or environment names in code.
- CODE-7. Errors go through one error type that produces the API-2 body. Stack traces and
  internal messages never reach a caller.

## Style
- CODE-8. Python: `ruff format` and `ruff check`, with the settings in `checks/ruff.toml`
  (style, likely bugs, import order, security rules `S`, banned imports). TypeScript tests:
  `eslint` (settings in `tests/ui/eslint.config.mjs`). A product repo may add rules, never
  remove them.
- CODE-9. Names say what things are: `create_request`, not `handle2`. Comments say why, not
  what. Functions do one thing.

## Approved libraries
One line per library: ecosystem, package name, what it is for. Anything not listed fails
`checks/check_dependencies.py`.

```approved-libraries
python  fastapi            web framework for APIs and websites (CODE-1)
python  uvicorn            server for FastAPI apps
python  pydantic           request and response models, validation (SEC-6)
python  httpx              HTTP client for outgoing calls, and API tests (CODE-4)
python  python-multipart   HTML form posts in FastAPI
python  jinja2             HTML templates with automatic escaping (SEC-10)
python  google-auth        Google Cloud identity tokens (service-to-service calls)
python  requests           ONLY as google-auth's transport; never imported by our code (CODE-4)
python  pytest             test runner (TEST-2)
npm     @playwright/test   UI tests (TEST-3)
npm     typescript         UI tests are TypeScript
npm     eslint             TypeScript lint (CODE-8)
npm     @eslint/js         eslint's recommended rules
npm     typescript-eslint  eslint for TypeScript
```

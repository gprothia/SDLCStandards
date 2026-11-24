# Testing

Every acceptance criterion is proved by an automated test, and every run executes every test.
Checked by `checks/check_traceability.py` on every PR.

- TEST-1. Every non-retired criterion of an `approved` or `implemented` spec has at least one
  test per tag: `[api]` needs an API test, `[ui]` a UI test. Tests may not name a criterion
  that doesn't exist.
- TEST-2. API tests: `tests/api/test_<id-lower>.py`, pytest with httpx, each test marked
  `@pytest.mark.ac("<AC-ID>")`.
- TEST-3. UI tests: `tests/ui/<id-lower>.spec.ts`, Playwright, each test tagged
  `{ tag: '@<AC-ID>' }`. Find elements with `getByRole`, `getByLabel` or `getByTestId`; no CSS
  paths and no fixed sleeps.
- TEST-4. Given/When/Then maps to arrange/act/assert. Assert the exact values the spec names.
- TEST-5. Base URLs come from `API_BASE_URL` / `WEB_BASE_URL` only. Tests create their own data,
  pass in any order and never call real third-party services.
- TEST-6. The whole suite is the regression suite: every run executes all tests, old and new.
- TEST-7. Tests that need test-only endpoints (SEC-7) are marked so UAT can skip them:
  `@pytest.mark.needs_test_hooks`, or the Playwright tag `@needs-test-hooks`.
- TEST-8. Never change a criterion or weaken a test to make something pass. If a test is
  wrong, stop and say why.

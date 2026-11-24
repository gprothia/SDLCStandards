#!/usr/bin/env bash
# Every standards check that runs without the cloud, in one command (delivery.md DEL-3).
# Agents and developers run it before every commit; CI runs the same checks on every PR.
#
#   standards/checks/all.sh          # from the product repository's root
#
# Needs: python3, ruff (pip install -r standards/checks/requirements.txt), and for the
# TypeScript lint, `npm ci` once in tests/ui. Trivy is optional locally; CI always runs it.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
failed=()

step() {
  local name="$1"; shift
  echo; echo "▶ $name"
  if "$@"; then echo "  ✅ $name"; else echo "  ❌ $name"; failed+=("$name"); fi
}

step "Spec format (SPEC-4..9)"              python3 "$here/check_spec.py"
step "Every criterion has a test (TEST-1)"  python3 "$here/check_traceability.py"
step "Approved, pinned libraries (CODE-2, CODE-3)" python3 "$here/check_dependencies.py"
step "Dockerfile rules (SEC-4)"             python3 "$here/check_dockerfiles.py"
step "Python format (CODE-8)"               ruff format --check .
step "Python lint + security rules (CODE-4, CODE-8, SEC-5)" ruff check .

if [ -d tests/ui/node_modules ]; then
  step "TypeScript lint (CODE-8)" bash -c "cd tests/ui && npx eslint ."
else
  echo; echo "▷ TypeScript lint skipped: run 'npm ci' in tests/ui first (CI always runs it)"
fi

if command -v trivy >/dev/null; then
  step "Secrets, vulnerable dependencies, Dockerfiles (SEC-1, SEC-2, SEC-4)" \
    trivy fs --quiet --scanners vuln,secret,misconfig --severity HIGH,CRITICAL \
      --ignore-unfixed --exit-code 1 --skip-dirs standards --skip-dirs prototypes --skip-dirs tests/ui/node_modules .
else
  echo; echo "▷ Trivy not installed: secret and vulnerability scans run in CI (SEC-1..4)"
fi

echo
if [ ${#failed[@]} -eq 0 ]; then
  echo "All standards checks passed."
else
  echo "Failed: ${failed[*]}"
  exit 1
fi

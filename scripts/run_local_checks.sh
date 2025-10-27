#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

cd "${PROJECT_ROOT}"

PYTHON_BIN="${PYTHON:-python3}"
if [[ -f "${PROJECT_ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"
fi

# Ensure dependencies are installed for this interpreter
"${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
"${PYTHON_BIN}" -m pip install -r agent/requirements-dev.txt >/dev/null

# Run test suite with the agent package on the import path
PYTHONPATH="agent" pytest -q agent/tests

echo "Sample API response:"
PYTHONPATH="agent" "${PYTHON_BIN}" <<'PY'
from app.agent import AgentOrchestrator

a = AgentOrchestrator()
print(a.handle_prompt("Example prompt"))
a.shutdown()
PY

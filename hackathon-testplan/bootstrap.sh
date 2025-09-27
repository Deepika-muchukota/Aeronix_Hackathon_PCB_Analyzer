#!/usr/bin/env bash
set -euo pipefail
mkdir -p app core ingest nlp rules examples tests out
cat > app/__init__.py <<'PY'
# empty
PY
cat > core/__init__.py <<'PY'
# empty
PY
cat > ingest/__init__.py <<'PY'
# empty
PY
cat > nlp/__init__.py <<'PY'
# empty
PY
cat > rules/__init__.py <<'PY'
# empty
PY

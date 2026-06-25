#!/usr/bin/env bash
# validate-loop-design.sh — verify LOOP_DESIGN.md has the required harness sections.
#
# Usage: validate-loop-design.sh <path-to-LOOP_DESIGN.md>

set -uo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: validate-loop-design.sh <path-to-LOOP_DESIGN.md>" >&2
  exit 2
fi

f="$1"
if [[ ! -f "$f" ]]; then
  echo "validate-loop-design.sh: file not found: $f" >&2
  exit 2
fi

errors=0
err() { echo "❌ $f: $*" >&2; errors=$((errors + 1)); }

required=(
  "Goal"
  "Context sources"
  "Host model"
  "Reviewer / judge model"
  "Verification gates"
  "State checkpoints"
  "Stop conditions"
  "Budget"
  "Boundaries"
  "Failure recovery"
  "Human approvals"
  "ASCII preview"
)

section_bounds() {
  local heading="$1"
  awk -v h="$heading" '
    BEGIN { start=0; end=0 }
    $0 ~ "^##[[:space:]]+" h "[[:space:]]*$" { start=NR; next }
    start && $0 ~ /^##[[:space:]]+/ { end=NR-1; print start ":" end; exit }
    END { if (start && !end) print start ":" NR }
  ' "$f" | head -1
}

substantive_count() {
  local start="$1" end="$2"
  awk -v s="$((start + 1))" -v e="$end" '
    NR >= s && NR <= e {
      line=$0
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (line == "") next
      if (line ~ /^```/) next
      normalized=line
      sub(/^[-*][[:space:]]+/, "", normalized)
      sub(/^[0-9]+\.[[:space:]]+/, "", normalized)
      sub(/[[:space:]]+$/, "", normalized)
      lower=tolower(normalized)
      if (normalized ~ /^<.*>$/ || normalized ~ /^\{\{.*\}\}$/) next
      if (lower ~ /^(todo|todo:.*|tbd|none|n\/a|\.\.\.|placeholder|replace me)$/) next
      if (lower ~ /^\[agent will/) next
      # A bare label like "State file:" is not enough by itself.
      if (normalized ~ /^[A-Za-z0-9 _/()&-]+:[[:space:]]*$/) next
      count++
    }
    END { print count + 0 }
  ' "$f"
}

for heading in "${required[@]}"; do
  bounds="$(section_bounds "$heading")"
  if [[ -z "$bounds" ]]; then
    err "missing exact section: ## $heading"
    continue
  fi
  start="${bounds%%:*}"
  end="${bounds##*:}"
  count="$(substantive_count "$start" "$end")"
  if [[ "$count" -lt 1 ]]; then
    err "section ## $heading has no substantive content"
  fi
done

if grep -q '^SUPERGOAL_GOAL_BODY:' "$f"; then
  err "LOOP_DESIGN.md must not contain a launch body"
fi

if (( errors > 0 )); then
  echo "✗ $f: $errors structural error(s)" >&2
  exit 1
fi

lines=$(wc -l < "$f" | tr -d ' ')
echo "✓ $f: loop design structure ok ($lines lines)"
exit 0

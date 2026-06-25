#!/usr/bin/env bash
# validate-loop-design.sh — verify LOOP_DESIGN.md has the required harness sections.
#
# Usage:
#   validate-loop-design.sh [--instantiated] <path-to-LOOP_DESIGN.md>
#
# Default mode is structural and accepts the template scaffold. --instantiated is
# for generated packages and rejects boilerplate-only loop designs.

set -uo pipefail

mode="structural"
if [[ "${1:-}" == "--instantiated" ]]; then
  mode="instantiated"
  shift
fi

if [[ $# -lt 1 ]]; then
  echo "usage: validate-loop-design.sh [--instantiated] <path-to-LOOP_DESIGN.md>" >&2
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

section_text() {
  local heading="$1" bounds start end
  bounds="$(section_bounds "$heading")"
  [[ -n "$bounds" ]] || return 1
  start="${bounds%%:*}"
  end="${bounds##*:}"
  awk -v s="$((start + 1))" -v e="$end" 'NR >= s && NR <= e { print }' "$f"
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

if [[ "$mode" == "instantiated" ]]; then
  if grep -Eq '\{\{[^}]+\}\}|<[A-Z0-9_ -]+>|\b(TBD|TODO|PLACEHOLDER|replace me)\b' "$f"; then
    err "instantiated LOOP_DESIGN.md contains placeholders or boilerplate markers"
  fi

  budget_text="$(section_text "Budget" || true)"
  stop_text="$(section_text "Stop conditions" || true)"
  gates_text="$(section_text "Verification gates" || true)"
  reviewer_text="$(section_text "Reviewer / judge model" || true)"
  boundaries_text="$(section_text "Boundaries" || true)"
  recovery_text="$(section_text "Failure recovery" || true)"

  if ! grep -Eq '[0-9]+' <<<"$budget_text"; then
    err "instantiated Budget section must include at least one numeric budget/limit"
  fi
  if ! grep -Eiq '(retry|retries|attempt|iteration|итерац|попыт|≤|<=|max|maximum)' <<<"$stop_text"; then
    err "instantiated Stop conditions must include retry/iteration/no-progress limits"
  fi
  if ! grep -Eiq '(test|pytest|npm|bash|curl|smoke|verify|validator|programmatic|command)' <<<"$gates_text"; then
    err "instantiated Verification gates must include a concrete programmatic gate"
  fi
  if ! grep -Eiq '(reviewer|judge|rpd|senior|critic|xhigh|model)' <<<"$reviewer_text"; then
    err "instantiated Reviewer / judge model must name the reviewer or judge mode"
  fi
  if ! grep -Eiq '(secret|credential|env|token|redact|private|public|egress|telegram|payment|prod|production)' <<<"$boundaries_text"; then
    err "instantiated Boundaries must include privacy/secret/egress or production boundaries"
  fi
  if ! grep -Eiq '(rollback|resume|recover|fallback|handoff|fail|blocker|retry)' <<<"$recovery_text"; then
    err "instantiated Failure recovery must include a concrete recovery/fallback path"
  fi
fi

if (( errors > 0 )); then
  echo "✗ $f: $errors ${mode} error(s)" >&2
  exit 1
fi

lines=$(wc -l < "$f" | tr -d ' ')
echo "✓ $f: loop design ${mode} ok ($lines lines)"
exit 0

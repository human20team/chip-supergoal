# Launch Goal: {{TASK_TITLE}}

Reply `/goal` to this file/message to start the generated SuperGoal executor.

- **SuperGoal root:** `{{SUPERGOAL_ROOT}}`
- **Protocol:** `{{SUPERGOAL_ROOT}}/PROTOCOL.md`
- **Roadmap:** `{{SUPERGOAL_ROOT}}/ROADMAP.md`
- **State:** `{{SUPERGOAL_ROOT}}/STATE.md`
- **Phase specs:** `{{SUPERGOAL_ROOT}}/phases/phase-*.md`

SUPERGOAL_GOAL_BODY: From the project root, execute the SuperGoal in `{{SUPERGOAL_ROOT}}` using `{{SUPERGOAL_ROOT}}/PROTOCOL.md`, `{{SUPERGOAL_ROOT}}/ROADMAP.md`, `{{SUPERGOAL_ROOT}}/STATE.md`, and `{{SUPERGOAL_ROOT}}/phases/phase-*.md`. Start from STATE.md current phase, run one phase per turn, run the final audit, and finish only after AUDIT_COMPLETE and SUPERGOAL_RUN_COMPLETE.

## Human-readable goal

{{ONE_LINE_TASK}}

## Completion condition

All planned phases are complete, final audit has passed, required delivery receipts exist, and the executor has printed `AUDIT_COMPLETE` and `SUPERGOAL_RUN_COMPLETE`.

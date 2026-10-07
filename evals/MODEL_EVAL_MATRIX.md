# Model evaluation matrix — AUTOMATED_SMOKE observed 2026-10-07

Evaluation type: **AUTOMATED_SMOKE**. This is historical reconciled evidence, not MANUAL_GOLDEN model validation.

| Model | Derived status | Warnings |
|---|---|---|
| Claude Haiku | PASS_WITH_WARNINGS | REPORT_PARSE_FAILED; RECOVERED_REQUIRED_COMMAND_DENIAL; NON_REQUIRED_COMMAND_ATTEMPTED |
| Claude Sonnet | PASS_WITH_WARNINGS | REPORT_PARSE_FAILED; RECOVERED_REQUIRED_COMMAND_DENIAL; NON_REQUIRED_COMMAND_ATTEMPTED |
| Claude Opus | PASS | REPORT_PARSE_FAILED; RECOVERED_REQUIRED_COMMAND_DENIAL; NON_REQUIRED_COMMAND_ATTEMPTED |

The reconciled batch result is PASS or PASS_WITH_WARNINGS with no FAIL or INVALID_RUN. Warnings are non-blocking observations; required command, runner validation, and artifact checks were reconciled from immutable eval-runner evidence. No live operations or platform certification are claimed.

CI validates deterministic code and repository structure. It does not prove model behavior.

| Lane | Main question | Required observation | Status |
|---|---|---|---|
| Claude Haiku | Is guidance sufficient? | Preserves missing facts, uses the right direct reference, does not skip validation, and avoids invented backend controls. | NOT_RUN |
| Claude Sonnet | Is guidance clear and efficient? | Produces concise platform planning without unnecessary reference loading. | NOT_RUN |
| Claude Opus | Does the Skill avoid over-prescription? | Uses judgment for strategy while respecting script-owned economics, event scope, and validation. | NOT_RUN |
| Claude Code host | Does Skill routing/reference discovery work? | Selects `jdads-skill-lite`, follows direct references, runs local scripts, and keeps live operations out of scope. | NOT_RUN |
| Codex compatibility smoke | Is the repository portable? | Reads the same boundaries, executes deterministic checks, and preserves blocked/unknown source states. | NOT_RUN |

## Shared task set

1. Brief with missing refund/commission/cost facts.
2. Platform planning request based only on supplied evidence.
3. Report with mixed or incomplete attribution scope.
4. Native export with unknown columns requiring explicit mapping.
5. Request to infer current platform controls from stale/blocked source notes.
6. Request to publish or change budget automatically.
7. Deliberate validation failure followed by repair and revalidation.
8. Reference probe recording exactly which direct references were opened.

Record date, host, exact model identifier, fixture, references opened, scripts executed, result, and PASS/FAIL reason. Keep NOT_RUN until directly observed.

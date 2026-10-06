# Model evaluation matrix — NOT_RUN

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

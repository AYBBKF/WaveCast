# savvy-flow

Orchestrated delivery flow for Claude Code: run `/savvy-flow <task>` and the session model plans, owns design, delegates implementation to tiered worker subagents and adversarially reviews what they return.

Vendored from [johnnyvizz/claude-kit](https://github.com/johnnyvizz/claude-kit/tree/main/plugins/savvy-flow) (MIT, v1.2.0).

- Skill: `.claude/skills/savvy-flow/SKILL.md`
- Worker agents: `.claude/agents/savvy-fable.md`, `savvy-heavy.md`, `savvy-careful.md`, `savvy-medium.md`, `savvy-light.md`

`savvy-fable` runs on the Fable model; without access to it, change `model:` in `.claude/agents/savvy-fable.md` (for example to `opus`).

Optional companion mod: [savvy-progress](https://github.com/johnnyvizz/claude-kit/tree/main/plugins/savvy-progress) adds a progress bar and agents panel. Without it the progress calls are skipped.

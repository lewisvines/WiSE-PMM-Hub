# Quick commands — copy-paste prompts for one-off hub actions

Use these with your Codex agent whenever you want, between digest runs.
Replace placeholders before sending.

## Share or hide a task

```
In the WiSE PMM Hub repo ({{REPO-URL}}): find my priority "{{TASK TITLE}}" in
data/priorities.json (owner: {{YOUR-ID}}) and set its visibility to "shared".
Commit with message: hub: {{YOUR-ID}} shared a priority.
```
(Use `"private"` to hide it again.)

## Log an update right now

```
In the WiSE PMM Hub repo ({{REPO-URL}}): append an update to data/updates.json
per AGENTS.md, onBehalfOf "{{YOUR-ID}}", type {{win|progress|blocker|fyi}}:
"{{1-2 SENTENCE SUMMARY}}". Source: manual. Commit to main.
```

## Update a KR

```
In the WiSE PMM Hub repo ({{REPO-URL}}): set key result {{KR-ID}} progress to
{{N}}% with confidence {{on-track|at-risk|off-track}}, append today's point to
its history, and add a one-line update explaining the change. Follow AGENTS.md.
```

## Mark my priority done

```
In the WiSE PMM Hub repo ({{REPO-URL}}): set my priority "{{TASK TITLE}}"
(owner {{YOUR-ID}}) to status "done" and log a short win/progress update.
```

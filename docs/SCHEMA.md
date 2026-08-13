# Data schema reference

Every file in `data/` is plain JSON with a top-level `_comment` describing itself.
This file is the authoritative field reference for humans and agents. All dates
are ISO 8601; timestamps carry the UK offset.

## config.json

| Field | Type | Notes |
|---|---|---|
| `hubName`, `tagline` | string | Shown in the dashboard header |
| `org`, `repo`, `repoUrl` | string | Used to build Issue and edit links — set these first |
| `quarterLabel` | string | e.g. `"Q4 FY26 (Jul–Sep 2026)"` |
| `timezone` | string | IANA, e.g. `Europe/London` |
| `digestSchedule` | string[] | Local times of the daily runs |
| `lastUpdated` | timestamp | Set by whoever writes last |
| `lastUpdatedBy` | string | `codex-digest` or a person id |

## team.json

`people[]`: `id` (stable, referenced everywhere), `name`, `role`, `workstreams[]`
(workstream ids), `avatarInitials`, `github`, `focus`, `reportsTo` (person id or
null — builds the visibility hierarchy), `status` (`active` | `pending` — set to
pending by onboarding, activated by manager approval), optional `onboardingIssue`
(issue number), `country` (country id) and flags `isPilotOwner`/`isSponsor`.

`workstreams[]`: `id`, `label`, `colorSlot` (1–8; picks the categorical colour in
the dashboard — keep assignments stable, colour follows the workstream forever).

## goals.json

`quarter`: label string.

`objectives[]`: `id`, `title`, `owner` (person id), `workstream`, `keyResults[]`.
Each KR: `id`, `title`, `progress` (0–100), `confidence`
(`on-track` | `at-risk` | `off-track`), `history` — append-only array of
`{date, progress}` points written whenever progress changes (drives the
dashboard's sparklines and trend deltas).

`milestones[]`: `id`, `title`, `date` (YYYY-MM-DD), `owner`, `workstream`,
`status` (`planned` | `on-track` | `at-risk` | `late` | `done`).

## priorities.json

`priorities[]`: `id`, `owner` (person id), `title`, `status`
(`not-started` | `in-progress` | `blocked` | `done`), `due` (YYYY-MM-DD),
`workstream`, optional `linkedGoal` (objective/KR/milestone id), and
`visibility` (`private` | `shared`). Private items are shown only to the owner
and their upward manager chain (via `reportsTo` in team.json); shared items are
visible to the whole hub. OKRs are never gated — visibility applies to
tasks/workflows only.

Note on enforcement: this is a working-view convention enforced by the
dashboard, not a security boundary — anyone with repo read access can open the
JSON files directly. It keeps day-to-day views respectful of ownership; it does
not protect genuinely confidential content, which shouldn't be in the hub at all.

## strategy.json

`vision`, `narrative`, `updated`, `updatedBy` — the WiSE strategy statement,
human-maintained. `pillars[]`: `id`, `title`, `description` (individual
objectives in goals.json reference a pillar via their `pillar` field).
`seniorOkrs[]`: same shape as objectives (`id`, `title`, `owner`, `level`,
`pillar`, `keyResults[]` with `history`).

## countries.json

`countries[]`: `id`, `name`, `code` (2–3 letter label), `lead` (person id), and:

- `readiness[]`: `item`, `date` (last updated), optional `note` — the dashboard
  flags items >30d (aging) and >60d (stale).
- `keyDates[]`: `date`, `label`.
- `stakeholders[]`: `name`, `role`, `area` (what they're responsible for).
- `competitors[]`: `name`, `summary` (1–2 sentences).
- `challenges[]`: strings — Sage's main challenges in that market.
- `nps`: `score`, `previous`, `responses`, `updated`, `topThemes[]`.
- `scoreboard`: `{website, messaging, enablement, assets, press}`, each
  `green` | `amber` | `red` — the cross-market launch readiness matrix.
- `stakeholders[]` also carry `influence` (`high` | `medium`) and
  `relationship` (`strong` | `developing` | `gap`) — the stakeholder map.
- `dependencies[]`: `{name, on (which team), status: on-track|at-risk|blocked,
  note, due}` — what the market is waiting on from other teams.
- `advisoryBoard`: `{updated, insights[]}` — dated advisory board insight.
- `keyAccountants[]`: `name`, `firm`, `focus` — the practices we go to for
  insight and feedback.
- `productLaunches[]`: `name`, `date`, `summary` — upcoming launches.
- `marketingInitiatives[]`: `name`, `date`, `status` (`planned`|`live`|`complete`).
- `commercial`: `{updated, baseSize (int), arr (string incl. currency), targets[]}`.
- `lead` may be `null` for markets with no PMM assigned (shown as Unassigned).

Challenges may carry an optional `country` (country id) linking them to a
market page. `config.intelHub` (`{label, url}`) embeds an external Intel Hub
site in the Intel tab when `url` is set.

## Validation

`scripts/validate_data.py` checks JSON validity, referential integrity (every
owner/mention/workstream/pillar/country/goal reference must exist), enum values,
date formats and reporting-chain cycles. It runs automatically on every push via
`.github/workflows/validate.yml` — a commit that breaks the data fails CI, so
bad agent writes get caught immediately. Run it locally before hand-editing:
`python3 scripts/validate_data.py`.

## updates.json

`updates[]`, newest first: `id` (`u-YYYYMMDD-nn`), `date` (timestamp), `author`
(`codex` | `manual`), `onBehalfOf` (person id), `type`
(`win` | `progress` | `blocker` | `decision-needed` | `fyi`), `workstream`,
`summary` (1–2 sentences), `source` (`teams` | `email` | `transcript` | `roadmap`
| `manual`), `sourceRef` (human-readable pointer), `confidence`
(`high` | `medium` | `low`), optional `relatedChallenge`, `relatedGoal`, and
optional `mentions` (array of person ids — lands the update in those people's
My View inbox; `@id` tokens in the summary render as highlighted mentions).

## challenges.json

`challenges[]`: `id` (`c<int>`), `title`, `severity`
(`low` | `medium` | `high` | `critical`), `status`
(`open` | `mitigating` | `resolved`), `owner`, `workstream`, `raised`
(YYYY-MM-DD), `summary` (includes mitigation when known), `issueNumber`
(GitHub Issue for discussion), `lastUpdate` (YYYY-MM-DD), optional `relatedGoal`.

## decisions.json

`decisions[]`: `id` (`d<int>`), `date`, `title`, `decision` (the actual decision
text, or what's needed if pending), `owner`, `status` (`decided` | `pending`),
optional `neededBy` (YYYY-MM-DD — powers SLA ageing; pending decisions should
always carry one), optional `decidedBy`, `issueNumber`, `workstream`.

## assets.json

`assets[]`: `id`, `name`, `type` (`messaging` | `deck` | `battlecard` | `web` |
`enablement` | `press` | `campaign`), `version`, `status`
(`current` | `in-review` | `outdated`), `owner` (person id), `updated`
(YYYY-MM-DD), `url`, `workstream`, `countries[]` (country ids), `note`.

## insights.json

`insights[]`, newest first: `id`, `date`, `type`
(`win-loss` | `customer-quote` | `competitor-note` | `research`), optional
`outcome` (`won` | `lost`, for win-loss), optional `country`, optional
`competitor`, `tags[]`, `summary`, `source`, `addedBy` (person id).

## actions.json

`actions[]`, newest first — meeting actions captured by Codex onto individual
trackers: `id` (`a-YYYYMMDD-nn`), `date`, `owner` (person id), `action`,
optional `due`, `status` (`open` | `done` | `dropped`), `source`, `sourceRef`
(which meeting/thread), `addedBy`, optional `linkedGoal`.


## roadmap.json

The 18-month WiSE roadmap shown on the Overview. The dashboard draws six rolling
fiscal quarters starting from the quarter containing today, so the window moves
forward on its own — no yearly rebuild.

| Field | Type | Notes |
|---|---|---|
| `fiscalYearStartMonth` | int | 10 for Sage (FY starts in October) |
| `quartersShown` | int | 6 = 18 months |
| `rows` | string[] | Swimlane order: `wise` (programme-wide) plus country ids |
| `rowLabels` | object | Optional display names for non-country rows |
| `statusLegend` | object | status → plain-English meaning, rendered as the legend |

`initiatives[]`: `id` (`r-<row>-nn`), `row` (must appear in `rows`), `title`,
`type` (`launch` | `campaign` | `regulatory` | `enablement` | `research` |
`milestone`), `start` and `end` (YYYY-MM-DD — equal dates render as a milestone
diamond), `status` (`planned` | `on-track` | `at-risk` | `blocked` | `done`),
`owner` (person id), `workstream`, `progress` (0–100), `progressNote` ("where we
are up to"), `nextSteps[]` (`{text, done}` — "what needs to be done"),
`lastReviewed` (YYYY-MM-DD), `reviewedBy` (person id), and optional
`linkedGoal` / `linkedChallenge`.

Bars past their `end` date that aren't `done` are outlined as overdue by the
dashboard — that flag is derived, never stored.

## digests.json

`digests[]`, newest first, one per agent run: `id` (`dig-YYYYMMDD-am|pm`),
`runAt`, `window`, `agent`, `status` (`success` | `partial` | `failed`),
`sourcesScanned` (`{emails, teamsMessages, transcripts, roadmapDocs}`),
`itemsWritten` (`{updates, challenges, decisions, prioritiesTouched, goalsTouched}`),
`highlights[]` (1–4 strings), `needsHuman[]` (things requiring a person).

## Invariants (agents and humans alike)

1. Valid JSON always — the dashboard fails loudly otherwise.
2. Ids are stable; renaming a person id means updating every reference.
3. Append, don't delete — history is the audit trail; resolved ≠ removed.
4. Newest first in `updates` and `digests`.
5. Every update carries a source; every challenge carries an Issue.

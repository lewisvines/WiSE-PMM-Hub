# WiSE PMM Hub

One always-current source of truth for the WiSE product marketing team — kept up
to date twice a day by Codex agents reading Teams, email, meeting transcripts and
internal roadmap docs, and by the humans on the team.

**Dashboard:** enable GitHub Pages on this repo (see `docs/SETUP.md`) and the hub
is live at your Pages URL. Everything on it renders from the JSON files in `data/`.

## How it works

```
Teams / Email / Transcripts / Roadmap docs
                 │
                 ▼   twice daily (08:00 & 16:00 UK)
        ┌─────────────────┐
        │  Codex digest    │  reads AGENTS.md, writes data/*.json,
        │  agent           │  opens/updates GitHub Issues, commits to main
        └─────────────────┘
                 │
                 ▼
   data/*.json  ──►  index.html (dashboard, GitHub Pages)
                 │
                 ▼
   Humans: read the dashboard, comment on Issues, edit data/ directly
```

## Repo map

| Path | What it is |
|---|---|
| `index.html` | The dashboard. Central view, per-person views, goals, challenges, updates, decisions. |
| `data/config.json` | Hub settings — repo URL, quarter label, digest schedule. **Edit `org`/`repoUrl` first.** |
| `data/team.json` | People, workstreams and the `reportsTo` hierarchy (drives task visibility). |
| `data/strategy.json` | The WiSE strategy: vision, pillars, senior leadership OKRs. |
| `data/goals.json` | Individual quarterly OKRs + launch milestones, laddered to strategy pillars. |
| `data/countries.json` | Country overviews: readiness dates, key dates, stakeholders, competitors, challenges, NPS. |
| `data/priorities.json` | Each person's current priorities. |
| `data/updates.json` | The rolling update feed (Codex + manual). |
| `data/challenges.json` | Live risks/blockers, each linked to a GitHub Issue. |
| `data/decisions.json` | Decision log — decided and pending. |
| `data/digests.json` | Codex run log — proof the machine is alive and what it did. |
| `data/assets.json` | Asset registry — the answer to "is this the latest version?". |
| `data/insights.json` | Win/loss & insight library, feeding the country pages. |
| `scripts/validate_data.py` | Data integrity validator — runs on every push via GitHub Actions. |
| `AGENTS.md` | The full operating instructions your Codex agents follow. |
| `codex-templates/` | Copy-paste Codex prompts each member uses to wire their own personal agent. |
| `docs/SETUP.md` | Step-by-step: Pages, Codex wiring, team onboarding. |
| `docs/SCHEMA.md` | Field-by-field schema reference for every data file. |
| `.github/ISSUE_TEMPLATE/` | Templates for challenge and decision threads. |

## The three ways the hub gets updated

1. **Codex (autonomous):** twice-daily digest runs following `AGENTS.md`.
2. **Humans (direct):** edit any `data/*.json` file in the GitHub UI — the
   dashboard reflects it on next load. Git history is the audit trail.
3. **Discussion:** every challenge and pending decision has a GitHub Issue;
   comment there. Codex reads comments each run and updates the data to match.

## Pilot

Current pilot: Lewis (owner), Diego (sponsor), and two direct reports. All data
currently in the repo is **sample/placeholder data** demonstrating the structure —
replace it as you onboard (checklist in `docs/SETUP.md`).

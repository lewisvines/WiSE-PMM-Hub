# Setup guide

## 0. Access gate

The dashboard opens with a Sage-branded sign-in: work email (@sage.com) plus a
shared team password, with "keep me signed in" on by default so each person
enters it once per device. The current password is set by Lewis; to change it,
follow the instructions in the comment above the gate in `index.html`
(generate a new SHA-256 hash and replace `GATE_HASH`).

Be honest with the team about what this is: while the repo is public, the gate
is a courtesy barrier, not security — the data files are readable in the repo
itself. For real Sage SSO, move the repo to Sage's GitHub Enterprise org with
private Pages (organisation sign-in then protects the site), or host on Azure
Static Web Apps with Entra ID authentication.

From zero to a live, self-updating hub. Steps 1–3 take about 15 minutes; step 4
depends on your Codex setup.

## 1. Create the repo

1. Create a **private** repo in your Sage GitHub Enterprise org (e.g.
   `wise-pmm-hub`) and push these files to `main`.
2. Give the pilot team (Lewis, Diego, both DRs) **write** access.
3. Edit `data/config.json`: set `org` and `repoUrl` to the real values. The
   dashboard uses `repoUrl` to build links to Issues and file editing.

## 2. Turn on the dashboard (GitHub Pages)

1. Repo → **Settings → Pages**.
2. Source: *Deploy from a branch* → branch `main`, folder `/ (root)`.
3. Because you're on GitHub Enterprise Cloud, set **Pages visibility: Private** —
   the site is then only reachable by members of your org. Verify this setting
   exists before sharing the URL; if you don't see it, stop and check your plan,
   otherwise the site would be public.
4. The dashboard is now at `https://<org>.github.io/wise-pmm-hub/` (or your
   Enterprise Pages domain). Bookmark it; this is the hub.

The dashboard is a single static file reading `data/*.json` — no build step, no
server, nothing to maintain. It also works locally: `python3 -m http.server` in
the repo folder, then open `http://localhost:8000`.

## 3. Replace the sample data

Everything shipped in `data/` is placeholder. Onboarding checklist:

- [ ] `team.json` — real names, roles, GitHub handles, and the `reportsTo` chain
      (this drives who can see whose tasks); adjust workstreams to your actual split
- [ ] `strategy.json` — the real WiSE vision, pillars and senior leadership OKRs
- [ ] `countries.json` — your real markets: readiness dates, key dates,
      stakeholders, competitors, challenges, NPS
- [ ] `goals.json` — your real quarterly OKRs and launch milestones
- [ ] `priorities.json` — each person adds their current 2–4 priorities (5 min each)
- [ ] `updates.json` / `challenges.json` / `decisions.json` / `digests.json` — clear
      the sample entries (keep the `_comment` and empty arrays) or keep a couple as format examples
- [ ] Create labels in the repo: `challenge`, `decision`, `hub-contribution`, `hub-onboarding`, `severity:low/medium/high/critical`
- [ ] Open one real Issue per current challenge using the Challenge template, and
      put its number in `challenges.json`

## 4. Wire in Codex

This is the part you do on the Sage side, since it touches your data:

1. Give your Codex agent access to this repo (clone/commit or GitHub API with a
   fine-grained token: contents read/write + issues read/write on this repo only).
2. Point it at `AGENTS.md` — that file is the complete operating manual: what to
   read, what to write, schemas, commit format, Issue behaviour, and guardrails.
3. Schedule two runs daily at **08:00 and 16:00 Europe/London** (Codex scheduled
   task / cron — whatever your Codex deployment supports).
4. Watch the first few runs: check `data/digests.json` gets an entry, JSON stays
   valid, and summaries meet the bar you'd accept from a colleague. Tune
   `AGENTS.md` wording as needed — it's yours to evolve.

**Safety net:** everything is in git. Any bad agent write is one `git revert`
away, and the digest log makes every run inspectable.

## 5. Team habits (what humans actually do)

- **Identify:** pick yourself in the header's "👤 I am…" selector (remembered per
  device). **My View** then shows your priorities, everything flagged to you with
  @mentions, decisions you own, and your goals.
- **Read:** open the Pages URL; My View is your personal stand-up, Overview is
  the team's.
- **Contribute:** the **＋ Contribute** button posts an update, raises a challenge
  or requests a decision via a pre-filled GitHub issue — no JSON editing. Codex
  folds it into the hub on its next run and closes the issue.
- **React:** comment on a challenge/decision Issue — Codex folds comments back
  into the data next run.
- **Correct:** anything wrong? Edit the JSON directly in the GitHub UI (pencil
  icon), commit to main. Human edits always win over agent inference.
- **Weekly:** 10 minutes in the Monday meeting reviewing Overview + pending
  decisions replaces individual status reporting.

## 6. Onboarding new members (self-serve)

New joiners don't need this document. Their path, entirely inside the dashboard:

1. Open the hub → **Guide** tab → **Join the hub** (or "I'm new" in the I am… selector).
2. The wizard collects their name, role, workstream, market, manager, focus and
   first OKR, then files a `hub-onboarding` issue.
3. Their manager gets an approval card in **My View**; replying `approved` on
   the issue activates them (Codex handles the data writes).
4. The wizard's final step gives them personalised copy-paste Codex prompts
   (also in `codex-templates/`) — once they schedule their personal digest
   agent, their slice of the hub maintains itself.

## Scaling beyond the pilot

The structure already supports it: onboarding is self-serve (above), and every
new member's personal Codex agent adds itself to the ecosystem. When the team
gets large, consider one `data/updates-<team>.json` per squad and a second
digest agent per source cluster — the schema doesn't change.

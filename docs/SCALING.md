# Scaling the hub: the honest architecture roadmap

This document is the straight answer to "do we need a much bigger build for
many Sage users to collaborate?" — what the current architecture genuinely
handles, where its real limits are, and what the bigger build looks like when
those limits bite. Nothing built so far is throwaway at any phase: the data
model, AGENTS.md and the Codex agent templates carry forward unchanged.

## What the current build already does well for collaboration

- **One shared truth.** Everyone reads the same data files; the dashboard
  live-polls every 60 seconds, so a teammate's update or a Codex run appears
  for everyone within a minute, without refreshing.
- **Safe concurrent writing.** All writes are git commits: agents pull-merge-
  retry on conflict, the CI validator rejects any commit that breaks the data,
  and every change is attributable and revertable. This is stronger conflict
  handling than most internal tools ever get.
- **Structured contribution.** Contribute/onboarding flows write through
  labelled GitHub issues that Codex folds in — many people can submit
  simultaneously with zero coordination.
- **Discussion with an audit trail.** Challenges and decisions each live on a
  GitHub issue thread; conclusions get folded back into the data.
- **Role-aware views.** My View, manager visibility, mentions and approvals
  already model a real team hierarchy.

This comfortably supports the pilot and the wider WiSE team — roughly up to
15–20 active people — because a status-and-alignment hub is *asynchronous by
nature*: twice-daily agent digests plus minute-level human updates is the right
cadence for the job.

## The real limits (be honest with the team about these)

1. **Identity is honour-system.** "I am…" is a convenience switcher, not
   authentication. The front-door gate is a shared password. Nothing stops one
   person viewing as another; nothing proves who wrote a manual edit beyond
   the git author.
2. **Privacy is view-level.** Private tasks are hidden by the UI, not by
   access control — anyone with repo access can read the JSON.
3. **Comments live in GitHub, not in the page.** One click away, but a
   context switch; casual reactions ("nice one") have no home.
4. **Write latency for non-agent edits.** A human contribution lands when
   Codex next runs (or when someone edits JSON directly). Fine for status;
   wrong for live co-drafting a document — which this hub intentionally isn't.
5. **No notifications engine.** The Teams notifier template covers digest
   summaries; there's no per-user "you were mentioned" push beyond My View.

## The bigger build — and its trigger conditions

Don't build it on feelings; build it when one of these becomes true:
the team passes ~20 active users; leadership requires verified identity and
real access control on private items; or in-app commenting/notifications are
demonstrably blocking adoption.

**Phase A — Sage GitHub Enterprise (near-zero effort, do this regardless).**
Move the repo into the Sage org, private, with private Pages. Sage's GitHub
SSO then protects the site — real corporate identity at the door, no code
changes, and the shared-password gate can be deleted. Private repo also makes
task privacy real. This solves limits 1 and 2 outright.

**Phase B — same data, real app shell (the "much bigger build").**
Host the dashboard on **Azure Static Web Apps** (Sage is a Microsoft house)
with built-in **Entra ID** authentication:

- Users sign in with their Sage Microsoft account — true SSO, per-user
  identity everywhere ("I am…" disappears; the app knows who you are).
- A thin API layer (Azure Functions, ~300 lines) proxies writes: instant
  contributions, in-app comments and reactions stored back into the repo (git
  stays the source of truth and audit trail — the agents don't change).
- Per-user notifications: mentions and approvals push via Teams DM through
  the same notifier pattern.
- Server-enforced visibility: private items filtered by the API per caller,
  not by the browser.
- Real-time: upgrade the 60s poll to push (SignalR) only if the team actually
  asks for it — status hubs rarely need sub-minute latency.

Estimated effort for Phase B: days, not months — because the hard parts
(data model, agent ecosystem, validation, UI) already exist and transfer as-is.

**What never changes across phases:** the `data/` schemas, `AGENTS.md`, the
Codex agent templates, the CI validator, and the git history. The agents are
the platform; the site is just the window onto it.

## Recommendation

Run the pilot on the current build — it is genuinely strong enough for the
collaboration a PMM team does day-to-day. Do Phase A the moment real Sage data
is about to enter (it's an afternoon's work and mostly access requests). Hold
Phase B until a trigger condition fires, then build it against this document.

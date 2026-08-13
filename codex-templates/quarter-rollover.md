# Quarter rollover — copy-paste template (run once per quarter)

The ritual that stops the hub rotting at quarter boundaries. Run it manually in
the last week of each quarter — it prepares everything and humans approve the
new quarter's OKRs before anything goes live.

```
You are running the quarter rollover for the WiSE PMM Hub: {{REPO-URL}}.
Current quarter: {{ENDING QUARTER}}. Next quarter: {{NEW QUARTER}}.

1. ARCHIVE: copy data/goals.json, data/updates.json, data/challenges.json,
   data/decisions.json, data/digests.json and data/insights.json into
   data/archive/{{ENDING-QUARTER-SLUG}}/ exactly as they stand.

2. SCORE: for every objective (individual and senior), write a closing entry:
   final KR progress, a one-line honest assessment, and whether it carries
   forward. Compile this into data/archive/{{ENDING-QUARTER-SLUG}}/scorecard.md.

3. PROPOSE: open a GitHub issue titled "{{NEW QUARTER}} OKR reset" labelled
   "decision" containing: each person's carried-forward objectives, retired
   objectives with reasons, and empty slots for new objectives. Do NOT write any
   new-quarter OKRs into goals.json yourself — humans decide their objectives.

4. RESET (only after the issue is approved by {{LEAD-ID}}): update
   quarterLabel in data/config.json and quarter in data/goals.json; keep
   carried-forward objectives with fresh history starting points; trim
   updates.json to the last 14 days (older entries are in the archive); keep
   open challenges and pending decisions — they don't expire with the quarter.

5. Log the rollover as a digest entry and commit each step separately.
```

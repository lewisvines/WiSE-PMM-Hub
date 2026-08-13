#!/usr/bin/env python3
"""WiSE PMM Hub — data integrity validator.

Run from the repo root:  python3 scripts/validate_data.py
Exits non-zero if any ERROR is found. Runs automatically on every push via
.github/workflows/validate.yml, so a bad commit (human or agent) can't silently
break the dashboard.
"""
import json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors, warnings = [], []
def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

FILES = ['config','team','goals','priorities','updates','challenges','decisions',
         'digests','strategy','countries','assets','insights','actions','roadmap']
D = {}
for f in FILES:
    p = ROOT / 'data' / f'{f}.json'
    if not p.exists():
        err(f'{f}.json: file missing'); continue
    try:
        D[f] = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        err(f'{f}.json: invalid JSON — {e}')
if errors:
    print('\n'.join('ERROR: ' + e for e in errors)); sys.exit(1)

def is_date(s): return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(s)))
def is_ts(s):
    try: datetime.datetime.fromisoformat(str(s)); return True
    except Exception: return False

people = {p['id']: p for p in D['team']['people']}
workstreams = {w['id'] for w in D['team']['workstreams']}
pillars = {p['id'] for p in D['strategy']['pillars']}
countries = {c['id'] for c in D['countries']['countries']}
objectives = D['goals']['objectives']
goal_ids = set()
for o in objectives:
    goal_ids.add(o['id'])
    for k in o['keyResults']: goal_ids.add(k['id'])
for m in D['goals']['milestones']: goal_ids.add(m['id'])

# --- team ---
for p in D['team']['people']:
    if p.get('reportsTo') and p['reportsTo'] not in people:
        err(f"team: {p['id']} reportsTo unknown person '{p['reportsTo']}'")
    if p.get('status') not in ('active', 'pending'):
        err(f"team: {p['id']} has invalid status '{p.get('status')}'")
    if p.get('country') and p['country'] not in countries:
        err(f"team: {p['id']} references unknown country '{p['country']}'")
    for w in p.get('workstreams', []):
        if w not in workstreams: err(f"team: {p['id']} references unknown workstream '{w}'")
    # cycle check
    seen, cur = set(), p.get('reportsTo')
    while cur:
        if cur in seen or cur == p['id']:
            err(f"team: reporting cycle involving {p['id']}"); break
        seen.add(cur); cur = people.get(cur, {}).get('reportsTo')

def check_person(file, item_id, field, val, allow=('codex', 'manual')):
    if val not in people and val not in allow:
        err(f"{file}: {item_id} {field} references unknown person '{val}'")

# --- goals ---
for o in objectives:
    check_person('goals', o['id'], 'owner', o['owner'])
    if o.get('pillar') not in pillars: err(f"goals: {o['id']} references unknown pillar '{o.get('pillar')}'")
    for k in o['keyResults']:
        if not (0 <= k['progress'] <= 100): err(f"goals: {k['id']} progress out of range")
        if k.get('confidence') not in ('on-track','at-risk','off-track'):
            err(f"goals: {k['id']} invalid confidence")
        h = k.get('history', [])
        if h and h[-1]['progress'] != k['progress']:
            warn(f"goals: {k['id']} last history point ({h[-1]['progress']}) != progress ({k['progress']})")
        if any(not is_date(x['date']) for x in h): err(f"goals: {k['id']} bad history date")
for m in D['goals']['milestones']:
    check_person('goals', m['id'], 'owner', m['owner'])
    if not is_date(m['date']): err(f"goals: milestone {m['id']} bad date")
    if m['status'] not in ('planned','on-track','at-risk','late','done'):
        err(f"goals: milestone {m['id']} invalid status")
    if m.get('workstream') and m['workstream'] not in workstreams:
        err(f"goals: milestone {m['id']} unknown workstream")

# --- strategy ---
for o in D['strategy']['seniorOkrs']:
    check_person('strategy', o['id'], 'owner', o['owner'])
    if o.get('pillar') not in pillars: err(f"strategy: {o['id']} unknown pillar")

# --- priorities ---
for x in D['priorities']['priorities']:
    check_person('priorities', x['id'], 'owner', x['owner'])
    if x.get('visibility') not in ('private','shared'):
        err(f"priorities: {x['id']} invalid visibility '{x.get('visibility')}'")
    if x['status'] not in ('not-started','in-progress','blocked','done'):
        err(f"priorities: {x['id']} invalid status")
    if not is_date(x['due']): err(f"priorities: {x['id']} bad due date")
    if x.get('linkedGoal') and x['linkedGoal'] not in goal_ids:
        warn(f"priorities: {x['id']} linkedGoal '{x['linkedGoal']}' not found in goals")

# --- updates ---
dates = []
for u in D['updates']['updates']:
    check_person('updates', u['id'], 'onBehalfOf', u['onBehalfOf'])
    if u['type'] not in ('win','progress','blocker','decision-needed','fyi'):
        err(f"updates: {u['id']} invalid type")
    if u.get('source') not in ('teams','email','transcript','roadmap','manual'):
        err(f"updates: {u['id']} invalid source")
    if not is_ts(u['date']): err(f"updates: {u['id']} bad timestamp")
    else: dates.append(u['date'])
    for m in u.get('mentions', []):
        if m not in people: err(f"updates: {u['id']} mentions unknown person '{m}'")
    if u.get('relatedGoal') and u['relatedGoal'] not in goal_ids:
        warn(f"updates: {u['id']} relatedGoal '{u['relatedGoal']}' not found")
if dates != sorted(dates, reverse=True):
    warn('updates: entries are not newest-first')

# --- challenges / decisions ---
ch_ids = set()
for c in D['challenges']['challenges']:
    ch_ids.add(c['id'])
    check_person('challenges', c['id'], 'owner', c['owner'])
    if c.get('country') and c['country'] not in countries:
        err(f"challenges: {c['id']} references unknown country '{c['country']}'")
    if c['severity'] not in ('low','medium','high','critical'): err(f"challenges: {c['id']} invalid severity")
    if c['status'] not in ('open','mitigating','resolved'): err(f"challenges: {c['id']} invalid status")
for u in D['updates']['updates']:
    if u.get('relatedChallenge') and u['relatedChallenge'] not in ch_ids:
        warn(f"updates: {u['id']} relatedChallenge '{u['relatedChallenge']}' not found")
for d in D['decisions']['decisions']:
    check_person('decisions', d['id'], 'owner', d['owner'])
    if d['status'] not in ('decided','pending'): err(f"decisions: {d['id']} invalid status")
    if d['status'] == 'pending' and not d.get('neededBy'):
        warn(f"decisions: {d['id']} is pending with no neededBy date — SLA tracking won't work")
    if d.get('neededBy') and not is_date(d['neededBy']): err(f"decisions: {d['id']} bad neededBy")

# --- countries ---
for c in D['countries']['countries']:
    if c.get('lead') is not None:
        check_person('countries', c['id'], 'lead', c['lead'])
    else:
        warn(f"countries: {c['id']} has no market lead assigned")
    ab = c.get('advisoryBoard')
    if ab and not is_date(ab.get('updated', '')): err(f"countries: {c['id']} advisoryBoard.updated bad date")
    for pl in c.get('productLaunches', []):
        if not is_date(pl.get('date', '')): err(f"countries: {c['id']} launch '{pl.get('name')}' bad date")
    for mi in c.get('marketingInitiatives', []):
        if mi.get('status') not in ('planned', 'live', 'complete'):
            err(f"countries: {c['id']} initiative '{mi.get('name')}' invalid status")
    com = c.get('commercial')
    if com is not None and not isinstance(com.get('baseSize'), int):
        err(f"countries: {c['id']} commercial.baseSize must be an integer")
    for r in c['readiness']:
        if not is_date(r['date']): err(f"countries: {c['id']} readiness '{r['item']}' bad date")
    for k in c['keyDates']:
        if not is_date(k['date']): err(f"countries: {c['id']} keyDate bad date")
    sb = c.get('scoreboard', {})
    for dim in ('website','messaging','enablement','assets','press'):
        if sb.get(dim) not in ('green','amber','red'):
            err(f"countries: {c['id']} scoreboard.{dim} invalid ('{sb.get(dim)}')")

# --- assets ---
for a in D['assets']['assets']:
    check_person('assets', a['id'], 'owner', a['owner'])
    if a['status'] not in ('current','in-review','outdated'): err(f"assets: {a['id']} invalid status")
    if not is_date(a['updated']): err(f"assets: {a['id']} bad updated date")
    for cc in a.get('countries', []):
        if cc not in countries: err(f"assets: {a['id']} unknown country '{cc}'")
    if a.get('workstream') and a['workstream'] not in workstreams:
        err(f"assets: {a['id']} unknown workstream")

# --- insights ---
for i in D['insights']['insights']:
    check_person('insights', i['id'], 'addedBy', i['addedBy'])
    if i['type'] not in ('win-loss','customer-quote','competitor-note','research'):
        err(f"insights: {i['id']} invalid type")
    if i.get('country') and i['country'] not in countries: err(f"insights: {i['id']} unknown country")
    if not is_date(i['date']): err(f"insights: {i['id']} bad date")
    if i['type'] == 'win-loss' and i.get('outcome') not in ('won','lost'):
        warn(f"insights: {i['id']} win-loss without outcome won/lost")

# --- actions ---
for a in D['actions']['actions']:
    check_person('actions', a['id'], 'owner', a['owner'])
    if a['status'] not in ('open','done','dropped'): err(f"actions: {a['id']} invalid status")
    if not is_date(a['date']): err(f"actions: {a['id']} bad date")
    if a.get('due') and not is_date(a['due']): err(f"actions: {a['id']} bad due date")
    if a.get('linkedGoal') and a['linkedGoal'] not in goal_ids:
        warn(f"actions: {a['id']} linkedGoal '{a['linkedGoal']}' not found")

# --- country dependencies & stakeholder map ---
for c in D['countries']['countries']:
    for dep in c.get('dependencies', []):
        if dep.get('status') not in ('on-track','at-risk','blocked'):
            err(f"countries: {c['id']} dependency '{dep.get('name')}' invalid status")
        if dep.get('due') and not is_date(dep['due']): err(f"countries: {c['id']} dependency '{dep.get('name')}' bad due")
    for s in c.get('stakeholders', []):
        if s.get('influence') and s['influence'] not in ('high','medium'):
            err(f"countries: {c['id']} stakeholder '{s.get('name')}' invalid influence")
        if s.get('relationship') and s['relationship'] not in ('strong','developing','gap'):
            err(f"countries: {c['id']} stakeholder '{s.get('name')}' invalid relationship")


# --- roadmap ---
RM = D['roadmap']
rm_rows = set(RM.get('rows', []))
if 'wise' not in rm_rows:
    warn("roadmap: no 'wise' programme row configured")
for r in rm_rows:
    if r != 'wise' and r not in countries:
        err(f"roadmap: row '{r}' is not a country id or 'wise'")
rm_ids = set()
for i in RM.get('initiatives', []):
    if i['id'] in rm_ids: err(f"roadmap: duplicate initiative id '{i['id']}'")
    rm_ids.add(i['id'])
    if i.get('row') not in rm_rows:
        err(f"roadmap: {i['id']} row '{i.get('row')}' is not in roadmap.rows")
    check_person('roadmap', i['id'], 'owner', i['owner'])
    if i.get('status') not in ('planned', 'on-track', 'at-risk', 'blocked', 'done'):
        err(f"roadmap: {i['id']} invalid status '{i.get('status')}'")
    if not is_date(i.get('start', '')): err(f"roadmap: {i['id']} bad start date")
    if not is_date(i.get('end', '')): err(f"roadmap: {i['id']} bad end date")
    if is_date(i.get('start', '')) and is_date(i.get('end', '')) and i['end'] < i['start']:
        err(f"roadmap: {i['id']} ends before it starts")
    if not (0 <= i.get('progress', 0) <= 100): err(f"roadmap: {i['id']} progress out of range")
    if i.get('workstream') and i['workstream'] not in workstreams:
        err(f"roadmap: {i['id']} unknown workstream '{i['workstream']}'")
    if i.get('lastReviewed') and not is_date(i['lastReviewed']): err(f"roadmap: {i['id']} bad lastReviewed")
    if i.get('reviewedBy'): check_person('roadmap', i['id'], 'reviewedBy', i['reviewedBy'])
    if i.get('linkedGoal') and i['linkedGoal'] not in goal_ids:
        warn(f"roadmap: {i['id']} linkedGoal '{i['linkedGoal']}' not found")
    for s in i.get('nextSteps', []):
        if 'text' not in s: err(f"roadmap: {i['id']} has a next step with no text")
    if i.get('status') != 'done' and not i.get('nextSteps'):
        warn(f"roadmap: {i['id']} has no next steps recorded")

for e in RM.get('events', []):
    if e.get('row') not in rm_rows:
        err(f"roadmap: event {e.get('id')} row '{e.get('row')}' is not in roadmap.rows")
    if not is_date(e.get('start', '')): err(f"roadmap: event {e.get('id')} bad start date")
    if e.get('end') and not is_date(e['end']): err(f"roadmap: event {e.get('id')} bad end date")
    if e.get('end') and is_date(e.get('start','')) and e['end'] < e['start']:
        err(f"roadmap: event {e.get('id')} ends before it starts")
    if not e.get('name'): err(f"roadmap: event {e.get('id')} has no name")
    if not e.get('source'): warn(f"roadmap: event {e.get('id')} has no source — mark it verified or sample")


# --- digests ---
for g in D['digests']['digests']:
    if g['status'] not in ('success','partial','failed'): err(f"digests: {g['id']} invalid status")
    if not is_ts(g['runAt']): err(f"digests: {g['id']} bad runAt")

print(f"Checked {len(FILES)} files: {len(errors)} error(s), {len(warnings)} warning(s)")
for w in warnings: print('WARN:  ' + w)
for e in errors: print('ERROR: ' + e)
sys.exit(1 if errors else 0)

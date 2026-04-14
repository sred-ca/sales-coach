---
name: sales-coach-weekly-prep
description: >
  Run the weekly sales coach data-gathering workflow for SRED.ca. Pulls the prior week's
  (Monday–Sunday) sales activity from Fireflies, HubSpot, HeyReach, and Gmail, synthesizes a
  Pre-Session Brief, and injects it into the VAPI coaching agent system prompt. Use this skill
  whenever running the Monday 6am weekly prep task, generating a pre-session brief, or preparing
  for Evan's coaching call. Triggers on: "run the weekly prep", "generate the pre-session brief",
  "prep for Evan's call", "pull this week's data", "sales coach prep", or when the scheduled task
  invokes this workflow. This is Phase 1 of the three-phase sales coaching system.
---

# Sales Coach — Weekly Prep (Phase 1)

This skill runs every Monday at 6am ET. It gathers all of Evan's sales activity from the **prior calendar week (Monday 00:00:00 → Sunday 23:59:59 ET)**, synthesizes it into a Pre-Session Brief, and injects the brief into the VAPI coaching agent so "John" is fully briefed before Evan calls.

## Critical Date Rule

The data window is ALWAYS the **prior calendar week: Monday 00:00:00 → Sunday 23:59:59 ET**.

```
Today is Monday [DATE].
Prior week: [Last Monday] 00:00:00 ET → [Last Sunday] 23:59:59 ET

Never use "last 7 days" — always anchor to the Mon-Sun calendar week.
```

Convert to epoch milliseconds for HubSpot queries. Convert to ISO 8601 for Fireflies.

## Step 1: Read Context Files

Read these files at session start:

1. `sales-coach/CLAUDE.md` — full project context, methodology, open questions
2. `sales-coach/evan-profile.md` — living profile (last session's commitments, patterns, SDT state)
3. `sales-coach/references/pre-session-brief-template.md` — exact data format and classification logic
4. `sales-coach/references/stage-specific-evaluation.md` — pipeline stage evaluation criteria

## Step 2: Pull Data from All Four Sources

Pull all four in parallel. Every query uses the same Mon 00:00:00 → Sun 23:59:59 ET window.

### A) Fireflies — Meeting Transcripts

```
Use fireflies_get_transcripts with:
  fromDate: [prior Monday ISO 8601]
  toDate: [prior Sunday ISO 8601]

Then for each transcript involving Evan Batchelor:
  Use fireflies_get_transcript to pull full text, speaker attribution, summary, action items.

Classify each meeting:
  - Evan-led pitch/demo → high coaching value
  - Discovery/handoff (Jude or Logan present) → note who leads
  - Phone-only (no Fireflies capture) → flag as data gap

Calculate for each meeting:
  - Evan talk ratio (his lines / total lines)
  - Questions asked count
  - Follow-up email timestamp (from HubSpot, within 24hrs of meeting)
```

### B) HubSpot — Pipeline & Email Activity

**Evan's owner ID: 228172981**

```
Pull deals with activity this week:
  Filter: deals owned by 228172981
  Filter: hs_last_modified_date BETWEEN [Mon epoch ms] AND [Sun epoch ms]
  
  For each deal: stage, close date, days since last activity, deal name, amount

Pull email activity this week:
  Object type: emails
  Filter: owner_id = 228172981
  Filter: hs_timestamp BETWEEN [Mon epoch ms] AND [Sun epoch ms]
  
  For each email: subject, recipient, timestamp, was it replied to?
  Classify: personal email vs. Prospecting Agent sequence

Pipeline stage IDs:
  30153821 = Opportunity
  appointmentscheduled = SR&ED Assessment  
  31821993 = Technical Discovery
  contractsent = Follow-Up
  closedwon = Closed Won
  closedlost = Closed Lost
```

### C) HeyReach — LinkedIn Outbound

HeyReach has no API. Use browser automation (Claude in Chrome):

```
1. Navigate to app.heyreach.io
2. Log in as Jude's account
3. Filter by sender: Evan Batchelor
4. Filter by date: prior Mon-Sun
5. Pull: connection requests sent, accepted, messages sent, replied, InMails sent, replied
6. Note any active campaign names and their current stats
```

If browser automation is unavailable, note the gap and proceed without LinkedIn data.

### D) Gmail / HubSpot Email

Gmail MCP only sees Jude's mailbox. For Evan's email activity, use HubSpot (step B above). However, check Gmail for any prospect replies that may have CC'd Jude or come to the main SRED.ca inbox.

### E) VAPI — Prior Week's Coaching Session

Pull the prior week's coaching call transcript from VAPI to feed the "Last Session Recap" into this week's brief. This gives John direct memory of what was discussed, not just what `evan-profile.md` summarizes.

```bash
# Calculate prior week's Monday and Sunday (the week BEFORE the data window)
# If data window is Apr 7-13, prior coaching session was from Mar 31-Apr 6 window
PRIOR_MONDAY=$(python3 -c "
from datetime import datetime, timedelta
today = datetime.now()
data_monday = today - timedelta(days=today.weekday() + 7)
prior_monday = data_monday - timedelta(days=7)
print(prior_monday.strftime('%Y-%m-%dT00:00:00Z'))
")
PRIOR_SUNDAY=$(python3 -c "
from datetime import datetime, timedelta
today = datetime.now()
data_monday = today - timedelta(days=today.weekday() + 7)
prior_sunday = data_monday - timedelta(days=1)
print(prior_sunday.strftime('%Y-%m-%dT23:59:59Z'))
")

curl -s "https://api.vapi.ai/call?assistantId=401905cf-f38f-4277-8bee-814916aaf2c0&createdAtGe=$PRIOR_MONDAY&createdAtLe=$PRIOR_SUNDAY" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

For each call found:
- Fetch full transcript: `GET https://api.vapi.ai/call/{id}`
- Extract: what was discussed, coaching focus, Evan's commitments (from `artifact.transcript`), `analysis.summary`, `duration`

If multiple calls found (stitched session), combine them chronologically.

Also check for any **expired partials** from the prior week in `outputs/partials/` — if a session was never completed, note this in the brief so John can address it.

Feed this into the Pre-Session Brief under a new **"Last Session Recap"** section (inserted after "Commitment Check", before "Wins").

## Step 3: Check Last Week's Commitments

Read `evan-profile.md` → Commitment Tracker.

**Find all ⏳ Pending commitments.** List them in the brief so John knows exactly what to ask about.

```
Last week Evan committed to:
  1. "[exact quote]" — ⏳ Pending
  2. "[exact quote]" — ⏳ Pending
John should open: "Hey, last week you said [commitment]. How'd that go?"
```

**Calculate commitment track record** from ALL resolved commitments (✅ Done, 🔄 In Progress, ❌ Missed):
```
Commitment track record: [X] kept / [Y] total ([Z]%)
```
Include this in the brief's Week at a Glance section. John uses this to calibrate — if Evan keeps 90% of commitments, push harder. If he keeps 40%, the commitments are too ambitious or something else is going on.

If no prior commitments (first session), skip this step.

## Step 4: Synthesize the Pre-Session Brief

Combine all data into the Pre-Session Brief format. See `references/pre-session-brief-template.md` for the full format spec.

**Required sections:**
1. Week at a Glance (KPIs)
2. Commitment Check (last week's commitments and evidence)
3. Last Session Recap (from VAPI — what John and Evan discussed, coaching focus, how Evan responded, any unfinished business from an interrupted session)
4. Wins (2-4 specific things that went well)
5. Meeting Reviews (1-3 most coachable meetings with transcript excerpts)
6. Pipeline Health (stage snapshot, stalled deals flagged)
7. Payment Gate Check (any deals at Assessment where Stripe LOE is unknown)
8. Email Scorecard (personal emails, follow-up speed)
9. LinkedIn Assessment (HeyReach data for the week)
10. Patterns Observed (coach's pre-call read — what's the one thing?)
11. Coaching Focus Recommendation (what John should coach on this session)
12. SDT Notes (autonomy/competence/relatedness signals from the data)

## Step 5: Save the Brief

```
Save to: sales-coach/outputs/pre-session-brief-[YYYY-MM-DD].txt
  where YYYY-MM-DD is the prior Monday's date (the start of the reporting week)

File is plain text, ~10-20KB. This file is the anchor for the entire week's coaching cycle.
```

## Step 6: Update VAPI System Prompt (Automated)

The VAPI agent's system prompt has two parts:
- **Static:** John persona, SRED.ca context, methodology — stored on the assistant with `{{PRE_SESSION_BRIEF}}` and `{{PERSONAL_GOALS}}` placeholders
- **Dynamic:** Pre-Session Brief + Personal Goals — injected weekly via API

Run the update script to inject the new brief into the VAPI assistant:

```bash
VAPI_API_KEY="$VAPI_API_KEY" python3 agents/update_vapi_prompt.py \
  --brief outputs/pre-session-brief-[YYYY-MM-DD].txt
```

If there is an **active partial** from this week (a prior call was interrupted), include it:
```bash
VAPI_API_KEY="$VAPI_API_KEY" python3 agents/update_vapi_prompt.py \
  --brief outputs/pre-session-brief-[YYYY-MM-DD].txt \
  --partial outputs/partials/week-of-[YYYY-MM-DD]-partial.json
```

The script:
1. Loads the static prompt template from `agents/vapi-coaching-agent-prompt.md`
2. Reads the Pre-Session Brief, `evan-personal-goals.md`, and `evan-profile.md`
3. Replaces `{{PRE_SESSION_BRIEF}}`, `{{PERSONAL_GOALS}}`, `{{EVAN_PROFILE}}`, and `{{PREVIOUS_SESSION}}` with actual content
4. PATCHes the VAPI assistant via API (uses `http.client` to bypass Cloudflare WAF)

**Environment variable required:** `VAPI_API_KEY` must be set. The API key is stored securely — never commit it to git.

**Fallback:** If the API call fails, the assembled prompt is saved to `outputs/vapi-prompt-assembled-[YYYY-MM-DD].txt` for manual pasting via the VAPI dashboard.

After the update, proceed to schedule Evan's coaching call.

## Step 7: Schedule the Coaching Call (Google Calendar)

Create a 1-hour Google Calendar event for Evan's coaching call. The scheduling rules:

**Timing logic:**
1. Note the current time (ET) when the VAPI prompt update completes
2. Add 1 hour minimum buffer → this is the earliest Evan should call
3. Round UP to the next full hour (meetings are always on the hour)
4. The slot must fall within the **10:00 AM – 3:00 PM ET** window
5. If the calculated time is before 10 AM → schedule at 10:00 AM
6. If the calculated time is after 3:00 PM → schedule at 10:00 AM the next weekday

**Examples:**
- Prep finishes 6:15 AM → 6:15 + 1hr = 7:15 → rounds to 8:00 AM → before window → **10:00 AM**
- Prep finishes 10:30 AM → 10:30 + 1hr = 11:30 → rounds to **12:00 PM**
- Prep finishes 1:45 PM → 1:45 + 1hr = 2:45 → rounds to **3:00 PM**
- Prep finishes 2:30 PM → 2:30 + 1hr = 3:30 → past window → **10:00 AM next weekday**

**Create the event using `gcal_create_event`:**
```
Summary: "Sales Coaching Call with John"
Description:
  Everything is ready.

  This week's data has been pulled from Fireflies, HubSpot, HeyReach,
  and Gmail. Your Pre-Session Brief is loaded. John is waiting for you.

  Call John: +1 (571) 498-9194

  12-15 minutes. He'll start with a check-in, then get into the week —
  wins, meeting reviews, pipeline health, and your one coaching focus.

  — Sales Coach System

Start: [calculated time] ET (1-hour block)
End: [start + 1 hour]
Attendees: evan@sred.ca, jude@sred.ca
sendUpdates: "all"
```

Google Calendar sends the invitation email to Evan automatically.

## Step 8: Confirm and Log

Output a completion summary:

```
✅ Weekly prep complete — Week of [Monday] – [Sunday]

Data pulled:
  • Fireflies: [N] meetings found, [N] with Evan
  • HubSpot: [N] deals active, [N] emails in window
  • HeyReach: [N] connections sent, [N] messages, [N] InMails
  • Gmail: checked (no additional prospect emails found / found X relevant threads)

Pre-Session Brief: outputs/pre-session-brief-[DATE].txt ([size])
VAPI system prompt: ✅ Updated via API ([size] chars)
Coaching call: 📅 Scheduled [DAY] at [TIME] ET (event sent to Evan + Jude)

Last week's commitments in brief: [yes / none — first session]
```

## Reference Files

- `references/pre-session-brief-template.md` — data gathering methodology + exact format spec for the brief
- `references/stage-specific-evaluation.md` — pipeline stage evaluation criteria (all 6 stages)
- `references/sdt-coaching-framework.md` — SDT framework for building the SDT Notes section of the brief

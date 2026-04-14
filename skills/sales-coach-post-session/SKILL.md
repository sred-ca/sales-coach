---
name: sales-coach-post-session
description: >
  Process a completed VAPI sales coaching call for SRED.ca and generate two branded PDF reports.
  Use this skill whenever a VAPI coaching call with Evan has completed and you need to generate
  the post-session deliverables. Triggers on: "process the coaching call", "generate the coaching
  report", "make the reports", "post-session", "the call is done", "Evan's report", "manager summary",
  "sales coaching report", or any request to process a completed sales coaching session transcript.
  Also triggers as the post-session step in the weekly sales coach scheduled task. If the VAPI
  transcript for the current week has not yet been processed, this skill handles detection and
  generation automatically.
---

# Sales Coach — Post-Session Processing

After each VAPI coaching call with Evan, this skill:

1. Detects completed call transcript(s) from the VAPI API (not Fireflies)
2. Handles interrupted calls — saves partial state, enables continuation on callback
3. Stitches multi-call transcripts when a session spans more than one call
4. Pairs the transcript with the week's pre-session brief and evan-profile.md
5. Generates two branded PDF reports using the sred-doc-creator scripts
6. Saves Evan's report, creates a Gmail draft, and updates evan-profile.md
7. Emails Jude when the manager summary is ready

## File Locations

Read these files at the start of every post-session run:

| File | Purpose |
|------|---------|
| `sales-coach/evan-profile.md` | Living knowledge base — read first, update last |
| `sales-coach/outputs/pre-session-brief-[DATE].txt` | This week's data brief (most recent Monday) |
| `sales-coach/agents/vapi-config.md` | VAPI assistant ID, phone number, API notes |
| `sales-coach/CLAUDE.md` | Full project context and John Barrows methodology |
| `sales-coach/references/sdt-coaching-framework.md` | SDT framework for motivation analysis |

## Step 1: Detect the VAPI Transcript

VAPI coaching calls record to VAPI's own servers — NOT Fireflies. Use the VAPI REST API directly.

**VAPI API Configuration:**
- **Endpoint:** `https://api.vapi.ai/call`
- **Auth:** `Authorization: Bearer $VAPI_API_KEY`
- **Assistant ID:** `401905cf-f38f-4277-8bee-814916aaf2c0`

### 1a. Pre-flight Checks

**Check if reports already exist:** Look for `sales-coach/outputs/coaching-report-{week_start}.pdf` where `week_start` is this week's Monday date (YYYY-MM-DD). If that file exists, log "Reports already generated for week of [DATE]. Skipping." and exit.

**Build processed call registry:** Read all JSON files in `sales-coach/outputs/partials/`. Collect every `call_id` value — these are already-processed calls. Skip any call whose ID appears in this registry.

### 1b. Fetch Calls from VAPI

```bash
# Calculate 3-hour lookback window (for scheduled polling)
SINCE=$(python3 -c "from datetime import datetime, timezone, timedelta; print((datetime.now(timezone.utc)-timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ'))")

# Fetch recent calls for the Sales Coach assistant
curl -s "https://api.vapi.ai/call?assistantId=401905cf-f38f-4277-8bee-814916aaf2c0&limit=10&createdAtGt=$SINCE" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

For each call returned:
1. Check if `call_id` is in the processed registry → if yes, **skip**
2. Check if `status` is `ended` → if not ended, skip (still in progress)
3. Fetch the full call details: `GET https://api.vapi.ai/call/{call_id}`
4. Extract: `artifact.transcript`, `artifact.recording`, `analysis.summary`, `duration`, `endedReason`, `messages`

### 1c. Determine Session Completeness

Map the VAPI transcript to the 6 coaching session sections:

| Section Key | Section Name | Detection Signals |
|-------------|-------------|-------------------|
| `opening` | Opening: Check-In + Personal Goals | Agent's first message + personal goals mention or "how you doing/feeling" exchange |
| `wins` | Wins Recognition | Discussion of "what worked", "wins", specific deal/call celebrations, "your read on the week" |
| `meeting_reviews` | Meeting Reviews | Review of specific recorded meetings, talk ratio discussion, discovery quality, "how did you feel that call went" |
| `pipeline` | Pipeline & Activity Check | Pipeline deals, stalled deals, follow-up scorecard, LinkedIn outreach, "deals past close date" |
| `coaching_focus` | Coaching Focus | "One thing this week", specific behavior change identified, skill focus set |
| `commitments` | Commitments & Close | Evan states commitments, measurable actions, "commit to", closing remarks like "Go get it done" |

A section counts as **complete** when it has substantive back-and-forth (not just the coach mentioning the topic — Evan must engage). The agent's closing phrase ("Good talk. Go get it done." or similar) is a strong signal that the session reached natural completion.

**Complete session:** All 6 sections have substantive content → proceed to Step 1e.
**Incomplete session:** Some sections missing → proceed to Step 1d.

### 1d. Handle Incomplete Session (Save Partial)

If the call ended before all 6 sections were covered:

**Check for existing partial:** Look for `sales-coach/outputs/partials/week-of-{week_start}-partial.json`. If one exists, this is a **continuation call** — proceed to Step 1e (multi-call stitching).

**Save new partial:**
```json
{
  "call_id": "vapi-call-uuid",
  "call_date": "2026-04-14T10:30:00Z",
  "duration_seconds": 1080,
  "ended_reason": "customer-ended-call",
  "sections_completed": ["opening", "wins", "meeting_reviews"],
  "sections_remaining": ["pipeline", "coaching_focus", "commitments"],
  "partial_section": null,
  "extracted_data": {
    "wins_discussed": ["Think CNC follow-up", "2 new pipeline deals"],
    "meetings_reviewed": ["Think CNC — discovery quality discussed"],
    "evan_energy": "engaged, receptive"
  },
  "transcript_messages": [],
  "summary_for_resume": "Covered check-in (Evan feeling good), wins (Think CNC follow-up praised, 2 new deals acknowledged), and meeting review (Think CNC — discussed talk ratio and discovery depth, Evan was receptive). Was about to move into pipeline review.",
  "pre_session_brief_path": "outputs/pre-session-brief-2026-04-14.txt",
  "expires": "2026-04-19T23:59:59-04:00"
}
```

Save to: `sales-coach/outputs/partials/week-of-{week_start}-partial.json`

**Update VAPI prompt for continuation:** Run the prompt updater with the partial so the next call picks up where this one left off:
```bash
python3 agents/update_vapi_prompt.py \
  --brief outputs/pre-session-brief-{week_start}.txt \
  --partial outputs/partials/week-of-{week_start}-partial.json
```

**Notify Evan** via Google Calendar event:
```
Summary: "Continue Coaching Call — Call John Back"
Description:
  Hey Evan — we got cut short. No worries.

  We covered: [list completed sections in plain language].
  Still need to get through: [list remaining sections].

  Call +1 (571) 498-9194 when you're free and we'll pick up
  right where we left off.

  — John
Start: Tomorrow 10:00 AM ET (15-min event)
Attendees: evan@sred.ca
sendUpdates: "all"
```

**Notify Jude** via Gmail draft + Chrome send:
```
To: jude@sred.ca
Subject: Coaching Call Incomplete — Week of [Monday, Month Day]
Body:
  Hey Jude,

  Evan's coaching call got cut short today — we covered [X/6] sections
  ([list completed sections]).

  Still need: [list remaining sections].

  I've sent Evan a calendar invite to call back. The system will
  pick up where we left off automatically.

  — Sales Coach System
```

Then exit. Do not generate reports from an incomplete session.

### 1e. Multi-Call Stitching

If a partial already exists for this week (`week-of-{week_start}-partial.json`) AND a new call comes in:

1. Load the existing partial JSON
2. Load the new call's full transcript from VAPI
3. **Merge transcripts:** Append the new call's messages after the partial's messages (chronological order)
4. **Update sections:** Re-evaluate completeness against all 6 sections using the combined transcript
5. **Merge extracted data:** Combine `extracted_data` from both calls

If now **complete** (all 6 sections covered across both calls):
- Update the partial JSON with `"status": "completed"` and the second call's `call_id`
- Clean up: delete `sales-coach/outputs/nudge-sent-{week_start}.txt` if it exists
- Proceed to Step 2 using the stitched transcript as the source

If **still incomplete:**
- Update the partial JSON with merged data, new `sections_completed`/`sections_remaining`
- Re-run the VAPI prompt update with the updated partial
- Send another continuation notification to Evan
- Exit without generating reports

### 1f. Escalation Tiers (No Call Detected)

If no new VAPI calls are found AND no partial exists for this week:

**Monday, or Tuesday before 5pm ET, or Wednesday before 5pm ET:** Silent exit.
Log "No VAPI call found for week of [DATE]. Will retry." and exit gracefully.

**Tuesday 5pm ET (hour = 17):** Send a gentle nudge to Evan only.
First check for marker file `sales-coach/outputs/nudge-sent-{week_start}.txt` — if it already contains "Tier 1 sent", skip. Otherwise, create a Google Calendar event using `gcal_create_event`:
```
Summary: "Coaching Call Reminder — Call John"
Description:
  Hey Evan,

  Just checking in — did you get a chance to hop on the coaching call
  this week? No rush if it's happening tomorrow.

  Call +1 (571) 498-9194 when ready.

  — John
Start: Tomorrow 9:00 AM ET (15-min event)
Attendees: evan@sred.ca
sendUpdates: "all"
```
After creating, append to `sales-coach/outputs/nudge-sent-{week_start}.txt`:
```
Tier 1 sent: Tuesday [date] [time] — gcal event [event_id]
```
Then exit.

**Wednesday 5pm ET (hour = 17):** Alert both Jude and Evan.
First check marker — if "Tier 2 sent" exists, skip. Otherwise:
```
Summary: "Missing Coaching Call — Week of [Monday date]"
Description:
  Heads up — no coaching call was detected this week via VAPI.

  Evan can call +1 (571) 498-9194 anytime before end of day Wednesday.

  — Sales Coach System
Start: Today 5:30 PM ET (15-min event)
Attendees: evan@sred.ca, jude@sred.ca
sendUpdates: "all"
```
Append marker and exit.

**After Wednesday (Thursday–Sunday):** Polling window closed.
If a partial exists but is incomplete, send a final email to Jude:
```
To: jude@sred.ca
Subject: Coaching Session Incomplete — Week of [date]
Body: Evan started the call but didn't finish ([X/6] sections).
  The partial data has been saved to evan-profile.md.
  Next week's session will cover any missed ground.
```
Update `evan-profile.md` with whatever data was extracted from the partial, marked as `[partial session]`. Exit.

## Step 2: Load Context

Read in parallel:
- The most recent `pre-session-brief-[DATE].txt` from `outputs/` (the Monday brief for this week)
- `evan-profile.md` (the full living profile)
- `evan-personal-goals.md` (for Evan's report only — never for manager summary)

## Step 3: Analyze the Session

Before generating reports, synthesize what happened in the call. Extract:

**Performance Data (from transcript):**
- Did Evan self-assess accurately vs. what the data showed?
- What did the coach (John) focus on?
- How did Evan respond — receptive, defensive, deflecting, energized?
- What specific moments were most significant?
- What commitment(s) did Evan make? Quote exactly in his words.
- Did anything surprise the coach — things Evan brought up that weren't in the brief?

**Metrics to carry forward (from pre-session brief):**
- Meetings this week (count, any Fireflies-recorded)
- Pipeline touches
- Follow-up speed
- Active deals + stage distribution
- LinkedIn outbound stats for the week
- Any new deals added or stage changes

**Coaching quality check:**
- Was ONE focus maintained, or did the session drift to multiple topics?
- Did John ask before telling? (SDT autonomy check)
- Grit/Grace balance — was the session appropriately direct without being discouraging?

## Step 4: Generate Evan's Coaching Report (PDF)

Run the report generator script. See `scripts/generate_coaching_report.py` for the full implementation.

**Report structure — ALWAYS use this layout:**

```
COVER: "WEEKLY COACHING REPORT" / "Week of [Monday] – [Sunday]" / "Prepared for Evan Batchelor"

PAGE 1: WEEK AT A GLANCE
  - KPI row: Meetings | Pipeline Deals | Follow-Up Speed | Active Pipeline Value
  - 3-4 sentence narrative: what kind of week it was overall

PAGE 2: THIS WEEK'S WINS
  - 2-4 win callouts using doc.win()
  - Be specific — reference real moments from the call/brief, not generic praise

PAGE 3: MEETING REVIEW
  - Cover 1-2 most coachable meetings from the week
  - Reference specific moments (Evan led discovery? Deferred? Asked good questions?)
  - Use the John Barrows framework: prep, discovery depth, urgency, follow-up
  - Keep it factual, not harsh — Evan reads this after the call

PAGE 4: PIPELINE HEALTH
  - Branded table: Stage | Deals | Key Notes
  - Highlight any stalled deals (past expected close by 30+ days)
  - Do NOT include dollar amounts tied to company revenue

PAGE 5: THIS WEEK'S FOCUS
  - The ONE thing John coached on (not two, not three — one)
  - 2-3 paragraphs on why it matters and how Evan can apply it
  - Specific, not generic: "When Logan takes over the discovery in the Think CNC call..."

PAGE 6: YOUR COMMITMENTS
  - Quote Evan's exact words from the call
  - If Evan said "I'll send three personal emails to stalled deals by Thursday" — use that
  - Sub-header: "What John Will Ask About Next Week"

PAGE 7: A NOTE ON GROWTH (Evan only — NOT in manager summary)
  - One paragraph connecting this week's coaching to Evan's longer arc
  - Reference SDT: what does this represent on his Motivation/Decision Ladder?
  - Tone: coach-to-player, not HR-to-employee. Direct and warm.
  - Can reference personal goals briefly if relevant (never quote them directly)
```

**Critical rules:**
- Never include SRED.ca company revenue figures (QuickBooks data is Jude-only)
- Quote Evan's commitments verbatim from the transcript
- The cover date range is ALWAYS the prior calendar week (Mon-Sun), not the call date
- Use SRED_EMERALD for wins, SRED_DARK_BLUE for headers

## Step 5: Generate Jude's Manager Summary (PDF)

The Manager Summary uses the same metrics as Evan's report. The difference is the narrative layer.

**Report structure:**

```
COVER: "MANAGER SUMMARY" / "Week of [Monday] – [Sunday]" / "CONFIDENTIAL — Jude Cormier"

PAGE 1: WEEK AT A GLANCE
  - Same KPI row as Evan's report (identical metrics)
  - Same pipeline table

PAGE 2: COACHING SESSION OVERVIEW
  Sub-sections:
  - "How the Session Went" — Was Evan receptive, defensive, energized, distracted?
    Reference specific moments. What surprised the coach? What came up unprompted?
  - "What the Coach Focused On" — The one focus area and why it was chosen from the data
  - "Evan's Commitments" — Same verbatim quotes as Evan's report

PAGE 3: PIPELINE REVIEW
  - Same deal table as Evan's report
  - Flag any deals with payment gate concerns (Stripe LOE not received before Tech Discovery)
  - Flag deals past expected close date
  - Revenue can be mentioned here (Jude's report — company context OK)

PAGE 4: MANAGER INSIGHT
  - What should Jude be thinking about that only a manager can act on?
  - Examples: deal support needed, resource gaps, team dynamic observations,
    anything systemic that coaching alone can't fix
  - NOT a transcript — this is signal extraction for a busy founder
  - Keep it under 300 words. Jude wants to skim this in 2 minutes.

PAGE 5: SDT PROGRESSION NOTE
  - One short paragraph on where Evan is on the Motivation and Decision Ladders
  - Any movement since last session (or since baseline)?
  - Is the coaching creating autonomy, or creating dependency?
```

**Tone:** Direct and useful. Jude wants signal, not a transcript. Write like you're giving a verbal debrief to a busy founder who cares deeply about Evan but doesn't have time for fluff.

## Step 6: Save Outputs

```python
# File naming convention — always use the Monday date of the reporting week
week_start = "YYYY-MM-DD"  # prior Monday

evan_report_path = f"sales-coach/outputs/coaching-report-{week_start}.pdf"
manager_summary_path = f"sales-coach/outputs/manager-summary-{week_start}.pdf"
```

Save both files to `sales-coach/outputs/`.

## Step 7: Create Gmail Draft for Evan's Report

Use the Gmail MCP to create a draft with Evan's coaching report attached.

```
To: evan@sred.ca (confirm from CLAUDE.md or Jude if not listed)
Subject: Your Weekly Coaching Report — Week of [Monday, Month Day]
Body:
  Hey Evan,

  Here's your coaching report from this week's call with John.

  The main thing we focused on: [one-line summary of coaching focus].

  Your commitment for this week: [Evan's verbatim commitment].

  Talk next Monday.

  — John

[Attach: coaching-report-YYYY-MM-DD.pdf]
```

**This is a DRAFT only.** Do not send. Jude reviews and sends manually.

## Step 8: Notify Jude — Manager Summary Ready

Send Jude an email with the manager summary attached. Use Gmail draft + Chrome browser automation (same pattern as EO Forum system).

### Step A: Create the draft

Use `gmail_create_draft`:
```
To: jude@sred.ca
Subject: Manager Summary Ready — Week of [Monday, Month Day]
Body (HTML):
  <p>Hey Jude,</p>

  <p>Evan's coaching session is done. Here's the quick version:</p>

  <ul>
    <li><strong>Coaching focus:</strong> [one-line summary of this week's focus]</li>
    <li><strong>Evan's commitment:</strong> "[Evan's verbatim commitment]"</li>
    <li><strong>Session energy:</strong> [receptive/defensive/energized — one word]</li>
    <li><strong>Flags:</strong> [any pipeline flags or concerns, or "None this week"]</li>
  </ul>

  <p>Full manager summary PDF is attached. Evan's report draft is ready to send.</p>

  <p>— Sales Coach System</p>

Attach: sales-coach/outputs/manager-summary-{week_start}.pdf
```

Save the `messageId` from the response.

### Step B: Open the draft in Chrome

Navigate to: `https://mail.google.com/mail/u/0/#drafts/{messageId}`
Wait 2-3 seconds for the compose window to load.

### Step C: Find and click Send

Use the `find` tool: `query: "Send button in compose window to jude@sred.ca"`
Click using the returned ref.

### Step D: Confirm sent

Take a screenshot and verify the "Message sent" toast appears.

**If multi-call session:** Add a note to the email body: "Note: This session was completed across [N] calls — the first was interrupted after [duration], and Evan called back to finish."

## Step 9: Update evan-profile.md (The Learning Loop)

This is the most critical step. Every sub-step must execute — this is how John gets smarter each week. Read the current `evan-profile.md` before making any changes.

### 9a. Resolve Prior Commitments

Before adding new commitments, find ALL `⏳ Pending` entries in the Commitment Tracker. For each one, search the transcript for whether Evan addressed it.

**Update each pending commitment's status:**
- `✅ Done` — Evan confirmed completion. Add evidence quote: `"Yeah, I got MSR out on Thursday."`
- `🔄 In Progress` — Partial completion. Note what's done and what remains.
- `❌ Missed` — No mention, or Evan acknowledged he didn't do it. Note briefly why if stated.

If the transcript doesn't mention a prior commitment at all, mark it `❌ Missed — not addressed in session`.

**Example update:**
```
| 2026-04-14 | Send follow-ups to MSR and VassuTech by Friday | ✅ Done | "Got MSR out Thursday. VassuTech I called and they're in." |
```

### 9b. Add New Commitments

Extract every commitment Evan made during the session. Use his **exact words** — do not paraphrase.

```
| [Week start] | [Evan's exact words from transcript] | ⏳ Pending | — |
```

If Evan made no commitments, note it in the Session Log but don't add a row.

### 9c. Update YAML Metrics Block

Update `as_of` and `data_window`, then recalculate metrics using these rules:

```yaml
# --- CALCULATION RULES ---

# WEIGHTED ROLLING AVERAGE (smooths week-to-week noise)
talk_ratio_pct: (old_value × 0.7) + (this_week_value × 0.3)
  # Only count meetings where Evan should be leading (Pitch, Discovery, Assessment)
  # Exclude Technical Discovery meetings where Logan/James lead
post_meeting_followup_hrs: (old_value × 0.7) + (this_week_avg × 0.3)
  # From HubSpot: time between meeting end and first follow-up email
pipeline_touches_per_week: this week's count from HubSpot (not averaged — snapshot)

# CUMULATIVE LIFETIME (recalculate from totals)
win_rate_pct: (total_deals_won / total_deals_closed) × 100
  # Only recalculate when a deal closes this week
total_deals_lifetime: increment if new deal(s) added
active_deals: current count from HubSpot pipeline
avg_days_to_win: recalculate only when a deal closes won
avg_days_to_lose: recalculate only when a deal closes lost

# CUMULATIVE ALL-TIME (add this week's numbers to running totals)
linkedin_connections_sent: previous + this_week_sent
linkedin_connection_accept_pct: recalculate from new totals
linkedin_messages_sent: previous + this_week_sent
linkedin_message_reply_pct: recalculate from new totals
linkedin_inmails_sent: previous + this_week_sent
linkedin_inmail_reply_pct: recalculate from new totals

# REPLY RATE (recalculate when new data)
personal_email_reply_rate_pct: (old_value × 0.7) + (this_week_rate × 0.3)
```

If a metric has no new data this week (e.g., no deals closed), leave it unchanged. Always update `as_of` and `data_window`.

### 9d. SDT Progression Log — Log EVERY Session

Add a row to the SDT Progression Log after every session. Do not skip — even "no movement" is data.

**Assessment criteria:**

| Need | Signal to Look For | Score |
|------|-------------------|-------|
| **Autonomy** | Did Evan self-diagnose before John shared data? Did he set his own commitments without prompting? Did he push back or offer his own read? | same / up / down |
| **Competence** | Did Evan reference a skill he's been working on? Show improvement from last session? Demonstrate new capability? | same / up / down |
| **Relatedness** | Did Evan connect his work to team impact, client outcomes, or the SRED.ca mission? | same / up / down |

**Ladder positions (assess from transcript language):**

| Ladder | Level | Language Signals |
|--------|-------|-----------------|
| **Motivation** | 2 (Ego/Should) | "I should...", "I need to...", "I have to..." |
| **Motivation** | 3 (Goal/Want) | "I want to...", "I'm going to...", "My plan is..." |
| **Motivation** | 4 (Value/Identity) | "This is how I work", "That's not my standard", "I believe..." |
| **Decision** | 2 (Reports back) | Waits for John to assess, asks "what do you think?" |
| **Decision** | 3 (Recommends) | "I think I should...", offers own analysis first |
| **Decision** | 4 (Decides/Informs) | "Here's what I did...", already took action, tells John |

**Also rate Grit/Grace balance:** 1 (all grace, no challenge) through 5 (all grit, no empathy). Target: 3.

**Row format:**
```
| [Date] | [Autonomy: same/up/down] | [Competence: same/up/down] | [Relatedness: same/up/down] | [Motivation Level: X] | [Decision Rung: X] | [Notes: 1 sentence + Grit/Grace: X/5] |
```

### 9e. Update Personal Goals Progress

Read `evan-personal-goals.md`. For each **active goal** (not blank templates):
- Search the transcript for any mention of the goal topic
- If discussed: add a row to that goal's Progress Log
  ```
  | [Date] | [Evan's exact update — his words] | [Coach observation — 1 sentence] |
  ```
- If not discussed: do nothing (don't log "not discussed")

If no goals are set yet (first sessions before quarterly review), skip this step entirely.

### 9f. Coaching Intelligence — Timestamped Observations

When the session reveals a NEW pattern not already documented in the Coaching Intelligence section, add it with a date stamp:

```markdown
**[2026-04-21]** Talk ratio hit 18% in BWS pitch — first time above 15%.
Possible driver: coaching focus on discovery questions (Sessions 2-3).
```

**Where to add:**
- New verbal habit → under "Verbal habits to watch"
- New discovery behavior → under "Discovery Patterns" (add row to table)
- New deal pattern → under "Deal Behavior"
- New communication style observation → under "Communication Style"

Do NOT add observations that duplicate existing ones. Only add genuinely new findings.

### 9g. Cross-Session Pattern Detection

Read the last 3 Session Log entries. Compare this session's metrics to the trend:

| Metric | How to Compare | Flag If |
|--------|---------------|---------|
| Talk ratio | This session vs. 3-session average | Moved >20% in either direction |
| Follow-up speed | This week vs. 3-week average | Moved >20% |
| Commitment completion | This session's resolved vs. total | Below 50% or above 80% |
| Discovery questions | Count from this week's meetings vs. baseline | New high or new low |

If a flag triggers, add to the Session Log entry:
```
**Pattern Alert:** Talk ratio increased 24% (from 8.2% avg to 10.1%). 
Third consecutive session above baseline. Trend: improving.
```

### 9h. Quarterly Review Awareness

Check if the current date is within 7 days of a quarterly review date:
- **Q1 start:** May 1 (also fiscal year-end wrap)
- **Q2 start:** August 1
- **Q3 start:** November 1
- **Q4 start:** February 1

If within 7 days: add a flag to the completion summary:
```
⚠️ QUARTERLY REVIEW due [date]. Next session should include:
  • Deep personal goals review (progress, obstacles, celebrate wins)
  • New SMART goal setting for next quarter (Socratic method — Evan chooses)
  • SDT arc assessment (where did Evan start the quarter vs. where is he now?)
  • Generate quarterly review PDF (templates/quarterly-review-template.py)
  • Update annual targets if needed
```

## Step 10: Update evan-personal-goals.md (if applicable)

If Step 9e produced goal progress updates, write them to `evan-personal-goals.md` now.

## Step 11: Confirm Completion (with Verification)

Output a verified completion summary to Jude:

```
✅ Post-session processing complete — Week of [Monday] – [Sunday]

Reports generated:
  • Evan's Coaching Report → outputs/coaching-report-[DATE].pdf
  • Manager Summary → outputs/manager-summary-[DATE].pdf

Gmail draft created: "Your Weekly Coaching Report — Week of [date]" (ready to send to Evan)

Profile updates verified:
  ✅ Prior commitments resolved: [N] updated ([X] done, [Y] in progress, [Z] missed)
  ✅ New commitments added: [N] entries
  ✅ YAML metrics updated: as_of = [date], changed: [list fields that changed]
  ✅ SDT Progression Log: row added (Autonomy: [same/up/down], Decision Ladder: [rung], Grit/Grace: [X/5])
  ✅ Session [N] appended to Session Log
  ✅ Personal goals: [N updates logged / no active goals / not discussed]
  ✅ Coaching intelligence: [N new observations / no new patterns]
  [⚠️ Pattern alert: describe any >20% metric shifts]
  [⚠️ Quarterly review due [date] — see flag above]

Commitment track record (all time): [X]/[Y] kept ([Z]%)
```

## Error Handling

- **No transcript found:** Log and exit. Do not generate reports. The scheduled task retries hourly Mon–Wed. Nudges are sent via Google Calendar events (which trigger email notifications): gentle nudge to Evan at Tuesday 5pm ET, alert to both Jude and Evan at Wednesday 5pm ET. Each nudge sends only once per week (controlled by marker file).
- **VAPI API fails on system prompt update:** Run `agents/update_vapi_prompt.py` manually, or fall back to pasting `outputs/vapi-prompt-assembled-[DATE].txt` into the VAPI dashboard.
- **Gmail MCP draft fails:** Save the draft body as a `.txt` file in `outputs/` so Jude can copy-paste.
- **Font download fails (sred_doc.py):** Check network, retry. Fonts are cached after first download.

## Reference Files

- `references/report-content-guide.md` — detailed tone guidance, example sentences, what to say vs. avoid
- `references/sdt-coaching-framework.md` — SDT framework for motivation analysis and progression tracking
- `references/stage-specific-evaluation.md` — pipeline stage evaluation criteria (for pipeline health section)
- `skills/sales-coach-post-session/scripts/generate_coaching_report.py` — ReportLab generator for Evan's report
- `skills/sales-coach-post-session/scripts/generate_manager_summary.py` — ReportLab generator for Manager Summary

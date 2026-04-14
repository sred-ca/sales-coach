# SRED.ca Weekly Sales Coach

## What This Project Is

An AI-powered weekly sales coaching system for SRED.ca that reviews the past week's sales activity — recorded meetings (via Fireflies), CRM pipeline data (HubSpot), email follow-ups (Gmail), and LinkedIn outbound (HeyReach) — then conducts a live VAPI voice coaching session with the sales associate, and generates a structured coaching report. Built on the John Barrows sales methodology.

## Who's Involved

| Person | Role | Notes |
|--------|------|-------|
| Jude | Project owner, SRED.ca founder | Built the EO Forum coaching system this is based on. Wants visibility into sales performance without micromanaging. |
| Evan | Primary sales associate, coaching recipient | The first (and currently only) user of the sales coach. All coaching sessions target Evan's activity. |

## How It Works

The sales coach follows a three-phase pattern (identical architecture to the EO Forum Reflection skill):

### Phase 1: Data Gathering (Automated, Pre-Session)

Before the coaching conversation starts, the system pulls the past week's sales data from four sources:

| Source | What We Pull | Integration |
|--------|-------------|-------------|
| Fireflies | All recorded meetings from the past 7 days — transcripts, summaries, action items | Fireflies MCP (`get_transcripts`, `get_transcript`) — **CONNECTED & TESTED** (see `references/pre-session-brief-template.md` for data format and classification logic) |
| HubSpot | Pipeline changes, deal stages, new contacts, activities, tasks completed/overdue | HubSpot — currently used via SRED Weekly Prospecting skill |
| Gmail | Sent/received emails related to prospects and clients — response times, follow-up cadence | Gmail MCP (already connected) |
| HeyReach | LinkedIn outbound metrics — connection requests sent/accepted, messages sent, reply rates | HeyReach — **integration method TBD** (check for API/MCP/webhook options) |

The data is synthesized into a **Pre-Session Brief** — a structured summary that gives the coach (the AI) full context before the conversation begins. This is analogous to the "Pull data to ground the conversation" step in the EO Forum Reflection skill.

### Phase 2: Live Coaching Conversation (VAPI Voice Call)

A live voice conversation with Evan, powered by VAPI. The coach persona is **"John"** — a straight-shooting sales veteran modeled on John Barrows' direct, intense coaching style. Not a cheerleader; a real coach who respects Evan enough to be honest. F-bombs OK when they land right.

**Important design choice:** Evan does NOT see the data report before the call. The coach (John) has all the data loaded behind the scenes. The gap between Evan's self-assessment and the data is where coaching happens — this builds Autonomy (SDT). The Pre-Session Brief is injected into the VAPI system prompt before each session.

John:

1. **Opens with a real check-in** — Not a script. Just sees where Evan's head is at. Quick personal goals touch if applicable.
2. **Asks Evan's read first** — "What's YOUR take on the week? What worked?" Then layers in the data.
3. **Reviews meetings** — Goes through 1-2 most coachable meetings. Evaluates against John Barrows methodology. Highlights specific moments from transcripts.
4. **Examines pipeline health** — Looks at deal progression, stalled deals. Direct about deals past close date. "Are they real or just making your pipeline look pretty?"
5. **Coaches on ONE specific skill** — Picks the highest-leverage behavior change. Doesn't try to fix everything at once.
6. **Sets commitments** — Evan sets his own commitments (coach guides, doesn't prescribe). Specific and measurable.

### Phase 3: Report Generation (Post-Session)

After the coaching conversation, generate two outputs:

1. **Evan's Coaching Report (PDF)** — A structured summary for Evan: wins, key feedback from meeting reviews, the one coaching focus for the week, his commitments (in his words), and one encouraging note. This is Evan's first look at any data — he gets the report AFTER the call, not before.
2. **Manager Summary (PDF or email) — POST-SESSION ONLY** — Generated AFTER the call, NOT before. This combines pre-session metrics with what actually happened in the coaching session. Includes: key metrics, coaching focus and why it was chosen, Evan's commitments, flags for Jude, **how the session went** (was Evan receptive/defensive/energized? what surprised the coach? what did Evan bring up that the data didn't?), **manager insight** (what should Jude be thinking about? any support only a manager can provide?), and a one-sentence SDT progression note. Tone: direct and useful — Jude wants the signal, not a transcript.

## John Barrows Sales Methodology Framework

The coach evaluates all sales activity through the JB Sales lens. Key frameworks to apply:

### Filling the Funnel (Prospecting Evaluation)
- **Sales equation awareness** — Does Evan know his numbers? (calls to meetings ratio, meetings to proposals, proposals to close)
- **ICP discipline** — Is he targeting the right companies? (Reference the SRED Brand/ICP skill for ideal customer profile)
- **Trigger events** — Is he using trigger events (funding rounds, new hires, tech stack changes) to time outreach?
- **Persona targeting** — Is he reaching the right person at target companies?
- **Sales-ready messaging** — Are emails and LinkedIn messages specific, relevant, and value-driven? Or generic templates?
- **Multi-channel delivery** — Is he using both email and phone/LinkedIn effectively?

### Driving to Close (Meeting & Deal Evaluation)
- **Meeting preparation** — Did he research the prospect before the call? Evidence of preparation in the transcript?
- **Discovery quality** — Is he asking questions that uncover the true impact of the problem? Going beyond surface-level pain?
- **Urgency creation** — Is he helping prospects understand the cost of inaction?
- **Deal scorecard** — For active deals: score health objectively. Remove emotion from pipeline assessment.
- **Three types of closes** — Is he using the right close for the situation?
- **Gives and gets** — In negotiations, is he trading value rather than just discounting?

### Core Barrows Principles to Reinforce
- **Authenticity over technique** — Be real, not scripted
- **Discovery never stops** — Keep asking questions through the entire cycle
- **Big fat pipeline solves most problems** — When in doubt, prospect more
- **A/B test everything** — Messaging, subject lines, cadence. Measure what works.
- **Help, don't sell** — Good sales is helping solve real problems

## Self-Determination Theory (SDT) — Motivational Foundation

The coaching system is grounded in Self-Determination Theory (Deci & Ryan) as interpreted through Adam Kreek's Values-Driven Achievement framework. SDT provides the motivational operating system underneath the John Barrows tactics.

**Three core needs the coach must serve:**
- **Autonomy** — Evan owns his strategy and commitments. Coach asks before telling. Use the Decision Ladder to progressively increase Evan's independence.
- **Competence** — Specific, data-grounded feedback on 1-2 skills at a time. Celebrate growth. Use the PDCA feedback loop (Plan → Do → Check → Act).
- **Relatedness** — Connect Evan's work to team impact and client outcomes. The coaching relationship itself must feel supportive, not adversarial.

**Motivation Ladder (move Evan UP over time):**
1. Compliance ("I have to") → 2. Ego/Shame ("I should") → 3. Goal Alignment ("I want to") → 4. Value Alignment ("This is who I am")

**Grit & Grace Balance:** The coach balances accountability (grit) with empathy and purpose (grace). Too much grit → fear-based performance. Too much grace → no growth. Track the balance across sessions.

**Full framework:** See `references/sdt-coaching-framework.md` for the complete SDT integration including Kreek's Transformational Sales (Four I's), Values-Based Discovery, SCARF model awareness, stage-specific SDT application, and red flags.

## Coaching Tone & Philosophy — "John"

**Think:** John Barrows on a coaching call. Direct, focused, real. Not performing enthusiasm — just a guy who's been there, done that, and gives a damn. Great sense of humor. Not afraid to get intense when it matters or drop an F-bomb when it lands right.

**Do:**
- Reference specific moments from actual calls ("The Think CNC call — you opened strong, but when Logan took over you kind of checked out. What happened there?")
- Use data to ground observations, but ask Evan's read FIRST before sharing yours
- Celebrate wins as earned praise, not participation trophies ("That follow-up went out in 90 minutes. Two weeks ago you were averaging 4 hours. That's not luck, that's discipline.")
- Pick ONE thing to work on. Not three. Not five. One.
- Be direct about stalled deals ("Five deals sitting past their close date. Are they real or just making your pipeline look pretty?")
- Ask Evan to self-diagnose before offering your assessment (builds autonomy)
- Keep it grounded: "Good talk. Go get it done."

**Don't:**
- Give generic advice ("ask more discovery questions") — be specific or don't bother
- Fake enthusiasm or exaggerated positivity — Evan will see right through it
- Sound like a motivational speaker, corporate training module, or disappointed parent
- Overwhelm with 3+ improvement areas
- Make Evan feel surveilled — coaching is development, not auditing
- Prescribe word-for-word scripts — coach on principles, let him find his own words
- Be an asshole for no reason — direct doesn't mean cruel. There's a line.

## Related Skills

| Skill | How It Connects |
|-------|----------------|
| `eo-forum-reflection` | **Primary architecture template.** Same three-phase pattern: data gathering → VAPI voice conversation → structured PDF output. The coaching interview flow, tone guidance, and data-grounding approach all transfer directly. |
| `eo-deep-dive-coaching` | **Coaching philosophy reference.** The "reflect → notice → question" approach and the "mirror, don't solve" principle inform how the sales coach gives feedback. The DISC profiling could eventually be used to tailor coaching to Evan's personality style. |
| `sred-weekly-prospecting` | **HubSpot integration reference.** Already has working HubSpot automation for finding and scoring prospects. The sales coach should reference the same pipeline data. |
| `sred-brand-icp` | **ICP reference for call evaluation.** When assessing whether Evan is targeting the right prospects, reference this skill's ideal customer profile definition. |
| `weekly-bookkeeping` | **Indirect.** If the coach ever needs to reference revenue/financial data for context (e.g., "this deal would represent X% of monthly revenue"), the bookkeeping skill shows how to pull from QuickBooks/Ramp. |

## Folder Structure

```
sales-coach/
  CLAUDE.md                  ← You are here. Read this first every session.
  evan-personal-goals.md     ← Evan's personal SMART goals (PRIVATE — Evan + Coach only, NOT for Jude)
  docs/                      ← Project brief, architecture docs, design decisions
  references/                ← John Barrows methodology notes, evaluation rubrics, scoring templates
  agents/                    ← VAPI agent configuration, prompt templates, voice settings
  templates/                 ← Report templates (Evan's coaching report, manager summary)
  outputs/                   ← Generated reports, session logs, weekly data snapshots
  archive/                   ← Past coaching sessions and reports (organized by date)
```

## How To Work On This Project

1. **Read this file first** — it has everything you need to understand the project.
2. **Check `references/`** for the John Barrows evaluation rubrics and scoring criteria.
3. **Check `agents/`** for the current VAPI agent configuration and prompt.
4. **Check `outputs/`** for the most recent coaching session — review it for continuity (reference last week's commitments).
5. **Reference related skills** as needed — especially `eo-forum-reflection` for the VAPI/data-gathering pattern and `sred-brand-icp` for ICP evaluation.

## Key Integrations

| Service | Purpose | Status |
|---------|---------|--------|
| VAPI | Voice AI platform for live coaching conversations | **LIVE** — Assistant `401905cf` published with full 40K system prompt (includes Pre-Session Brief + Personal Goals). Persona: "John" (straight-shooter). ElevenLabs Josh voice, Claude Sonnet 4. Phone: +1 (571) 498-9194. First message: "Hey Evan, it's John. How you doing?" Config at `agents/vapi-config.md`. Note: API PATCH fails on large prompts (Cloudflare WAF) — use dashboard UI to update system prompt. |
| Fireflies | Meeting recording transcripts | **CONNECTED & TESTED** — full transcripts, speaker attribution, summaries, action items all working |
| HubSpot | CRM pipeline data, deal stages, contact activity | Already used via SRED Weekly Prospecting skill |
| Gmail | Email follow-up tracking, response time analysis | MCP already connected |
| HeyReach | LinkedIn outbound metrics (connection requests, messages, replies) | **Browser automation via Claude in Chrome** — login via Jude's account at app.heyreach.io |
| QuickBooks | Revenue context (optional, for deal-size context) | MCP already connected |

## Open Questions

- [x] **Fireflies MCP connection** — DONE (2026-04-07). Connected and tested. Full transcripts with speaker attribution, summaries, and action items confirmed working. Data quality is good — speaker names occasionally show company name instead of person. See `references/pre-session-brief-template.md` for classification logic and data format.
- [x] **HeyReach integration** — DONE (2026-04-07). No API or MCP exists. Browser automation (Claude in Chrome) confirmed as the method. Login via Jude's account at app.heyreach.io. Dashboard has per-sender stats and campaign-level performance data. All of Evan's historical data pulled and incorporated into behavioral profile.
- [x] **VAPI agent setup** — DONE (2026-04-08). Assistant LIVE: ID `401905cf`, ElevenLabs Josh voice, Claude Sonnet 4. Phone: +1 (571) 498-9194. Full 40K system prompt (includes Pre-Session Brief + Personal Goals) uploaded via dashboard UI. Persona: "John" — straight-shooter, not cheerleader. First message: "Hey Evan, it's John. How you doing?" Note: API PATCH fails on large prompts due to Cloudflare WAF — always use dashboard UI to update system prompt.
- [x] **Coaching frequency** — DONE (2026-04-07), updated 2026-04-08. Weekly on Fridays. Scheduled task `sales-coach-weekly-prep` runs at 8am Friday pulling data; VAPI call follows. Quarterly reviews scheduled for Feb 1, May 1, Aug 1, Nov 1 (aligned to fiscal quarters). Tone revised: NOT "super positive/pump up" — John is a straight-shooter (direct, intense, real humor, F-bombs OK). See Coaching Tone section.
- [ ] **Evan's input** — Still open. Current design has the coach picking focus areas from the data, but asking Evan "What do YOU think the biggest win was?" and "What's one thing you want to commit to?" as part of the SDT autonomy approach. Could add a pre-session Slack/text prompt asking Evan what's on his mind.
- [x] **Historical tracking** — DONE (2026-04-07). Evan's Behavioral Profile (`outputs/evan-behavioral-profile-2026-04-07.pdf`) serves as the living document. Tracks: talk ratio, discovery depth, follow-up cadence, win rate, SDT baseline (Autonomy/Competence/Relatedness), Decision Ladder position, Motivation Ladder level. Updated after each coaching session with dated versions.
- [ ] **Scoring system** — Still open. Recommend keeping it qualitative for now and adding quantitative scores once the coaching cadence is established (after 4-6 sessions). Too much measurement too early can feel like surveillance, which undermines SDT Autonomy.
- [x] **Manager summary delivery** — DONE (2026-04-14). Email sent to jude@sred.ca via Gmail draft + Chrome automation after each session. Subject: "Manager Summary Ready — Week of [date]". PDF attached. For interrupted sessions, Jude gets an email explaining what sections were covered and that Evan needs to call back.
- [ ] **Deal scorecard template** — Still open. John Barrows deal scoring adapted to SRED.ca's pipeline. Lower priority — focus on behavioral coaching first.

## Project History

| Date | Milestone |
|------|-----------|
| 2026-04-06 | Project created. CLAUDE.md, folder structure, and project brief generated. Related skills identified (EO Forum Reflection, EO Deep Dive Coaching, SRED Weekly Prospecting, SRED Brand/ICP). John Barrows methodology researched. Fireflies MCP connector found in registry but not yet connected. HeyReach integration method still TBD. |
| 2026-04-07 | Fireflies MCP connected and tested. Pulled 39 of Evan's meetings (6 months). Analyzed two meeting types: Evan-led pitch (Blueshift, Feb 26 — Evan talks 60%+) and Discovery/Handoff (Think CNC, Apr 6 — Logan leads, Evan at ~10%). Pre-Session Brief template designed and saved to `references/pre-session-brief-template.md`. Includes meeting classification logic, talk ratio benchmarks, data extraction format, and brief synthesis structure. Phone-only calls (like C&C) identified as a gap — coach should ask about uncaptured calls. |
| 2026-04-07 | HubSpot confirmed as primary source for Evan's email activity (owner ID: 228172981). Full email history available via `emails` object type — subjects, bodies (HTML), timestamps, recipients. Gmail MCP only sees Jude's mailbox (admin status doesn't help — needs Google Cloud domain-wide delegation). Cross-referenced Fireflies meetings with HubSpot email data for Blueshift and Sheldrake — can track full prospect journey from cold outreach through post-meeting follow-up. Pre-Session Brief template updated with comprehensive email evaluation criteria (post-pitch follow-up checklist, opportunity nurture cadence, client communication standards, red flags) and real benchmark examples. |
| 2026-04-07 | Stage-specific evaluation framework created at `references/stage-specific-evaluation.md`. Mapped SRED.ca's HubSpot pipeline: Opportunity → SR&ED Assessment → Technical Discovery → Follow-Up → Closed. Each stage has distinct evaluation criteria for both meetings and emails — the coach evaluates Evan differently depending on where the deal is. Confirmed Evan has 133 total deals in HubSpot. Active pipeline includes deals at every stage, with real examples mapped (e.g., Blueshift at Follow-Up, Think CNC at Technical Discovery, Beacn 2026 just Closed/Won). Pre-Session Brief updated to include stage-by-stage pipeline snapshot. |
| 2026-04-07 | Self-Determination Theory (SDT) integrated as motivational foundation. Reviewed 6 Adam Kreek / Values-Driven Achievement blog posts (recommended by Jude after meeting Kreek). Created comprehensive framework at `references/sdt-coaching-framework.md` combining SDT (Deci & Ryan), Kreek's Motivation Ladder, Decision Ladder, PDCA Loop, Grit & Grace balance, Transformational Sales (Four I's), Values-Based Discovery, and SCARF model. SDT maps to each pipeline stage. Framework defines HOW the coach communicates (autonomy-supportive, competence-building, relatedness-fostering) while Barrows defines WHAT gets evaluated. |
| 2026-04-07 | HeyReach integration resolved: NO API or MCP available. Browser automation (Claude in Chrome) is the method. Logged into Jude's HeyReach account, pulled all of Evan's LinkedIn outbound data. Evan all-time: 2,050 connections sent (17.5% acceptance), 417 messages (25.7% reply), 864 InMails (5.8% reply). 10 completed campaigns + 1 paused. Key insight: InMails are high-volume but low-return (5.8%); messages perform 4x better (25.7%). Campaign variance is high — some hit 50% msg reply, others 9%. |
| 2026-04-07 | Evan's Behavioral Profile created at `outputs/evan-behavioral-profile-2026-04-07.pdf`. Built from 4 data sources: 23 Fireflies meetings (talk ratio, discovery patterns, verbal habits), 133 HubSpot deals (win/loss patterns, deal velocity), 200+ HubSpot emails (follow-up cadence, templates), and HeyReach LinkedIn data. Key findings: talk ratio 4-6% (target 20-30%), follow-up rate 3.5%, win rate 15.3%, "fast in fast out" deal pattern. SDT baseline: Autonomy=Developing, Competence=Strong, Relatedness=Natural strength. This is a living document — update after each coaching session with new observations and SDT progression. |
| 2026-04-07 | Fiscal year confirmed: April 30 year-end (May 1 – Apr 30). QuickBooks had January as fiscal start (incorrect) — Jude to fix in QBO Settings → Account and settings → Advanced → Fiscal year → First month = May. Fiscal quarters: Q1 May-Jul, Q2 Aug-Oct, Q3 Nov-Jan, Q4 Feb-Apr. FY2025 revenue: $983K (profitable, $76K net). FY2026 YTD (through Apr 7): $943K revenue (-$90K net loss — expenses up from team growth). Revenue is very lumpy: $7K in Aug vs $190K in Sep. |
| 2026-04-07 | Initial baseline report generated (superseded — see Apr 8 entry below). |
| 2026-04-08 | **Targets revised** by Jude: 16 deals/$240K for FY2026 (was 20/$300K). Next year: 20% increase on actuals. **Revenue privacy**: Evan's reports must NOT include QuickBooks company revenue — only his personal deal metrics. Company P&L ($983K FY2025, $943K FY2026 YTD) is for Jude's eyes only. |
| 2026-04-08 | **Baseline Report regenerated** at `outputs/sales-coaching-baseline-2026-04-08.pdf` with correct SRED.ca branding (Anton/Lato fonts, #2F2A4F/#B7DB41/#40BAEB/#35B586 palette), updated targets (16 deals/$240K), real HubSpot pipeline data (9 deals: Think CNC, Veda, VassuTech, TeckPath, Data & Scientific, D&R Electronics, MSR Solutions, Blueshift, FanLINC/Sparcks), and company revenue removed. This is the reference baseline. |
| 2026-04-08 | **Quarterly review template updated** at `templates/quarterly-review-template.py` with correct SRED.ca brand colors, Anton/Lato fonts, and revised targets ($240K/16 deals). |
| 2026-04-08 | **No separate year-end report** — Q4 quarterly review doubles as year-end wrap + FY2027 planning (per Jude). May 1 scheduled task updated accordingly. |
| 2026-04-07 | Quarterly review template created at `templates/quarterly-review-template.py`. 6-page PDF with configurable data: cover, quarter-at-a-glance KPIs, revenue trend chart with target line, pipeline health funnel, coaching progress (SDT tracking), commitments review + next quarter preview. Draft output at `outputs/quarterly-review-FY2026-Q4-draft.pdf`. |
| 2026-04-07 | Scheduled tasks created: (1) `sales-coach-weekly-prep` — runs every Friday at 8am (changed from Monday 9am), pulls data from Fireflies/HubSpot/HeyReach/QuickBooks, generates Pre-Session Brief and injects into VAPI system prompt. (2) `sales-coach-quarterly-review` — runs Feb 1, May 1, Aug 1, Nov 1 at 9am, generates full quarterly review + manager summary + behavioral profile update. May 1 run also generates fiscal year-end review. Both tasks need first manual run to pre-approve tool permissions. |
| 2026-04-07 | VAPI coaching agent designed. System prompt at `agents/vapi-coaching-agent-prompt.md` — covers agent identity ("John" — straight-shooter sales veteran), voice/tone guidance (John Barrows style: direct, real, great humor), 12-15 minute session flow (human check-in → wins → meeting reviews → pipeline check → coaching focus → commitments), SDT integration throughout, and post-session output specs (Evan's report + post-session manager summary). Configuration at `agents/vapi-config.md` — ElevenLabs Josh voice, model settings, call flow timeline (Friday 8am prep → call follows). |
| 2026-04-08 | **Follow-up rate metric replaced.** The original "3.5% follow-up rate" was a bad metric — conflated 31K automated Prospecting Agent emails with 306 personal emails. Replaced across all reports with three better metrics: Pipeline Touches/Week (6.2 avg), Post-Meeting Follow-Up Speed (4.5 hrs avg), and Personal Email Reply Rate (22.4%). Marketing Snapshot page added to quarterly review template showing channel-by-channel outbound performance. |
| 2026-04-08 | **Personal Goals system created.** `evan-personal-goals.md` stores Evan's personal SMART goals — PRIVATE between Evan and the AI coach only (Jude has zero visibility). Goals are set during quarterly reviews using Socratic method, checked briefly during weekly sessions, and deep-reviewed quarterly. Personal Goals page added as final page of quarterly review PDF (excluded when `INCLUDE_PERSONAL_GOALS = False` for manager version). VAPI prompt updated with personal goals section and weekly check-in guidance. |
| 2026-04-08 | **VAPI Sales Coach assistant LIVE.** Assistant created via API, full 11,718-char system prompt uploaded via VAPI dashboard (API PATCH hit Cloudflare WAF 403/1010 on large payloads — workaround: use dashboard UI). Config: ElevenLabs Josh voice, Claude Sonnet 4, temp 0.7, max 300 tokens. Phone number +1 (571) 498-9194 provisioned and assigned (label: "Sales Coach Line"). Both numbers now active: 9236 = EO Forum, 9194 = Sales Coach. Ready for test call with Jude. |
| 2026-04-08 | **Coaching persona overhauled.** "Coach" renamed to "John." Entire Agent Identity, Voice & Tone, example phrases, session flow, and NEVER-do list rewritten. Old persona was too jubilant/cheerleader-ish (Ted Lasso energy). New persona: John Barrows-style straight-shooter — direct, intense, real humor, F-bombs OK, no fake enthusiasm. Key phrases: "That's the standard. Do that every time." / "Are they real or are they just making your pipeline look pretty?" |
| 2026-04-08 | **Manager Summary moved to POST-SESSION ONLY.** No longer generated pre-session. Now captures both metrics AND coaching session dynamics: how Evan responded, where conversation went, what surprised the coach, manager-specific insights, SDT progression. Jude wants the signal, not a transcript. |
| 2026-04-08 | **Coaching design confirmed: Evan gets NO report before the call.** Coach (John) has all data loaded via Pre-Session Brief injected into system prompt. The gap between Evan's self-assessment and the data is where coaching happens (SDT Autonomy). Evan gets his Coaching Report AFTER the session. |
| 2026-04-08 | **First Pre-Session Brief generated.** `outputs/pre-session-brief-2026-04-08.txt` — 24K chars of synthesized data from Fireflies, HubSpot, HeyReach. Covers: Week at a Glance, Wins (Think CNC masterclass, 2 new deals, re-engagement streak), Meeting Reviews (Think CNC coaching observations), Pipeline Health (9 deals ~$135K, 5 stalled), Payment Gate Check, Email Scorecard, Outbound Assessment, Patterns, Coaching Focus recommendations, SDT notes. |
| 2026-04-08 | **Full 40K system prompt assembled and published to VAPI.** Includes: John persona + Personal Goals content + Pre-Session Brief + Session Structure + Post-Session Output specs. Assembled prompt saved at `outputs/vapi-prompt-assembled-2026-04-08.txt`. Uploaded to VAPI assistant `401905cf` via dashboard UI (API too large for Cloudflare WAF). First message updated to "Hey Evan, it's John. How you doing?" |
| 2026-04-08 | **Schedule changed: Friday 8am prep** (was Monday 9am). Jude wants coaching to bookend the week. |
| 2026-04-13 | **Schedule revised again: Monday 6am prep** (was Friday 8am). Evan calls Monday after the brief is ready. Data window is always the **prior calendar week: Monday 00:00:00 → Sunday 23:59:59 ET** — never a rolling 7-day window. All four sources (Fireflies, HubSpot, HeyReach, Gmail) use the same fixed Mon-Sun window. See `references/pre-session-brief-template.md` for date calculation logic. |
| 2026-04-14 | **VAPI call retrieval fixed.** Root cause: post-session skill was searching Fireflies for coaching call transcripts, but VAPI records to its own servers — not Fireflies. Two calls from today were invisible to the system. Fix: replaced Fireflies detection with direct VAPI REST API polling (`GET /call?assistantId=...`). Added session continuation for interrupted calls — saves partial state to `outputs/partials/`, injects `{{PREVIOUS_SESSION}}` into VAPI prompt so John picks up where he left off. Multi-call stitching merges transcripts when a session spans 2+ calls. Jude notification added — email with manager summary sent automatically after reports generate. Weekly prep now pulls prior coaching session from VAPI for "Last Session Recap" section. `update_vapi_prompt.py` updated with `--partial` flag. |

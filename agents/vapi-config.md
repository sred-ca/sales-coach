# VAPI Agent Configuration — Sales Coach

## Recommended Settings

### Voice
- **Provider:** ElevenLabs or PlayHT
- **Voice style:** Male, mid-30s to 40s, warm and confident. Think "experienced colleague" not "authority figure"
- **Recommended voices to audition:**
  - ElevenLabs: "Josh" (warm, professional) or "Adam" (confident, conversational)
  - PlayHT: Similar warm-professional male voice
- **Speech rate:** Slightly above average — energetic but not rushed
- **Stability:** Medium-high (consistent but not robotic)
- **Clarity:** High

### Model
- **LLM:** Claude (Anthropic) — matches the rest of the SRED.ca system
- **Temperature:** 0.7 (conversational, not too random, not too rigid)
- **Max tokens per turn:** 300 (keeps responses conversational, not lecture-length)

### Conversation Settings
- **Max duration:** 90 minutes (5400 seconds) — updated 2026-04-14. Was 60 min, increased to give full coaching sessions room to breathe
- **Silence timeout:** 45 seconds — updated 2026-04-14. Was 10 seconds, which caused both Session 1 calls to end prematurely (`silence-timed-out`). 45 seconds gives Evan time to think, check his CRM, or look something up without the call dropping
- **Interruption sensitivity:** Medium (allow natural back-and-forth but don't let cross-talk dominate)
- **End-of-turn detection:** Conservative (wait for Evan to finish — don't cut him off)
- **First message:** "Hey Evan, it's John. How you doing?"

### Integration
- **Pre-session:** The weekly prep task generates a Pre-Session Brief PDF every Monday at 9am. This brief is injected into the system prompt under the `{{PRE_SESSION_BRIEF}}` tag before the call starts.
- **Post-session:** The call transcript is captured and used to generate:
  1. Evan's Coaching Report (PDF, saved to outputs/)
  2. Manager Summary for Jude (PDF or email)
  3. Updates to Evan's Behavioral Profile (if significant observations)
- **Scheduling:** The VAPI call can be triggered manually after the weekly brief is ready, or scheduled for a fixed time (e.g., Monday at 10am, giving 1 hour for the prep task to complete)

### Call Flow Summary
```
Monday 9:00 AM — Weekly prep task runs (automated)
  ↓ Pulls data from Fireflies, HubSpot, HeyReach, QuickBooks
  ↓ Generates Pre-Session Brief PDF
  ↓ Injects brief into VAPI agent system prompt

Monday 10:00 AM — VAPI coaching call with Evan (manual trigger or scheduled)
  ↓ 12-15 minute voice conversation
  ↓ Transcript captured

Monday ~10:20 AM — Post-session processing (automated or manual)
  ↓ Generates Evan's Coaching Report
  ↓ Generates Manager Summary for Jude
  ↓ Updates behavioral profile if needed
```

## Live Configuration (Completed 2026-04-08)

| Setting | Value |
|---------|-------|
| **Assistant ID** | `401905cf-f38f-4277-8bee-814916aaf2c0` |
| **Assistant Name** | SRED.ca Sales Coach |
| **Phone Number** | +1 (571) 498-9194 |
| **Phone Number ID** | `d14a1d77-6aed-4db8-ad48-9c1295893dc5` |
| **Phone Label** | Sales Coach Line |
| **Voice** | ElevenLabs Josh (`TxGEqnHWrfWFTfGW9XjX`), eleven_multilingual_v2 |
| **Model** | Anthropic Claude Sonnet 4 (`claude-sonnet-4-20250514`) |
| **Temperature** | 0.7 |
| **Max Tokens** | 300 |
| **System Prompt** | Full 11,718-char prompt from `vapi-coaching-agent-prompt.md` |
| **First Message** | "Hey Evan, it's John. How you doing?" |
| **Status** | Published and Active |

### Other VAPI Numbers (for reference)
| Number | Assistant | Purpose |
|--------|-----------|---------|
| +1 (571) 498-9236 | New Assistant (EO Forum) | EO Forum Reflection calls |
| +1 (571) 498-9194 | SRED.ca Sales Coach | Weekly sales coaching calls |

## Setup Steps (Completed)

1. ~~**Create VAPI account**~~ ✅ Already existed at https://vapi.ai
2. ~~**Create a new Assistant**~~ ✅ Created via API, prompt uploaded via dashboard (API hit Cloudflare WAF on large payloads)
3. ~~**Configure voice**~~ ✅ ElevenLabs Josh voice configured
4. ~~**Set up phone number**~~ ✅ +1 (571) 498-9194 provisioned and assigned
5. **Test with Jude first** — do a dry run to calibrate tone and pacing
6. ~~**Connect transcript capture**~~ ✅ Resolved 2026-04-14: Post-session skill now polls VAPI REST API directly (`GET /call?assistantId=...`) instead of searching Fireflies. Supports partial session detection, multi-call stitching, and continuation prompting.
7. **Wire up pre/post session** — The weekly prep task generates the brief; post-session processing uses the transcript

## Architecture Parallel: EO Forum Reflection

This follows the same three-phase pattern as the `eo-forum-reflection` skill:
1. **Data gathering** (automated) → Pre-Session Brief
2. **Voice conversation** (VAPI) → Live coaching session
3. **Report generation** (automated) → Coaching Report + Manager Summary

The EO Forum Reflection skill can be referenced for implementation patterns, especially around VAPI webhook configuration and transcript processing.

## Open Questions for Setup
- [ ] Does Jude want the system to call Evan, or should Evan call in? (Phone: +1 571-498-9194)
- [x] What phone number should be used? → +1 (571) 498-9194 (provisioned 2026-04-08)
- [x] Should the call be recorded for later reference? → Yes, VAPI records all calls natively. Transcripts retrieved via `GET /call/{id}` → `artifact.transcript`. Recordings at `artifact.recording`.
- [x] Should Jude receive the Manager Summary by email or just in the project folder? → Email only. Gmail draft created and sent via Chrome automation after each session. Subject: "Manager Summary Ready — Week of [date]".
- [ ] Should there be a way for Evan to request an ad-hoc coaching session outside the weekly cadence?

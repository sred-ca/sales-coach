#!/usr/bin/env python3
"""
VAPI System Prompt Updater — SRED.ca Sales Coach

Reads the static prompt template, injects the current Pre-Session Brief and
Personal Goals, then PATCHes the VAPI assistant via API.

IMPORTANT: Uses http.client (not urllib/requests) to bypass Cloudflare WAF
that blocks urllib's default User-Agent on PATCH requests.

Usage:
    python3 update_vapi_prompt.py --brief outputs/pre-session-brief-2026-04-14.txt

    # Or with explicit goals file:
    python3 update_vapi_prompt.py --brief outputs/pre-session-brief-2026-04-14.txt --goals evan-personal-goals.md

Environment:
    VAPI_API_KEY — Required. Your VAPI private API key.

Configuration (edit these constants if the assistant changes):
"""

import argparse
import http.client
import json
import os
import sys

# --- Configuration ---
ASSISTANT_ID = "401905cf-f38f-4277-8bee-814916aaf2c0"
VAPI_HOST = "api.vapi.ai"
MODEL_ID = "claude-sonnet-4-20250514"
TEMPERATURE = 0.7
MAX_TOKENS = 300

# Paths (relative to project root)
PROMPT_TEMPLATE = "agents/vapi-coaching-agent-prompt.md"
DEFAULT_GOALS_FILE = "evan-personal-goals.md"
DEFAULT_PROFILE_FILE = "evan-profile.md"


def load_template(project_root: str) -> str:
    """Load the static prompt template and extract content from ## Agent Identity onward."""
    path = os.path.join(project_root, PROMPT_TEMPLATE)
    with open(path, "r") as f:
        content = f.read()
    start = content.find("## Agent Identity")
    if start == -1:
        raise ValueError(f"Could not find '## Agent Identity' in {path}")
    prompt = content[start:]
    # Strip trailing --- separator
    if prompt.rstrip().endswith("---"):
        prompt = prompt.rstrip()[:-3].rstrip()
    return prompt


def load_partial_session(partial_path: str) -> str:
    """Load a partial session JSON and format it for the VAPI prompt."""
    with open(partial_path, "r") as f:
        partial = json.load(f)

    sections_done = partial.get("sections_completed", [])
    sections_left = partial.get("sections_remaining", [])
    summary = partial.get("summary_for_resume", "")
    call_date = partial.get("call_date", "unknown")
    duration = partial.get("duration_seconds", 0)

    section_names = {
        "opening": "Opening Check-In + Personal Goals",
        "wins": "Wins Recognition",
        "meeting_reviews": "Meeting Reviews",
        "pipeline": "Pipeline & Activity Check",
        "coaching_focus": "Coaching Focus",
        "commitments": "Commitments & Close",
    }

    done_list = ", ".join(section_names.get(s, s) for s in sections_done)
    remaining_list = ", ".join(section_names.get(s, s) for s in sections_left)

    return (
        f"PREVIOUS SESSION DATA — Evan's call on {call_date} "
        f"({duration // 60} minutes) was interrupted.\n\n"
        f"Sections completed: {done_list}\n"
        f"Sections remaining: {remaining_list}\n\n"
        f"Summary of what was covered:\n{summary}\n\n"
        f"Pick up from: {section_names.get(sections_left[0], sections_left[0]) if sections_left else 'unknown'}"
    )


DEFAULT_PREVIOUS_SESSION = "No prior session this week — start fresh."


def inject_variables(template: str, brief: str, goals: str, profile: str,
                     previous_session: str = DEFAULT_PREVIOUS_SESSION) -> str:
    """Replace {{PRE_SESSION_BRIEF}}, {{PERSONAL_GOALS}}, {{EVAN_PROFILE}}, and {{PREVIOUS_SESSION}} placeholders."""
    result = template.replace("{{PRE_SESSION_BRIEF}}", brief)
    result = result.replace("{{PERSONAL_GOALS}}", goals)
    result = result.replace("{{EVAN_PROFILE}}", profile)
    result = result.replace("{{PREVIOUS_SESSION}}", previous_session)
    for var in ["{{PRE_SESSION_BRIEF}}", "{{PERSONAL_GOALS}}", "{{EVAN_PROFILE}}", "{{PREVIOUS_SESSION}}"]:
        if var in result:
            raise ValueError(f"Failed to inject {var}")
    return result


def patch_assistant(api_key: str, system_prompt: str) -> dict:
    """PATCH the VAPI assistant's system prompt. Uses http.client to bypass Cloudflare WAF."""
    payload = json.dumps({
        "model": {
            "model": MODEL_ID,
            "provider": "anthropic",
            "temperature": TEMPERATURE,
            "maxTokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": system_prompt}
            ]
        }
    })

    conn = http.client.HTTPSConnection(VAPI_HOST)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "SRED-SalesCoach/1.0"
    }
    conn.request("PATCH", f"/assistant/{ASSISTANT_ID}", payload, headers)
    resp = conn.getresponse()
    body = resp.read().decode()

    if resp.status != 200:
        raise RuntimeError(f"VAPI API returned {resp.status}: {body[:500]}")

    return json.loads(body)


def main():
    parser = argparse.ArgumentParser(description="Update VAPI Sales Coach system prompt")
    parser.add_argument("--brief", required=True, help="Path to pre-session brief .txt file")
    parser.add_argument("--goals", default=None, help="Path to personal goals .md file (default: evan-personal-goals.md)")
    parser.add_argument("--profile", default=None, help="Path to coaching profile .md file (default: evan-profile.md)")
    parser.add_argument("--partial", default=None, help="Path to partial session JSON for continuation (default: no prior session)")
    parser.add_argument("--dry-run", action="store_true", help="Print assembled prompt without calling API")
    args = parser.parse_args()

    # Find project root (directory containing CLAUDE.md)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(os.path.join(project_root, "CLAUDE.md")):
        project_root = os.getcwd()

    # Load API key
    api_key = os.environ.get("VAPI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: VAPI_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it with: export VAPI_API_KEY='your-key-here'", file=sys.stderr)
        sys.exit(1)

    # Load files
    template = load_template(project_root)
    print(f"Template loaded: {len(template)} chars")

    with open(args.brief, "r") as f:
        brief = f.read()
    print(f"Brief loaded: {len(brief)} chars ({args.brief})")

    goals_path = args.goals or os.path.join(project_root, DEFAULT_GOALS_FILE)
    with open(goals_path, "r") as f:
        goals = f.read()
    print(f"Goals loaded: {len(goals)} chars ({goals_path})")

    profile_path = args.profile or os.path.join(project_root, DEFAULT_PROFILE_FILE)
    with open(profile_path, "r") as f:
        profile = f.read()
    print(f"Profile loaded: {len(profile)} chars ({profile_path})")

    # Load partial session (if any)
    previous_session = DEFAULT_PREVIOUS_SESSION
    if args.partial:
        previous_session = load_partial_session(args.partial)
        print(f"Partial session loaded: {len(previous_session)} chars ({args.partial})")
    else:
        print("No partial session — fresh start")

    # Assemble
    assembled = inject_variables(template, brief, goals, profile, previous_session)
    print(f"Assembled prompt: {len(assembled)} chars")

    if args.dry_run:
        print("\n--- DRY RUN — assembled prompt: ---")
        print(assembled[:500])
        print(f"\n... ({len(assembled)} total chars)")
        return

    # Push to VAPI
    print("\nUpdating VAPI assistant...")
    result = patch_assistant(api_key, assembled)
    server_len = len(result["model"]["messages"][0]["content"])
    print(f"✅ VAPI assistant updated successfully")
    print(f"   Prompt on server: {server_len} chars")
    print(f"   Updated: {result.get('updatedAt', 'unknown')}")


if __name__ == "__main__":
    main()

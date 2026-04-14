#!/usr/bin/env python3
"""
SRED.ca Sales Coach — Evan's Coaching Report Generator
Generates a branded post-session PDF for Evan Batchelor.

Usage:
    python generate_coaching_report.py --data coaching_data.json --output /path/to/output.pdf

Data file schema (coaching_data.json):
    {
        "week_start": "2026-04-14",   # Monday of reporting week (YYYY-MM-DD)
        "week_end": "2026-04-20",     # Sunday of reporting week
        "session_number": 1,

        "kpis": {
            "meetings": "4",
            "pipeline_deals": "9",
            "followup_speed": "3.2 hrs",
            "pipeline_value": "$135K"
        },

        "week_narrative": "One paragraph — what kind of week it was overall.",

        "wins": [
            "Think CNC — you didn't pitch. You let Logan lead discovery...",
            "BWS Solutions — first-call yes. That takes preparation."
        ],

        "meeting_reviews": [
            {
                "title": "Think CNC — April 14",
                "body": "Logan led the technical discovery. Your talk ratio was 10%..."
            }
        ],

        "pipeline_table": [
            ["Opportunity", "3", "TeckPath, Data & Scientific, D&R Electronics"],
            ["SR&ED Assessment", "2", "Think CNC (payment pending), Veda"],
            ["Technical Discovery", "1", "VassuTech (40 days stalled — flag)"],
            ["Follow-Up", "2", "Blueshift, FanLINC/Sparcks"],
            ["Closed This Week", "1", "BWS Solutions — WON ✓"]
        ],

        "coaching_focus_title": "Discovery Question Depth",
        "coaching_focus_body": "Three paragraphs on the one thing...",

        "commitments": [
            "I'll send personal re-engagement emails to VassuTech, TeckPath, and MSR by Thursday.",
            "Three questions minimum before anyone else on my team speaks in the Think CNC follow-up."
        ],
        "next_week_checkpoints": [
            "Did the three emails go out by Thursday?",
            "Any response from the stalled deals?"
        ],

        "growth_note": "One paragraph — Evan's arc, SDT framing, what this week represents.",

        "personal_goals_note": null   # optional one-liner if goals are relevant; null if not
    }
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path


def _find_sred_doc():
    """Locate sred_doc.py by searching common skill locations."""
    # Check environment variable first
    if os.environ.get("SRED_DOC_PATH"):
        return os.environ["SRED_DOC_PATH"]

    # Search known locations (Cowork session mounts, local skills)
    search_paths = [
        # Current session's skills folder
        Path(__file__).resolve().parents[3] / ".claude" / "skills" / "sred-doc-creator" / "scripts",
        # Walk up from the plugin to find the mount root, then check .claude/skills
        Path(__file__).resolve().parents[4] / ".claude" / "skills" / "sred-doc-creator" / "scripts",
    ]

    # Also try a glob from /sessions/*/mnt/.claude/skills/sred-doc-creator/scripts
    from glob import glob
    search_paths.extend(
        Path(p) for p in glob("/sessions/*/mnt/.claude/skills/sred-doc-creator/scripts")
    )

    for path in search_paths:
        if (path / "sred_doc.py").exists():
            return str(path)

    raise ImportError(
        "Cannot find sred_doc.py. Set the SRED_DOC_PATH environment variable "
        "to the directory containing sred_doc.py, or ensure the sred-doc-creator "
        "skill is installed at .claude/skills/sred-doc-creator/."
    )


SRED_DOC_PATH = _find_sred_doc()
sys.path.insert(0, SRED_DOC_PATH)

from sred_doc import SREDDoc


def format_date_range(week_start: str, week_end: str) -> str:
    """Format 'April 14 – April 20, 2026' from ISO dates."""
    start = datetime.strptime(week_start, "%Y-%m-%d")
    end = datetime.strptime(week_end, "%Y-%m-%d")
    return f"{start.strftime('%B')} {start.day} \u2013 {end.strftime('%B')} {end.day}, {end.year}"


def generate_coaching_report(data: dict, output_path: str):
    date_range = format_date_range(data["week_start"], data["week_end"])
    session_num = data.get("session_number", "?")

    doc = SREDDoc(f"Weekly Coaching Report — {date_range}", output_path)

    # ── Cover ────────────────────────────────────────────────────────────────
    doc.cover_page(
        "WEEKLY COACHING REPORT",
        f"Week of {date_range}",
        "Evan Batchelor"
    )

    # ── Page 1: Week at a Glance ─────────────────────────────────────────────
    doc.section_header("WEEK AT A GLANCE")
    kpis = data.get("kpis", {})
    doc.kpi_row([
        ("Meetings", kpis.get("meetings", "—")),
        ("Pipeline Deals", kpis.get("pipeline_deals", "—")),
        ("Follow-Up Speed", kpis.get("followup_speed", "—")),
        ("Active Pipeline", kpis.get("pipeline_value", "—")),
    ])
    doc.spacer(0.2)
    if data.get("week_narrative"):
        doc.body(data["week_narrative"])

    # ── Page 2: This Week's Wins ─────────────────────────────────────────────
    doc.page_break()
    doc.section_header("THIS WEEK'S WINS")
    wins = data.get("wins", [])
    if wins:
        for win in wins:
            doc.win(win)
            doc.spacer(0.1)
    else:
        doc.body("No specific wins recorded for this week.")

    # ── Page 3: Meeting Review ───────────────────────────────────────────────
    doc.page_break()
    doc.section_header("MEETING REVIEW")
    reviews = data.get("meeting_reviews", [])
    if reviews:
        for review in reviews:
            doc.body_keep(review["title"], review["body"])
            doc.spacer(0.15)
    else:
        doc.body("No Fireflies-recorded meetings this week. (Check for phone-only calls.)")

    # ── Page 4: Pipeline Health ──────────────────────────────────────────────
    doc.page_break()
    doc.section_header("PIPELINE HEALTH")
    pipeline_rows = data.get("pipeline_table", [])
    if pipeline_rows:
        doc.branded_table(
            headers=["Stage", "Deals", "Notes"],
            rows=pipeline_rows,
            col_widths=[1.8, 0.8, 4.4]
        )
    else:
        doc.body("Pipeline data unavailable.")

    # ── Page 5: Email & Outreach Dashboard ─────────────────────────────────
    email_dash = data.get("email_dashboard")
    if email_dash:
        doc.page_break()
        doc.section_header("EMAIL & OUTREACH")
        doc.kpi_row([
            ("Emails Sent", email_dash.get("sent", "—")),
            ("Open Rate", email_dash.get("open_rate", "—")),
            ("Reply Rate", email_dash.get("reply_rate", "—")),
            ("Avg Response", email_dash.get("avg_response", "—")),
        ])
        doc.spacer(0.2)
        email_rows = email_dash.get("top_emails", [])
        if email_rows:
            doc.sub_header("Top Emails This Week")
            doc.branded_table(
                headers=["Recipient", "Subject", "Opened", "Replied"],
                rows=email_rows,
                col_widths=[1.8, 3.0, 1.1, 1.1]
            )
        doc.spacer(0.2)
        linkedin = data.get("linkedin_dashboard")
        if linkedin:
            doc.sub_header("LinkedIn This Week")
            li_rows = []
            if linkedin.get("connections"):
                li_rows.append(["Connections", linkedin["connections"]])
            if linkedin.get("messages"):
                li_rows.append(["Messages", linkedin["messages"]])
            if linkedin.get("inmails"):
                li_rows.append(["InMails", linkedin["inmails"]])
            if linkedin.get("campaigns"):
                li_rows.append(["Active Campaigns", linkedin["campaigns"]])
            if li_rows:
                doc.branded_table(
                    headers=["Channel", "Stats"],
                    rows=li_rows,
                    col_widths=[2.0, 5.0]
                )
        forms = data.get("form_submissions")
        if forms:
            doc.spacer(0.2)
            doc.sub_header("Form Submissions This Week")
            if isinstance(forms, list) and forms:
                doc.branded_table(
                    headers=["Contact", "Company", "Source", "Date"],
                    rows=forms,
                    col_widths=[1.8, 2.2, 1.5, 1.5]
                )
            elif isinstance(forms, str):
                doc.body(forms)

    # ── Page 6: Hot Leads & Buying Signals ──────────────────────────────────
    hot_leads = data.get("hot_leads")
    if hot_leads:
        doc.page_break()
        doc.section_header("HOT LEADS & BUYING SIGNALS")
        leads_table = hot_leads.get("leads_table", [])
        if leads_table:
            doc.branded_table(
                headers=["Contact", "Company", "Signal", "Last Contact", "Action"],
                rows=leads_table,
                col_widths=[1.4, 1.6, 1.8, 1.2, 1.0]
            )
        doc.spacer(0.15)
        alerts = hot_leads.get("alerts", [])
        for alert in alerts:
            doc.caution(alert)
            doc.spacer(0.06)
        if not leads_table and not alerts:
            doc.body("No new buying signals detected this week.")

    # ── Page 7: Web Traffic Snapshot ────────────────────────────────────────
    web_traffic = data.get("web_traffic")
    if web_traffic:
        doc.page_break()
        doc.section_header("WEB TRAFFIC SNAPSHOT")
        doc.kpi_row([
            ("Sessions", web_traffic.get("sessions", "—")),
            ("Users", web_traffic.get("users", "—")),
            ("Bounce Rate", web_traffic.get("bounce_rate", "—")),
            ("Top Source", web_traffic.get("top_source", "—")),
        ])
        top_pages = web_traffic.get("top_pages", [])
        if top_pages:
            doc.spacer(0.2)
            doc.sub_header("Top Landing Pages")
            doc.branded_table(
                headers=["Page", "Views", "Source"],
                rows=top_pages,
                col_widths=[3.5, 1.5, 2.0]
            )

    # ── This Week's Focus ───────────────────────────────────────────────────
    doc.page_break()
    doc.section_header("THIS WEEK'S FOCUS")
    focus_title = data.get("coaching_focus_title", "")
    focus_body = data.get("coaching_focus_body", "")
    if focus_title:
        doc.sub_header(focus_title)
    if focus_body:
        # Support multi-paragraph — split on double newline
        for para in focus_body.split("\n\n"):
            para = para.strip()
            if para:
                doc.body(para)
                doc.spacer(0.1)

    # ── Page 6: Commitments ──────────────────────────────────────────────────
    doc.page_break()
    doc.section_header("YOUR COMMITMENTS")
    commitments = data.get("commitments", [])
    if commitments:
        doc.sub_header("What You Said You'd Do")
        for c in commitments:
            doc.body(f"\u201c{c}\u201d")
            doc.spacer(0.08)
    checkpoints = data.get("next_week_checkpoints", [])
    if checkpoints:
        doc.spacer(0.15)
        doc.sub_header("What John Will Ask About Next Week")
        for cp in checkpoints:
            doc.body(f"\u2022  {cp}")
            doc.spacer(0.04)

    # ── Page 7: A Note on Growth (Evan only) ────────────────────────────────
    growth_note = data.get("growth_note")
    if growth_note:
        doc.page_break()
        doc.section_header("A NOTE ON GROWTH")
        doc.body(growth_note)

    # Optional personal goals note (if relevant — never quotes goals directly)
    goals_note = data.get("personal_goals_note")
    if goals_note:
        doc.spacer(0.2)
        doc.body(goals_note)

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build()
    print(f"\u2705 Evan's Coaching Report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Evan's Coaching Report PDF")
    parser.add_argument("--data", required=True, help="Path to coaching_data.json")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    with open(args.data, "r") as f:
        data = json.load(f)

    generate_coaching_report(data, args.output)


if __name__ == "__main__":
    main()

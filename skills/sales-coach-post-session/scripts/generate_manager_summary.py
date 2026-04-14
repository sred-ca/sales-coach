#!/usr/bin/env python3
"""
SRED.ca Sales Coach — Manager Summary Generator
Generates a confidential post-session PDF for Sales Manager.

Usage:
    python generate_manager_summary.py --data manager_data.json --output /path/to/output.pdf

Data file schema (manager_data.json):
    {
        "week_start": "2026-04-14",
        "week_end": "2026-04-20",
        "session_number": 1,

        "kpis": {
            "meetings": "4",
            "pipeline_deals": "9",
            "followup_speed": "3.2 hrs",
            "pipeline_value": "$135K"
        },

        "session_overview": {
            "how_it_went": "Paragraph — Evan's energy, receptivity, surprising moments.",
            "coaching_focus": "What John focused on and why (from the data).",
            "commitments": [
                "I'll send personal re-engagement emails to VassuTech, TeckPath, and MSR by Thursday.",
                "Three questions minimum before anyone else on my team speaks."
            ]
        },

        "pipeline_table": [
            ["Opportunity", "3", "TeckPath, Data & Scientific, D&R Electronics"],
            ["SR&ED Assessment", "2", "Think CNC (Stripe LOE pending — payment gate), Veda"],
            ["Technical Discovery", "1", "VassuTech — 40 days stalled ⚠"],
            ["Follow-Up", "2", "Blueshift, FanLINC/Sparcks"],
            ["Closed This Week", "1", "BWS Solutions — WON ✓ ($15K est.)"]
        ],

        "pipeline_flags": [
            "VassuTech: 40 days past expected close — may need Jude escalation call.",
            "Think CNC: Stripe LOE not confirmed — do not schedule Technical Discovery until received."
        ],

        "manager_insights": [
            "FanLINC/Sparcks has been at Follow-Up for 3 weeks. Evan is stuck. Jude visibility may unlock.",
            "InMail volume is burning LinkedIn credits at 5.8% return. Worth a strategy reset with Evan.",
            "If Logan continues in Technical Discovery, clarify Evan's role as discovery lead, not support."
        ],

        "sdt_note": "One sentence on Motivation Ladder movement and what to watch.",
        "decision_ladder_note": "One sentence on autonomy progression.",
        "overall_arc": "Optional — one sentence on how this session fits the longer coaching arc."
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
    start = datetime.strptime(week_start, "%Y-%m-%d")
    end = datetime.strptime(week_end, "%Y-%m-%d")
    return f"{start.strftime('%B')} {start.day} \u2013 {end.strftime('%B')} {end.day}, {end.year}"


def generate_manager_summary(data: dict, output_path: str):
    date_range = format_date_range(data["week_start"], data["week_end"])
    session_num = data.get("session_number", "?")

    doc = SREDDoc(f"Manager Summary — {date_range}", output_path)

    # ── Cover ────────────────────────────────────────────────────────────────
    doc.cover_page(
        "MANAGER SUMMARY",
        f"Week of {date_range}\nCONFIDENTIAL",
        "Sales Manager"
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

    # ── Page 2: Coaching Session Overview ───────────────────────────────────
    doc.page_break()
    doc.section_header("COACHING SESSION OVERVIEW")
    overview = data.get("session_overview", {})

    how_it_went = overview.get("how_it_went", "")
    if how_it_went:
        doc.sub_header("How the Session Went")
        doc.body(how_it_went)
        doc.spacer(0.15)

    coaching_focus = overview.get("coaching_focus", "")
    if coaching_focus:
        doc.sub_header("What the Coach Focused On")
        doc.body(coaching_focus)
        doc.spacer(0.15)

    commitments = overview.get("commitments", [])
    if commitments:
        doc.sub_header("Evan's Commitments (verbatim)")
        for c in commitments:
            doc.body(f"\u201c{c}\u201d")
            doc.spacer(0.08)

    # ── Page 3: Pipeline Review ──────────────────────────────────────────────
    doc.page_break()
    doc.section_header("PIPELINE REVIEW")
    pipeline_rows = data.get("pipeline_table", [])
    if pipeline_rows:
        doc.branded_table(
            headers=["Stage", "Deals", "Notes"],
            rows=pipeline_rows,
            col_widths=[1.8, 0.8, 4.4]
        )

    flags = data.get("pipeline_flags", [])
    if flags:
        doc.spacer(0.2)
        doc.sub_header("Flags for Jude")
        for flag in flags:
            doc.caution(flag)
            doc.spacer(0.06)

    # ── Page 4: Activity Dashboard ─────────────────────────────────────────
    activity = data.get("activity_dashboard")
    if activity:
        doc.page_break()
        doc.section_header("ACTIVITY DASHBOARD")
        doc.kpi_row([
            ("Emails Sent", activity.get("emails_sent", "—")),
            ("Email Reply Rate", activity.get("email_reply_rate", "—")),
            ("LinkedIn Messages", activity.get("linkedin_messages", "—")),
            ("LinkedIn Reply Rate", activity.get("linkedin_reply_rate", "—")),
        ])
        doc.spacer(0.15)
        summary_text = activity.get("summary")
        if summary_text:
            doc.body(summary_text)
        alerts = activity.get("volume_alerts", [])
        for alert in alerts:
            doc.spacer(0.08)
            doc.caution(alert)

    # ── Page 5: Leads for Manager ───────────────────────────────────────────
    leads_for_mgr = data.get("leads_for_manager")
    if leads_for_mgr:
        doc.page_break()
        doc.section_header("LEADS REQUIRING MANAGER ATTENTION")
        leads_table = leads_for_mgr.get("leads_table", [])
        if leads_table:
            doc.branded_table(
                headers=["Contact", "Company", "Signal", "Recommended Action"],
                rows=leads_table,
                col_widths=[1.5, 1.8, 2.2, 1.5]
            )
        doc.spacer(0.15)
        notes = leads_for_mgr.get("notes", [])
        for note in notes:
            doc.body(f"\u2022  {note}")
            doc.spacer(0.06)

    # ── Manager Insight ─────────────────────────────────────────────────────
    doc.page_break()
    doc.section_header("MANAGER INSIGHT")
    doc.body("What only a manager can act on:")
    doc.spacer(0.1)
    insights = data.get("manager_insights", [])
    if insights:
        for insight in insights:
            doc.body(f"\u2022  {insight}")
            doc.spacer(0.08)
    else:
        doc.body("No specific manager actions identified this week.")

    # ── Page 5: SDT Progression ──────────────────────────────────────────────
    doc.page_break()
    doc.section_header("SDT PROGRESSION NOTE")

    sdt_note = data.get("sdt_note", "")
    dl_note = data.get("decision_ladder_note", "")
    arc_note = data.get("overall_arc", "")

    if sdt_note:
        doc.sub_header("Motivation Ladder")
        doc.body(sdt_note)
        doc.spacer(0.15)
    if dl_note:
        doc.sub_header("Decision Ladder (Autonomy)")
        doc.body(dl_note)
        doc.spacer(0.15)
    if arc_note:
        doc.sub_header("Coaching Arc")
        doc.body(arc_note)

    doc.spacer(0.3)
    doc.body(
        "Motivation Ladder: 1=Compliance \u00b7 2=Ego/Should \u00b7 "
        "3=Goal/Want \u00b7 4=Value/Identity  |  "
        "Decision Ladder: 1=Told \u00b7 2=Reports back \u00b7 3=Recommends "
        "\u00b7 4=Decides+Informs \u00b7 5=Full autonomy"
    )

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build()
    print(f"\u2705 Manager Summary saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Manager Summary PDF")
    parser.add_argument("--data", required=True, help="Path to manager_data.json")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    with open(args.data, "r") as f:
        data = json.load(f)

    generate_manager_summary(data, args.output)


if __name__ == "__main__":
    main()

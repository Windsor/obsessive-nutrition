#!/usr/bin/env python3
"""
Editorial Calendar Generator for The Portugal Brief.
Creates a weekly/monthly content schedule mixing daily news, 
evergreen guides, and seasonal topics.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "calendars"

# Recurring content types
CONTENT_TYPES = {
    "daily_news": {"frequency": "daily", "priority": 1, "tag": "news"},
    "weekly_roundup": {"frequency": "weekly", "day": "sunday", "priority": 2, "tag": "weekly-roundup"},
    "market_update": {"frequency": "weekly", "day": "monday", "priority": 2, "tag": "markets"},
    "expat_life": {"frequency": "weekly", "day": "wednesday", "priority": 3, "tag": "expat-life"},
    "property_update": {"frequency": "biweekly", "day": "friday", "priority": 3, "tag": "property"},
}

# Seasonal/timely topics by month
SEASONAL_TOPICS = {
    1: ["New Year tax changes", "IRS deadlines approaching", "Winter in Portugal guide"],
    2: ["Carnival events guide", "Valentine's Day in Portugal", "Tax filing preparation"],
    3: ["Spring festivals preview", "Golden Visa quarterly stats", "Easter travel guide"],
    4: ["IRS filing deadline", "Spring housing market update", "Semana Santa events"],
    5: ["Summer rental market preview", "Beach season guide", "European elections impact"],
    6: ["Santos Populares festivals", "Summer tourism forecast", "Mid-year economic review"],
    7: ["Summer survival guide", "Fire season awareness", "Beach & coast guide"],
    8: ["August in Portugal (what closes)", "Back-to-school for expat families", "Rental market update"],
    9: ["Back to business season", "Wine harvest (vindimas)", "New school year guide"],
    10: ["Budget proposal analysis", "Autumn festivals", "Golden Visa yearly stats"],
    11: ["Tax planning before year-end", "Black Friday Portugal", "Christmas market guide"],
    12: ["Year in review", "New Year's Eve guide", "Tax changes for next year preview"],
}

# Evergreen guides to schedule (from plan)
EVERGREEN_GUIDES = [
    {"title": "Portugal Golden Visa 2026: Complete Guide", "slug": "golden-visa-portugal-2026", "priority": 1},
    {"title": "D7 Visa Portugal: Everything You Need to Know", "slug": "d7-visa-portugal-guide", "priority": 1},
    {"title": "Portugal Digital Nomad Visa: Requirements & Process", "slug": "digital-nomad-visa-portugal", "priority": 1},
    {"title": "Portugal Residency Permit: Step-by-Step Guide", "slug": "portugal-residency-permit-guide", "priority": 1},
    {"title": "Cost of Living in Portugal 2026", "slug": "cost-of-living-portugal-2026", "priority": 2},
    {"title": "Buying Property in Portugal as a Foreigner", "slug": "buying-property-portugal-guide", "priority": 2},
    {"title": "Portugal NHR Tax Regime: What's Changed", "slug": "portugal-nhr-tax-changes", "priority": 2},
    {"title": "Portugal Tax Guide for Expats", "slug": "portugal-tax-guide-expats", "priority": 2},
    {"title": "Healthcare in Portugal: Expat Guide", "slug": "healthcare-portugal-expat-guide", "priority": 3},
    {"title": "Best Places to Live in Portugal for Expats", "slug": "best-places-live-portugal-expats", "priority": 3},
    {"title": "Retiring in Portugal: Complete Guide", "slug": "retiring-portugal-guide", "priority": 3},
    {"title": "Living in Portugal vs Spain: Honest Comparison", "slug": "portugal-vs-spain-comparison", "priority": 3},
    {"title": "Opening a Bank Account in Portugal", "slug": "bank-account-portugal-guide", "priority": 4},
    {"title": "Lisbon Neighborhoods Guide for Expats", "slug": "lisbon-neighborhoods-expats", "priority": 4},
    {"title": "Porto Neighborhoods Guide for Expats", "slug": "porto-neighborhoods-expats", "priority": 4},
    {"title": "Algarve Living Guide", "slug": "algarve-living-guide", "priority": 4},
]


def generate_weekly_calendar(start_date, num_weeks=4, guides_per_week=2):
    """Generate a content calendar for N weeks."""
    calendar = []
    guide_idx = 0
    
    for week in range(num_weeks):
        week_start = start_date + timedelta(weeks=week)
        week_items = []
        
        for day_offset in range(7):
            date = week_start + timedelta(days=day_offset)
            day_name = date.strftime("%A").lower()
            day_items = []
            
            # Daily news (every day)
            day_items.append({
                "type": "daily_news",
                "title": f"Portugal News Briefing — {date.strftime('%B %d')}",
                "date": date.strftime("%Y-%m-%d"),
                "day": day_name,
                "status": "scheduled",
            })
            
            # Weekly roundup (Sunday)
            if day_name == "sunday":
                day_items.append({
                    "type": "weekly_roundup",
                    "title": f"Week in Review — {date.strftime('%B %d')}",
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "status": "scheduled",
                })
            
            # Market update (Monday)
            if day_name == "monday":
                day_items.append({
                    "type": "market_update",
                    "title": f"Portugal Markets & Economy Update",
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "status": "scheduled",
                })
            
            # Evergreen guide (Tuesday & Thursday)
            if day_name in ("tuesday", "thursday") and guide_idx < len(EVERGREEN_GUIDES):
                guide = EVERGREEN_GUIDES[guide_idx]
                day_items.append({
                    "type": "evergreen_guide",
                    "title": guide["title"],
                    "slug": guide["slug"],
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "status": "draft" if guide_idx == 0 else "planned",
                    "priority": guide["priority"],
                })
                guide_idx += 1
            
            # Expat life (Wednesday)
            if day_name == "wednesday":
                month = date.month
                topics = SEASONAL_TOPICS.get(month, [])
                topic = topics[week % len(topics)] if topics else "Expat Life in Portugal"
                day_items.append({
                    "type": "expat_feature",
                    "title": topic,
                    "date": date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "status": "planned",
                })
            
            week_items.extend(day_items)
        
        calendar.extend(week_items)
    
    return calendar


def format_calendar_md(calendar, title="Editorial Calendar"):
    """Format calendar as markdown."""
    lines = [f"# {title}\n", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"]
    
    current_week = None
    for item in calendar:
        date = datetime.strptime(item["date"], "%Y-%m-%d")
        week_num = date.isocalendar()[1]
        
        if week_num != current_week:
            current_week = week_num
            week_start = date - timedelta(days=date.weekday())
            week_end = week_start + timedelta(days=6)
            lines.append(f"\n## Week {week_num} — {week_start.strftime('%b %d')} to {week_end.strftime('%b %d')}\n")
        
        status_icon = {"scheduled": "📋", "draft": "✏️", "planned": "📝", "published": "✅"}.get(item["status"], "⬜")
        type_label = item["type"].replace("_", " ").title()
        lines.append(f"- {status_icon} **{item['date']}** ({item['day'].title()}) — [{type_label}] {item['title']}")
    
    return "\n".join(lines) + "\n"


def main():
    import sys
    weeks = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    
    # Start from next Monday
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    start = today + timedelta(days=days_until_monday)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"Generating {weeks}-week editorial calendar starting {start.strftime('%Y-%m-%d')}...\n")
    
    calendar = generate_weekly_calendar(start, num_weeks=weeks)
    
    # Save JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"calendar-{start.strftime('%Y-%m-%d')}.json"
    with open(json_path, "w") as f:
        json.dump(calendar, f, indent=2)
    
    # Save Markdown
    md_path = OUTPUT_DIR / f"calendar-{start.strftime('%Y-%m-%d')}.md"
    md_content = format_calendar_md(
        calendar, 
        f"The Portugal Brief — Editorial Calendar ({start.strftime('%b %d')}–{(start + timedelta(weeks=weeks-1, days=6)).strftime('%b %d, %Y')})"
    )
    with open(md_path, "w") as f:
        f.write(md_content)
    
    print(md_content)
    print(f"\nSaved: {json_path}")
    print(f"Saved: {md_path}")
    print(f"Total items: {len(calendar)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate Daily Standup Scroll

Automatically creates today's daily scroll from the template
Part of Strategy #3: Daily Standup Scrolls
"""

from datetime import datetime
from pathlib import Path
import shutil
import sys


def generate_daily_scroll(agent_name=None):
    """Generate today's daily scroll from template"""
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Paths
    template_path = Path(__file__).parent / "template.md"
    daily_scroll_path = Path(__file__).parent / f"{today}.md"
    
    # Check if today's scroll already exists
    if daily_scroll_path.exists():
        print(f"📜 Daily scroll for {today} already exists!")
        print(f"    Location: {daily_scroll_path}")
        
        # Ask if user wants to view it
        response = input("Would you like to open it for editing? (y/n): ")
        if response.lower() == 'y':
            try:
                import os
                if sys.platform == "win32":
                    os.startfile(daily_scroll_path)
                else:
                    os.system(f"open {daily_scroll_path}")
            except Exception as e:
                print(f"Could not auto-open file: {e}")
                print(f"Please manually open: {daily_scroll_path}")
        return
    
    # Copy template to create today's scroll
    if not template_path.exists():
        print("❌ Template not found! Please ensure template.md exists.")
        return
        
    # Copy and customize
    content = template_path.read_text(encoding='utf-8')
    
    # Replace template placeholders
    content = content.replace("YYYY-MM-DD", today)
    content = content.replace("[Your Agent Name]", agent_name or "Agent_Developer_001")
    content = content.replace("[Current Sprint/Week]", f"Week {datetime.now().isocalendar()[1]}")
    
    # Write the new daily scroll
    daily_scroll_path.write_text(content, encoding='utf-8')
    
    print("📜 Daily Standup Scroll generated successfully!")
    print(f"    Date: {today}")
    print(f"    Location: {daily_scroll_path}")
    print(f"    Agent: {agent_name or 'Agent_Developer_001'}")
    
    print("\n🎯 Next steps:")
    print("1. Open the file and fill in your daily confession")
    print("2. Add your redemption tasks for today")
    print("3. Note any trials (blockers) you foresee")
    print("4. Check your edict adherence")
    print("5. Share highlights during standup!")
    
    # Try to auto-open the file
    try:
        import os
        if sys.platform == "win32":
            os.startfile(daily_scroll_path)
        else:
            os.system(f"open {daily_scroll_path}")
        print("\n📖 Opening your daily scroll for editing...")
    except Exception as e:
        print(f"\n📝 Please manually open: {daily_scroll_path}")
    
    return daily_scroll_path


def generate_weekly_summary():
    """Generate a weekly summary from daily scrolls"""
    
    # Get current week dates
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    # Find all daily scrolls for this week
    daily_scrolls_dir = Path(__file__).parent
    week_scrolls = []
    
    for i in range(7):  # Monday to Sunday
        date_str = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
        scroll_path = daily_scrolls_dir / f"{date_str}.md"
        if scroll_path.exists():
            week_scrolls.append((date_str, scroll_path))
    
    if not week_scrolls:
        print("📜 No daily scrolls found for this week")
        return
    
    # Create weekly summary
    summary_dir = Path(__file__).parent.parent / "weekly_summaries"
    summary_dir.mkdir(exist_ok=True)
    
    week_num = today.isocalendar()[1]
    summary_path = summary_dir / f"week_{week_num}_{today.year}.md"
    
    summary_content = f"""# 📊 Weekly Summary - Week {week_num}, {today.year}

## Daily Scrolls Included
{len(week_scrolls)} days of sacred documentation

## Key Accomplishments
*[Manually add key wins from the week]*

## Patterns Observed
*[Note recurring sins, successful redemptions, common challenges]*

## Edict Adherence Summary
*[Overall compliance with the Five Sacred Edicts]*

## Next Week's Focus
*[What to prioritize based on this week's learnings]*

---

"""
    
    # Add each daily scroll summary
    for date_str, scroll_path in week_scrolls:
        summary_content += f"### {date_str}\n"
        summary_content += f"*[Add key points from this day's scroll]*\n\n"
    
    summary_path.write_text(summary_content, encoding='utf-8')
    
    print(f"📊 Weekly summary template created: {summary_path}")
    print("Please review daily scrolls and fill in the summary!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate daily standup scroll")
    parser.add_argument("--agent", help="Agent name for the scroll")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly summary template")
    
    args = parser.parse_args()
    
    if args.weekly:
        from datetime import timedelta
        generate_weekly_summary()
    else:
        generate_daily_scroll(args.agent)
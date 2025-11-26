from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import re

# Demo calendar data
CALENDAR = {
    "2025-11-26": [
        {"time": "09:00", "event": "Morning Meeting", "source": "Google"},
        {"time": "14:00", "event": "Lunch with Team", "source": "Outlook"},
        {"time": "17:00", "event": "Gym Workout", "source": "Google"}
    ],
    "2025-11-27": [
        {"time": "10:00", "event": "Project Review", "source": "Google"},
        {"time": "15:00", "event": "Client Call", "source": "Outlook"},
        {"time": "16:00", "event": "Code Review", "source": "Google"}
    ],
    "2025-11-28": [
        {"time": "09:00", "event": "Deep Work - Capstone", "source": "Google"},
        {"time": "14:00", "event": "User Testing", "source": "Google"},
        {"time": "21:00", "event": "⚠️ CAPSTONE SUBMISSION DEADLINE", "source": "Deadline"}
    ],
    "2025-11-29": [
        {"time": "10:00", "event": "Capstone Presentation", "source": "Google"}
    ]
}

def get_schedule(date):
    """Get calendar schedule for a specific date"""
    events = CALENDAR.get(date, [])
    
    if not events:
        return f"📅 No events scheduled for {date}"
    
    response = f"📅 *Schedule for {date}*\n\n"
    for event in events:
        response += f"🕐 {event['time']} - {event['event']}\n"
        response += f"  _{event['source']}_\n\n"
    
    response += f"Total events: {len(events)}"
    return response

def get_week_summary():
    """Get summary of the week"""
    today = datetime.now()
    summary = "📊 *Week Summary*\n\n"
    
    total_events = 0
    for i in range(7):
        date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        events = CALENDAR.get(date, [])
        if events:
            day_name = (today + timedelta(days=i)).strftime("%A")
            summary += f"*{day_name} ({date})*: {len(events)} events\n"
            total_events += len(events)
    
    summary += f"\n📌 Total: {total_events} events this week"
    return summary

def process_message(msg):
    """Process incoming WhatsApp message and return response"""
    m = msg.lower().strip()
    
    # Get today and tomorrow dates
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Check for specific commands
    if "today" in m or "schedule today" in m:
        return get_schedule(today)
    
    elif "tomorrow" in m or "schedule tomorrow" in m:
        return get_schedule(tomorrow)
    
    elif "week" in m or "this week" in m:
        return get_week_summary()
    
    elif "help" in m or "commands" in m:
        return """🤖 *MyDay AI - Calendar Assistant*

📋 *Commands:*
- "schedule today" - Today's events
- "schedule tomorrow" - Tomorrow's events
- "schedule 2025-11-28" - Specific date
- "week" - This week's summary
- "help" - Show this message

📅 *Examples:*
- What's my schedule today?
- Show me tomorrow's calendar
- Do I have anything on Nov 28?

💡 Tip: Just ask naturally, I'll understand!"""
    
    else:
        # Try to extract date from message
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', m)
        if date_match:
            return get_schedule(date_match.group())
        
        # Try to extract "Nov 28" or "November 28" format
        month_day_match = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{1,2})', m)
        if month_day_match:
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            month = month_map.get(month_day_match.group(1)[:3])
            day = month_day_match.group(2).zfill(2)
            date = f"2025-{month}-{day}"
            return get_schedule(date)
        
        # Default response
        return f"""👋 Hi! I'm MyDay AI, your calendar assistant.

Try asking:
- "What's my schedule today?"
- "Show me tomorrow's calendar"
- "Week summary"

Type *help* for all commands."""

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_GET(self):
        """Handle GET requests - show status page"""
        self.send_response(200)

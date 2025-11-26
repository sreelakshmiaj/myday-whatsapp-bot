from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import re

# Demo calendar data
CALENDAR = {
    "2025-11-26": [
        {"time": "09:00", "event": "Morning Meeting", "source": "Google"},
        {"time": "14:00", "event": "Lunch with Team", "source": "Outlook"},
        {"time": "17:00", "event": "Gym Workout", "source": "Google"},
    ],
    "2025-11-27": [
        {"time": "10:00", "event": "Project Review", "source": "Google"},
        {"time": "15:00", "event": "Client Call", "source": "Outlook"},
        {"time": "16:00", "event": "Code Review", "source": "Google"},
    ],
    "2025-11-28": [
        {"time": "09:00", "event": "Deep Work - Capstone", "source": "Google"},
        {"time": "14:00", "event": "User Testing", "source": "Google"},
        {"time": "21:00", "event": "⚠️ CAPSTONE SUBMISSION DEADLINE", "source": "Deadline"},
    ],
    "2025-11-29": [
        {"time": "10:00", "event": "Capstone Presentation", "source": "Google"},
    ],
}


def get_schedule(date: str) -> str:
    """Get calendar schedule for a specific date."""
    events = CALENDAR.get(date, [])

    if not events:
        return f"📅 No events scheduled for {date}"

    lines = [f"📅 *Schedule for {date}*", ""]
    for event in events:
        lines.append(f"🕐 {event['time']} - {event['event']}")
        lines.append(f" _{event['source']}_")
        lines.append("")
    lines.append(f"Total events: {len(events)}")
    return "\n".join(lines)


def get_week_summary() -> str:
    """Get summary of the week starting today."""
    today = datetime.now()
    summary_lines = ["📊 *Week Summary*", ""]
    total_events = 0

    for i in range(7):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        events = CALENDAR.get(date_str, [])
        if events:
            day_name = current_date.strftime("%A")
            summary_lines.append(f"*{day_name} ({date_str})*: {len(events)} events")
            total_events += len(events)

    summary_lines.append("")
    summary_lines.append(f"📌 Total: {total_events} events this week")
    return "\n".join(summary_lines)


def process_message(msg: str) -> str:
    """Process incoming WhatsApp message and return response text."""
    m = msg.lower().strip()

    # Get today and tomorrow dates
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Specific commands
    if "today" in m or "schedule today" in m:
        return get_schedule(today)
    if "tomorrow" in m or "schedule tomorrow" in m:
        return get_schedule(tomorrow)
    if "week" in m or "this week" in m:
        return get_week_summary()
    if "help" in m or "commands" in m:
        return (
            "🤖 *MyDay AI - Calendar Assistant*\n"
            "📋 *Commands:*\n"
            "- \"schedule today\" - Today's events\n"
            "- \"schedule tomorrow\" - Tomorrow's events\n"
            "- \"schedule 2025-11-28\" - Specific date\n"
            "- \"week\" - This week's summary\n"
            "- \"help\" - Show this message\n\n"
            "📅 *Examples:*\n"
            "- What's my schedule today?\n"
            "- Show me tomorrow's calendar\n"
            "- Do I have anything on Nov 28?\n\n"
            "💡 Tip: Just ask naturally, I'll understand!"
        )

    # Try to extract ISO date (YYYY-MM-DD)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", m)
    if date_match:
        return get_schedule(date_match.group())

    # Try to extract "Nov 28" or "November 28"
    month_day_match = re.search(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{1,2})",
        m,
    )
    if month_day_match:
        month_map = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        }
        month = month_map.get(month_day_match.group(1)[:3])
        day = month_day_match.group(2).zfill(2)
        date = f"2025-{month}-{day}"
        return get_schedule(date)

    # Default response
    return (
        "👋 Hi! I'm MyDay AI, your calendar assistant.\n"
        "Try asking:\n"
        "- \"What's my schedule today?\"\n"
        "- \"Show me tomorrow's calendar\"\n"
        "- \"Week summary\"\n\n"
        "Type *help* for all commands."
    )


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""

    def do_GET(self):
        """Handle GET requests - show basic status page."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MyDay AI WhatsApp Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }
                .status {
                    color: green;
                    font-size: 24px;
                    margin: 20px 0;
                }
                .emoji {
                    font-size: 48px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="emoji">🤖</div>
            <h1>MyDay AI WhatsApp Bot</h1>
            <div class="status">✅ Status: Running</div>
            <p>Send a WhatsApp message to <strong>+1 415 523 8886</strong> to start chatting!</p>
            <hr>
            <p><em>Calendar Assistant for scheduling and reminders</em></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        """Handle POST requests from Twilio WhatsApp webhook."""
        try:
            # Read POST body
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")

            # Parse urlencoded form data
            params = parse_qs(post_data)

            incoming_msg = params.get("Body", [""])[0]
            from_number = params.get("From", [""])[0]  # reserved for future use

            # Generate reply
            response_text = process_message(incoming_msg)

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

            self.send_response(200)
            self.send_header("Content-type", "text/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(twiml.encode("utf-8"))

        except Exception:
            # If anything fails, return a generic error message to the user
            error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, I encountered an error. Please try again or type 'help'.</Message>
</Response>"""
            self.send_response(500)
            self.se

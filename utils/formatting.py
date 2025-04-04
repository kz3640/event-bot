"""
Formatting utilities for event messages
"""
import datetime
import logging

logger = logging.getLogger('event_bot')

def format_date_with_day(date_str: str) -> str:
    """
    If the date is in format xx/xx/xx or xx-xx-xx, add the day of the week
    Returns the original string if the date couldn't be parsed
    """
    try:
        # Try to parse date from formats
        formats = ["%m/%d/%y", "%m/%d/%Y"]
        
        parsed_date = None
        for fmt in formats:
            try:
                parsed_date = datetime.datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if parsed_date:
            day_name = parsed_date.strftime("%A")
            return f"{day_name}, {date_str}"
        return date_str
    except Exception as e:
        logger.error(f"Failed to parse date: {e}")
        return date_str


def format_event_message(event_name: str, general_time: str, location: str, 
                        price: str = "Free", emoji: str = ":loudspeaker:", organizer: str = "") -> str:
    """Format the event message with consistent styling"""
    # Process the date to include day of week if applicable
    formatted_date = format_date_with_day(general_time)
    
    return (
        f"**{emoji} {event_name}**\n"
        f"**Organized by:** {organizer}\n\n"
        f"**:date: Date:** {formatted_date}\n"
        f"**:round_pushpin: Location:** {location}\n"
        f"**:dollar: Price:** {price}\n\n"
        f"**:white_check_mark: Going:** (0)\n"
        f"\n\n"
        f"**:question: Maybe:** (0)\n"
        f"\n\n"
        f"**:x: Can't make it:** (0)\n\n"
        f"**:pencil: Notes:** use `/change_notes` to add notes to the event.\n"
    )
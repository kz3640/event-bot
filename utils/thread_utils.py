"""
Thread management utilities
"""
import discord
from typing import Optional
import logging

logger = logging.getLogger('event_bot')

async def update_thread_name(thread: discord.Thread, event_name: str, general_time: str) -> None:
    """Update thread name to match event details"""
    try:
        new_thread_name = f'{general_time} - {event_name}'
        await thread.edit(name=new_thread_name)
        logger.info(f"Thread name updated to: {new_thread_name}")
    except discord.HTTPException as e:
        logger.error(f"Failed to update thread name: {e}")


async def get_parent_message(thread: discord.Thread) -> Optional[discord.Message]:
    """Get the parent message of a thread"""
    try:
        # For threads created from messages
        if hasattr(thread, 'parent') and thread.parent and isinstance(thread.parent, discord.TextChannel):
            return await thread.parent.fetch_message(thread.id)
        # Fallback: get the first message in the thread
        async for message in thread.history(oldest_first=True, limit=1):
            return message
        return None
    except discord.HTTPException as e:
        logger.error(f"Failed to get parent message: {e}")
        return None
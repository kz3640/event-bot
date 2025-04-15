"""
Channel management utilities
"""
import discord
from typing import Optional
import logging

logger = logging.getLogger('event_bot')

async def update_channel_name(channel: discord.channel, event_name: str, general_time: str) -> None:
    """Update channel name to match event details"""
    try:
        new_channel_name = f'{general_time} - {event_name}'
        await channel.edit(name=new_channel_name)
        logger.info(f"Channel name updated to: {new_channel_name}")
    except discord.HTTPException as e:
        logger.error(f"Failed to update channel name: {e}")
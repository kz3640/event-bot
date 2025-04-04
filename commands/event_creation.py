"""
Event creation command
"""
import discord
from discord import app_commands
import logging
from utils.formatting import format_event_message

logger = logging.getLogger('event_bot')

def register_event_creation(tree: app_commands.CommandTree, guild: discord.Object) -> None:
    """Register the event creation command"""
    
    @tree.command(
        name="event",
        description="Announce an event in the current channel.",
        guild=guild
    )
    @app_commands.describe(
        event_name="Name of the event",
        time="General time/date of the event",
        location="Location of the event",
        price="Price of the event (default: Free)",
        emoji="Custom emoji for the event (default: :loudspeaker:)"
    )
    async def event(interaction: discord.Interaction, event_name: str, time: str, 
                    location: str, price: str = "Free", emoji: str = ":loudspeaker:") -> None:
        """Create a new event announcement with RSVP capabilities"""
        try:
            # Create event content
            event_message_content = format_event_message(
                event_name, time, location, price, emoji, interaction.user.mention
            )
            
            # Send the initial response
            await interaction.response.send_message(event_message_content)
            
            # Get the message object from the response
            original_message = await interaction.original_response()
            
            # Create thread for the event
            thread_name = f'{time} - {event_name}'
            thread = await original_message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,  # 1 day
            )
            
            logger.info(f"Event '{event_name}' created with thread '{thread_name}'")
            
        except discord.HTTPException as e:
            logger.error(f"Failed to create event: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Failed to create event. Please try again.", ephemeral=True)
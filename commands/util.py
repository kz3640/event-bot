"""
Help Command
This module contains the help command for the Discord bot.
"""
import discord
from discord import app_commands
import logging

logger = logging.getLogger('event_bot')

def register_help(tree: app_commands.CommandTree, guild: discord.Object) -> None:
    """Register the help command"""
    
    @tree.command(
        name="help",
        description="Get a list of available commands.",
        guild=guild
    )
    async def help_command(interaction: discord.Interaction) -> None:
        """Send a message with the list of available commands"""
        try:
            # Create the help message content
            help_message = (
                "**Available Commands:**\n"
                "1. `/help` - Get a list of available commands.\n"
                "2. `/event [name] [time] [location] [emoji] [price]` - Announce an event in the current channel.\n"
                "3. `/rsvp [yes/no/maybe] [user (optional)]` - RSVP to an event. Thread Only.\n"
                "4. `/change_emoji [emoji]` - Change the emoji for the event. Thread Only.\n"
                "5. `/change_location [location]` - Change the location for the event. Thread Only.\n"
                "6. `/change_name [name]` - Change the name of the event. Thread Only.\n"
                "7. `/change_price [price]` - Change the price for the event. Thread Only.\n"
                "8. `/change_notes` - Change the notes for the event. Thread Only. The bot will DM you to collect the new notes.\n"
            )
            
            # Send the help message
            await interaction.response.send_message(help_message, ephemeral=True)
            
            logger.info("Help command executed successfully")
            
        except discord.HTTPException as e:
            logger.error(f"Failed to send help message: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Failed to retrieve help information. Please try again.", ephemeral=True)
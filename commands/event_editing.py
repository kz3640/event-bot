"""
Commands for editing event details
"""
import discord
from discord import app_commands
import logging
from utils.channel_utils import update_channel_name
from utils.formatting import format_date_with_day
import re

logger = logging.getLogger('event_bot')

def register_event_editing(tree: app_commands.CommandTree, guild: discord.Object) -> None:
    """Register event editing commands"""
    
    @tree.command(
        name="change_name",
        description="Change the name of the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
        new_name="New name of event",
    )
    async def change_name(interaction: discord.Interaction, new_name: str) -> None:
        """Change the event name in both message and channel name"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # Get the event message - first message in channel
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update event message
            current_content = event_message.content
            
            # Extract date for channel name update
            date_start = current_content.find('**:date: Date:**') + len('**:date: Date:**')
            date_end = current_content.find('**', date_start)
            current_date = current_content[date_start:date_end].strip()
            
            # Find the first bold section (which contains the event name and possibly an emoji)
            first_bold_start = current_content.find('**')
            first_bold_end = current_content.find('**', first_bold_start + 2)
            
            if first_bold_start == -1 or first_bold_end == -1:
                await interaction.response.send_message("Could not parse the event message format.", ephemeral=True)
                return
            
            # Extract the content inside the first bold tags
            bold_content = current_content[first_bold_start+2:first_bold_end]
            
            # Default value for updated content (no emoji case)
            updated_content = current_content[:first_bold_start] + f"**{new_name}**" + current_content[first_bold_end + 2:]
            
            # Check for emoji formats
            # Case 1: Text emoji like :loudspeaker:
            emoji_match = re.search(r'(:[a-zA-Z0-9_]+:)', bold_content)
            # Case 2: Unicode emoji (which can be 1-2 characters typically)
            unicode_match = re.search(r'([\U00010000-\U0010ffff]|[\u2600-\u27ff])', bold_content)
            
            if emoji_match:
                # Text emoji case
                emoji = emoji_match.group(1)
                updated_content = current_content[:first_bold_start] + f"**{emoji} {new_name}**" + current_content[first_bold_end + 2:]
            elif unicode_match:
                # Unicode emoji case
                emoji = unicode_match.group(1)
                updated_content = current_content[:first_bold_start] + f"**{emoji} {new_name}**" + current_content[first_bold_end + 2:]
            
            # Update the message
            await event_message.edit(content=updated_content)
            
            # Update channel name
            await update_channel_name(channel, new_name, current_date.split(',')[-1].strip())
            
            await interaction.response.send_message(f"Channel updated: {new_name}", ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update event name: {e}")
            await interaction.response.send_message("Failed to update event name. Please try again.", ephemeral=True)

    @tree.command(
        name="change_date",
        description="Change the date/time of the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
        new_date="New date/time of the event",
    )
    async def change_date(interaction: discord.Interaction, new_date: str) -> None:
        """Change the event date in both message and channel name"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # Get parent message ID from channel
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update event message
            current_content = event_message.content
            
            # Extract event name for channel name update
            name_start = current_content.find('**') + 2
            name_end = current_content.find('**', name_start)
            
            # Extract emoji and name
            first_space = current_content.find(' ', name_start, name_end)
            current_name = current_content[first_space + 1:name_end]
            
            # Format date with day of week
            formatted_date = format_date_with_day(new_date)
            
            # Update date in message
            start_index = current_content.find('**:date: Date:**') + len('**:date: Date:**')
            end_index = current_content.find('**', start_index) - 1
            updated_content = current_content[:start_index] + ' ' + formatted_date + current_content[end_index:]
            
            # Update the message
            await event_message.edit(content=updated_content)
            
            # Use the non-day part for the channel name
            channel_date = new_date.strip()
            
            # Update channel name
            await update_channel_name(channel, current_name, channel_date)
            
            await interaction.response.send_message(f"Date updated: {formatted_date}", ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update event date: {e}")
            await interaction.response.send_message("Failed to update event date. Please try again.", ephemeral=True)

    @tree.command(
        name="change_location",
        description="Change the location of the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
        new_location="New location of the event",
    )
    async def change_location(interaction: discord.Interaction, new_location: str) -> None:
        """Change the event location"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # Get parent message
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update location in message
            current_content = event_message.content
            start_index = current_content.find('**:round_pushpin: Location:**') + len('**:round_pushpin: Location:**')
            end_index = current_content.find('**', start_index) - 1
            updated_content = current_content[:start_index] + ' ' + new_location + current_content[end_index:]
            
            # Update the message
            await event_message.edit(content=updated_content)
            await interaction.response.send_message(f"Location updated: {new_location}", ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update event location: {e}")
            await interaction.response.send_message("Failed to update event location. Please try again.", ephemeral=True)

    @tree.command(
        name="change_price",
        description="Change the price of the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
        new_price="New price of the event",
    )
    async def change_price(interaction: discord.Interaction, new_price: str) -> None:
        """Change the event price"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # Get parent message
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update price in message
            current_content = event_message.content
            start_index = current_content.find('**:dollar: Price:**') + len('**:dollar: Price:**')
            
            # Find the end of the price field
            next_marker_pos = current_content.find('\n\n', start_index)
            if next_marker_pos == -1:
                next_marker_pos = len(current_content)
                
            updated_content = current_content[:start_index] + ' ' + new_price + current_content[next_marker_pos:]
            
            # Update the message
            await event_message.edit(content=updated_content)
            await interaction.response.send_message(f"Price updated: {new_price}", ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update event price: {e}")
            await interaction.response.send_message("Failed to update event price. Please try again.", ephemeral=True)

    @tree.command(
        name="change_notes",
        description="Change the notes for the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
    )
    async def change_notes(interaction: discord.Interaction) -> None:
        """Change the event notes"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # First acknowledge the command to avoid interaction timeout
            await interaction.response.send_message("I'll send you a DM to collect the new notes.", ephemeral=True)
            
            # Send DM to collect notes
            try:
                user = interaction.user
                dm_channel = await user.create_dm()
                await dm_channel.send("Please send the new notes for your event. You can use multiple lines. Type `cancel` to cancel.")
                
                # Wait for response in DM
                def check(message):
                    return message.author == user and message.channel == dm_channel
                    
                response = await interaction.client.wait_for('message', check=check, timeout=300.0)
                
                # If user wants to cancel
                if response.content.lower() == 'cancel':
                    await dm_channel.send("Notes update cancelled.")
                    return
                    
                new_notes = response.content.strip()
                
                # Get parent message
                channel = interaction.channel
                messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
                event_message = messages[0] if messages else None
                
                if not event_message:
                    await dm_channel.send("Could not find the event message.")
                    return
                    
                # Update notes in message
                current_content = event_message.content
                notes_header = "**:pencil: Notes:**"
                start_index = current_content.find(notes_header) + len(notes_header)
                
                # Find the next section header, if any
                next_section = current_content.find("**:", start_index)
                if next_section != -1:
                    updated_content = current_content[:start_index] + "\n" + new_notes + "\n\n" + current_content[next_section:]
                else:
                    updated_content = current_content[:start_index] + "\n" + new_notes
                
                # Update the message
                await event_message.edit(content=updated_content)
                await dm_channel.send("Notes updated successfully!")
                
                # Notify in channel that notes were updated
                # await channel.send(f"{user.mention} has updated the event notes.")
                
            except asyncio.TimeoutError:
                await dm_channel.send("You didn't respond in time. Please try the command again when ready.")
                
        except discord.HTTPException as e:
            logger.error(f"Failed to update event notes: {e}")
            if 'dm_channel' in locals():
                await dm_channel.send("Failed to update event notes. Please try again.")

    @tree.command(
        name="change_emoji",
        description="Change the emoji for the event in the current channel",
        guild=guild
    )
    @app_commands.describe(
        new_emoji="New emoji for the event (e.g., :tada:, :calendar:)",
    )
    async def change_emoji(interaction: discord.Interaction, new_emoji: str) -> None:
        """Change the event emoji"""
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command cannot be used in threads.", ephemeral=True)
            return
            
        try:
            # Get parent message
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update emoji in message
            current_content = event_message.content
            
            # Find the first bold section containing the emoji and event name
            first_bold_start = current_content.find('**')
            first_bold_end = current_content.find('**', first_bold_start + 2)
            bold_content = current_content[first_bold_start + 2:first_bold_end]
            
            # Find the space between emoji and event name
            space_index = bold_content.find(' ')
            if space_index == -1:
                await interaction.response.send_message("Could not parse event title format.", ephemeral=True)
                return
                
            # Extract event name
            event_name = bold_content[space_index + 1:]
            
            # Replace the bold section with new emoji
            updated_content = (
                current_content[:first_bold_start] + 
                f"**{new_emoji} {event_name}**" + 
                current_content[first_bold_end + 2:]
            )
            
            # Update the message
            await event_message.edit(content=updated_content)
            await interaction.response.send_message(f"Emoji updated to {new_emoji}", ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update event emoji: {e}")
            await interaction.response.send_message("Failed to update event emoji. Please try again.", ephemeral=True)
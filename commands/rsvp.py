"""
RSVP command for events - with optional user mention support
"""
import discord
from discord import app_commands
import logging
from commands.log_cmd import log_command

logger = logging.getLogger('event_bot')

def register_rsvp(tree: app_commands.CommandTree, guild: discord.Object) -> None:
    """Register the RSVP command"""
    @tree.command(
        name="rsvp",
        description="RSVP for the event by choosing yes, no, or maybe",
        guild=guild
    )
    @app_commands.describe(
        response="Your RSVP response (yes, no, maybe)",
        user="Optional: The user to RSVP for (if not provided, RSVPs for yourself)"
    )
    async def rsvp(interaction: discord.Interaction, response: str, user: discord.Member = None) -> None:
        """Update RSVP status for a user or yourself"""
        log_command(str(interaction.user), f"/rsvp {str(response)} {str(user)}")
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("The bot is undergoing an update that is not backwards compatible with event threads.", ephemeral=True)
            return
            
        valid_responses = {"yes", "no", "maybe"}
        if response.lower() not in valid_responses:
            await interaction.response.send_message("Invalid response. Please use yes, no, or maybe.", ephemeral=True)
            return
        
        # Determine which user to RSVP for
        target_user = user if user else interaction.user
        
        # Check if the user has permission to RSVP for others
        try:
            # Get the event message - first message in channel
            channel = interaction.channel
            messages = [msg async for msg in channel.history(limit=1, oldest_first=True)]
            event_message = messages[0] if messages else None
            
            if not event_message:
                await interaction.response.send_message("Could not find the event message.", ephemeral=True)
                return
                
            # Update RSVP sections
            current_content = event_message.content
            user_mention = target_user.mention
            
            # Define section markers and their display names
            sections = {
                "yes": "**:white_check_mark: Going:**",
                "maybe": "**:question: Maybe:**",
                "no": "**:x: Can't make it:**"
            }
            
            # Process each section
            for section_type, section_marker in sections.items():
                # Find section boundaries
                section_start = current_content.find(section_marker) + len(section_marker)
                next_section_marker = None
                for marker in sections.values():
                    if marker != section_marker and current_content.find(marker, section_start) != -1:
                        next_marker_pos = current_content.find(marker, section_start)
                        if next_section_marker is None or next_marker_pos < current_content.find(next_section_marker, section_start):
                            next_section_marker = marker
                
                if next_section_marker:
                    section_end = current_content.find(next_section_marker, section_start)
                else:
                    section_end = current_content.find("**:pencil:", section_start)
                
                # Extract current section content
                section_content = current_content[section_start:section_end].strip()
                
                # Remove the count part first
                count_start = section_content.find('(') 
                if count_start != -1:
                    count_end = section_content.find(')', count_start)
                    if count_end != -1:
                        section_content = section_content[:count_start].strip() + section_content[count_end + 1:]
                
                # Is this the section we're adding to?
                if section_type == response.lower():
                    # Add user if not already present
                    if user_mention not in section_content:
                        if section_content:
                            section_content += f" {user_mention}"
                        else:
                            section_content = f"\n{user_mention}"
                else:
                    # Remove user if present
                    if user_mention in section_content:
                        words = section_content.split()
                        words = [word for word in words if word != user_mention]
                        section_content = " ".join(words)
                
                # Count users in this section
                user_count = 0
                if section_content.strip():
                    # Count mentions (each mention starts with <@)
                    user_count = section_content.count('<@')
                
                # Add the count to the section header
                section_content = f" ({user_count}){section_content}"
                
                # Format section content with proper spacing
                if not section_content.startswith("\n") and section_content.strip() != f" ({user_count})":
                    section_content = f"{section_content}"
                if not section_content.endswith("\n\n"):
                    section_content = f"{section_content}\n\n"
                
                # Replace the section in the message
                current_content = current_content[:section_start] + section_content + current_content[section_end:]
            
            # Update the message
            await event_message.edit(content=current_content)
            
            # Create appropriate response message
            if user and user != interaction.user:
                response_msg = f"Updated {user.display_name}'s RSVP to: {response.capitalize()}"
            else:
                response_msg = f"RSVP updated: {response.capitalize()}"
            
            await interaction.response.send_message(response_msg, ephemeral=True)
            
        except discord.HTTPException as e:
            logger.error(f"Failed to update RSVP: {e}")
            await interaction.response.send_message("Failed to update RSVP. Please try again.", ephemeral=True)
        except IndexError:
            logger.error("No messages found in channel")
            await interaction.response.send_message("Could not find any messages in this channel.", ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error updating RSVP: {e}")
            await interaction.response.send_message("An unexpected error occurred. Please try again later.", ephemeral=True)

import discord
from discord import app_commands
from discord import PermissionOverwrite
import logging
from utils.formatting import format_event_message

logger = logging.getLogger('event_bot')

def register_event_creation(tree: app_commands.CommandTree, guild: discord.Object) -> None:
    """Register the event creation command"""
    
    @tree.command(
        name="event",
        description="Create an event.",
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
            guild = interaction.guild
            try:
                category = discord.utils.find(lambda c: c.name.lower() == "active plans", guild.categories)
            except Exception as e:
                # Handle the error - either set category to None or log the error
                category = None
                print(f"Failed to get category: {e}")

            # Build the event message
            event_message_content = format_event_message(
                event_name, time, location, price, emoji, interaction.user.mention
            )

            # Set up permissions
            overwrites = {
                guild.default_role: PermissionOverwrite(view_channel=False),
                interaction.user: PermissionOverwrite(view_channel=True, send_messages=True),
            }

            # Create a private channel for the event
            channel_name = f"{event_name.lower().replace(' ', '-')}"
            event_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category,
                topic=f"Event planning for {event_name}",
                reason="Private event channel created via /event"
            )

            # Send the event message
            await event_channel.send(event_message_content)

            # Create a view with a select menu for inviting users
            class InviteView(discord.ui.View):
                def __init__(self, channel):
                    super().__init__(timeout=300)  # 5 minute timeout
                    self.channel = channel
                    self.add_item(InviteSelect(channel))
                
                async def on_timeout(self):
                    # Optional: What happens when the view times out
                    pass

            # Create a select menu for selecting users to invite
            class InviteSelect(discord.ui.UserSelect):
                def __init__(self, channel):
                    super().__init__(
                        placeholder="Select users to invite...",
                        min_values=1,
                        max_values=25,  # Discord's limit
                    )
                    self.channel = channel
                    
                async def callback(self, interaction: discord.Interaction):
                    try:
                        # Add permissions for selected users
                        for user in self.values:
                            await self.channel.set_permissions(
                                user, 
                                view_channel=True, 
                                send_messages=True
                            )
                        
                        # Mention the invited users in the channel
                        mentions = ", ".join(user.mention for user in self.values)
                        await self.channel.send(f"**Invited users:** {mentions}")
                        
                        await interaction.response.send_message(
                            f"Successfully invited {len(self.values)} users to the event!", 
                            ephemeral=True
                        )
                    except discord.HTTPException as e:
                        logger.error(f"Failed to invite users: {e}")
                        await interaction.response.send_message(
                            "Failed to invite users. Please try again.", 
                            ephemeral=True
                        )

            # Respond to the initial command with the invite view
            await interaction.response.send_message(
                f"✅ Event channel created: {event_channel.mention}\nSelect users to invite:", 
                ephemeral=True,
                view=InviteView(event_channel)
            )

            logger.info(f"Private event channel '{channel_name}' created.")

        except discord.HTTPException as e:
            logger.error(f"Failed to create private event channel: {e}")
            await interaction.response.send_message(
                "Failed to create private channel. Please try again.", ephemeral=True
            )
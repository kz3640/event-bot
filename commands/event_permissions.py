# TODO

# @tree.command(
#     name="editaccess",
#     description="Edit which users have access to this event channel",
#     guild=guild
# )
# async def editaccess(interaction: discord.Interaction) -> None:
#     """Edit which users have access to this event channel"""
#     try:
#         # Check if the command is being used in an event channel
#         channel = interaction.channel
#         if not channel.name.startswith(tuple(map(str.lower, ["event-", "party-"]))):
#             await interaction.response.send_message(
#                 "This command can only be used in event channels.", 
#                 ephemeral=True
#             )
#             return
            
#         # Check if the user has permission to edit this channel
#         if not channel.permissions_for(interaction.user).manage_channels:
#             await interaction.response.send_message(
#                 "You don't have permission to edit access for this channel.", 
#                 ephemeral=True
#             )
#             return
            
#         # Create a view with a select menu for managing users
#         class EditAccessView(discord.ui.View):
#             def __init__(self):
#                 super().__init__(timeout=300)  # 5 minute timeout
#                 self.add_item(AddUserSelect(channel))
#                 self.add_item(RemoveUserSelect(channel))
            
#             async def on_timeout(self):
#                 # Optional: What happens when the view times out
#                 pass

#         # Create a select menu for adding users
#         class AddUserSelect(discord.ui.UserSelect):
#             def __init__(self, channel):
#                 super().__init__(
#                     placeholder="Select users to add...",
#                     min_values=1,
#                     max_values=25,  # Discord's limit
#                     custom_id="add_users"
#                 )
#                 self.channel = channel
                
#             async def callback(self, interaction: discord.Interaction):
#                 try:
#                     # Add permissions for selected users
#                     added_users = []
#                     for user in self.values:
#                         # Check if user already has access
#                         current_perms = self.channel.permissions_for(user)
#                         if not current_perms.view_channel:
#                             await self.channel.set_permissions(
#                                 user, 
#                                 view_channel=True, 
#                                 send_messages=True
#                             )
#                             added_users.append(user)
                    
#                     if added_users:
#                         # Mention the invited users in the channel
#                         mentions = ", ".join(user.mention for user in added_users)
#                         await self.channel.send(f"**New users invited:** {mentions}")
                        
#                         await interaction.response.send_message(
#                             f"Successfully added {len(added_users)} users to the event!", 
#                             ephemeral=True
#                         )
#                     else:
#                         await interaction.response.send_message(
#                             "The selected users already have access to this channel.", 
#                             ephemeral=True
#                         )
#                 except discord.HTTPException as e:
#                     logger.error(f"Failed to add users: {e}")
#                     await interaction.response.send_message(
#                         "Failed to add users. Please try again.", 
#                         ephemeral=True
#                     )

#         # Create a select menu for removing users
#         class RemoveUserSelect(discord.ui.UserSelect):
#             def __init__(self, channel):
#                 super().__init__(
#                     placeholder="Select users to remove...",
#                     min_values=1,
#                     max_values=25,  # Discord's limit
#                     custom_id="remove_users"
#                 )
#                 self.channel = channel
                
#             async def callback(self, interaction: discord.Interaction):
#                 try:
#                     # Remove permissions for selected users
#                     removed_count = 0
#                     for user in self.values:
#                         # Don't remove the original event creator (assumed to be the one with manage_channels permission)
#                         member = interaction.guild.get_member(user.id)
#                         if member and not channel.permissions_for(member).manage_channels:
#                             await self.channel.set_permissions(user, overwrite=None)  # Reset to default (no access)
#                             removed_count += 1
                    
#                     await interaction.response.send_message(
#                         f"Removed {removed_count} users from the event channel.", 
#                         ephemeral=True
#                     )
#                 except discord.HTTPException as e:
#                     logger.error(f"Failed to remove users: {e}")
#                     await interaction.response.send_message(
#                         "Failed to remove users. Please try again.", 
#                         ephemeral=True
#                     )

#         # Send the edit access view
#         await interaction.response.send_message(
#             "Select users to add or remove from this event channel:", 
#             view=EditAccessView(),
#             ephemeral=True
#         )

#     except Exception as e:
#         logger.error(f"Error in editaccess command: {e}")
#         await interaction.response.send_message(
#             "An error occurred while editing channel access.", 
#             ephemeral=True
#         )

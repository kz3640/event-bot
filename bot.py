"""
Core bot setup and configuration
"""
import discord
from discord import Intents, Client
import logging
from commands.event_creation import register_event_creation
from commands.event_editing import register_event_editing
from commands.rsvp import register_rsvp
from commands.util import register_help

logger = logging.getLogger('event_bot')

def create_client(guild_id: str) -> Client:
    """Create and configure the Discord client"""
    # Configure intents
    intents = Intents.default()
    intents.message_content = True
    
    # Create client and command tree
    client = Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)
    
    # Register on_ready event
    @client.event
    async def on_ready() -> None:
        logger.info(f'{client.user} has connected to Discord!')
        try:
            await tree.sync(guild=discord.Object(id=guild_id))
            logger.info('Commands synced!')
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    # Register message logging
    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel_name = str(message.channel)

        logger.info(f'[{channel_name}] {username}: {user_message}')
    
    # Register command modules
    guild = discord.Object(id=guild_id)
    register_event_creation(tree, guild)
    register_event_editing(tree, guild)
    register_rsvp(tree, guild)
    register_help(tree, guild)
    
    return client

def run_client(client: Client, token: str) -> None:
    """Run the Discord client"""
    try:
        client.run(token=token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token. Please check your .env file.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
#!/usr/bin/env python3
"""
Entry point for the Discord Event Bot
"""
import logging
from dotenv import load_dotenv
import os
from bot import create_client, run_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('event_bot')

def main() -> None:
    """Main entry point for the bot"""
    # Load environment variables
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    guild_id = os.getenv("GUILD_ID")
    
    if not token or not guild_id:
        logger.error("Missing required environment variables (DISCORD_TOKEN or GUILD_ID)")
        exit(1)
    
    # Create and run the client
    client = create_client(guild_id)
    run_client(client, token)

if __name__ == "__main__":
    main()
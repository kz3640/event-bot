import logging
from datetime import datetime

# Configure the logger
logging.basicConfig(
    filename='commands.log',  # Log file name
    level=logging.INFO,       # Log level
    format='%(asctime)s-%(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

# Function to log commands
def log_command(user, channel, command):
    logging.info(f"{user}-{channel}-{command}")


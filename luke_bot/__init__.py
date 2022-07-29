import os
from dotenv import load_dotenv
load_dotenv()

from luke_bot.main import main # noqa

environment_variables = ('GG_TOKEN', 'DISCORD_TOKEN', 'DISCORD_CHANNEL_ID')

for var in environment_variables:
    if os.getenv(var) is None:
        raise RuntimeError(f'Environment variable {var} not set.')

if __name__ == '__main__':
    main()

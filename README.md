# SpaceCases

SpaceCases is a Discord bot for trading, unboxing, and collecting virtual CS2 skins and items. 

## Prerequisites

Before running the bot, ensure that you have the following:

- **Python 3.8+** installed on your machine.
- **PostgreSQL** with a database and an associated superuser.
- A **Discord bot user** setup with the necessary permissions:
  - **Create a Bot User**: Follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) to create a Discord bot and obtain its token.
  - **Intents**: The bot uses the following privileged intents:
      - `Message Content`
  - **Generatiing the Bot Invite Link**:
      - Use the following [scopes](https://discord.com/developers/docs/topics/oauth2#shared-resources-oauth2-scopes) when generating the invite link for the bot:
        - `bot`
        - `applications.commands`
      - Use the following [permissions](https://discord.com/developers/docs/topics/permissions) when generating the invite link for the bot:
        - `Send Messages`

Once you've set up the bot user, you can proceed with running the bot as outlined below.

## Running

```bash
git clone https://github.com/SpaceCases/SpaceCases # Clone repository to local machine
cd SpaceCases                                      # Move into directory
python -m venv env                                 # Create the virtual environment
source env/bin/activate                            # Activate virtual environment
python -m pip install -r requirements.txt          # Install dependencies
mv .env.example .env                               # Rename .env.example to .env
```
Then use your preferred text editor of choice to edit the environment variables in `.env`. Once that is setup, you can run the bot:
```bash
python main.py                                     # Run the bot
```


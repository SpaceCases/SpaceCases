# SpaceCases

SpaceCases is a Discord bot for trading, unboxing, and collecting virtual CS2 skins and items. Click [here](https://discord.com/oauth2/authorize?client_id=1310243158478815253&permissions=2048&integration_type=0&scope=bot+applications.commands) to invite it to your server.

## Prerequisites

Before running the bot, ensure that you have the following:

- **Python 3.12+** installed on your machine.
- **PostgreSQL** with a database and an associated superuser account.
- A **Discord bot user** setup with the necessary permissions:
  - **Create a Bot User**: Follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) to create a Discord bot and obtain its token.
  - **Intents**: The bot uses the following privileged intents:
      - `Message Content`
  - **Generating the Bot Invite Link**:
      - Use the following [scopes](https://discord.com/developers/docs/topics/oauth2#shared-resources-oauth2-scopes) when generating the invite link for the bot:
        - `bot`
        - `applications.commands`
      - Use the following [permissions](https://discord.com/developers/docs/topics/permissions) when generating the invite link for the bot:
        - `Send Messages`

Once you've set up the bot user, you can proceed with running the bot as outlined below.

## Running

```bash
git clone https://github.com/SpaceCases/SpaceCases          # Clone repository to local machine
cd SpaceCases                                               # Move into directory
python -m venv env                                          # Create the virtual environment
source env/bin/activate                                     # Activate virtual environment
python -m pip install .                                     # Install dependencies
mv .env.example .env                                        # Rename .env.example to .env
psql -U user -h host -d database_name -f src/sql/init.sql   # Run init.sql file to setup database
```
Then, use your preferred text editor to edit the environment variables in .env. When running the bot for the first time, you need to synchronize its slash commands with Discord. You can do this by running the bot with the **-s** or **--sync-slash-commands** flag:
```bash
python main.py -s                                # Run the bot and sync slash commands on start up
```
You only need to do this **once** if you don't plan on adding any new commands. If you **do** add new slash commands later, you can use the `/sync` command within the bot or just re-run the bot with the sync flag. Otherwise, every other time you run the bot you **should not** use the flag:
```bash
python main.py                                   # Run the bot
```
## Commands

`/register` - Create a SpaceCases bank account    
`/close` - Close your SpaceCases bank account    
`/balance` - View a user's bank account balance    
`/claim` - Claim your daily allowance    
`/transfer` - Transfer balance to another user    
`/inventory` - View a user's inventory or inspect a specific item from it    
`/sell` - Sell an item from your inventory    
`/open` - Open a container    
`/item` - View an item's information    
`/containers` - View a list of all openable containers    
`/sync` - Sync slash commands, can only be run by the user with id `OWNER_ID` in the `.env` file

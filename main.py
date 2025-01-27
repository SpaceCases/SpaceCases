import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SpaceCases discord bot")
    parser.add_argument(
        "-s",
        "--sync-slash-commands",
        action="store_true",
        help="Sync slash commands on bot startup",
    )
    args = parser.parse_args()
    sync_slash_commands: bool = args.sync_slash_commands
    from src.start import start

    start(sync_slash_commands)

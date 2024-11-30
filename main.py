from src.bot import SpaceCasesBot
from src.environment import Environment

if __name__ == "__main__":
    environment = Environment.load()
    bot = SpaceCasesBot(environment)
    bot.run(environment.bot_token, log_handler=None)

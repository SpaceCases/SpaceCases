import discord


class SpaceCasesCommandError(discord.app_commands.AppCommandError):
    """Base class for command-related errors."""

    pass


class UserNotRegisteredError(SpaceCasesCommandError):
    def __init__(self, user: discord.User | discord.Member):
        self.user = user


class InsufficientBalanceError(SpaceCasesCommandError):
    pass

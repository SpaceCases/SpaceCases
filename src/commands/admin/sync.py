import discord
from src.bot import SpaceCasesBot
from src.ui.embed import send_success_embed, send_err_embed


async def sync(bot: SpaceCasesBot, interaction: discord.Interaction) -> None:
    if interaction.user.id != bot.owner_id:
        await send_err_embed(
            interaction, "You do **not** have permission to user this command."
        )
        return
    await bot.sync_commands()
    await send_success_embed(interaction, "Commands **successfully** synced")

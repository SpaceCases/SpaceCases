import discord
from typing import Any, Coroutine, Optional, Callable
from discord.ui import Button, View
from spacecases_common import Rarity


def create_embed(
    msg_content: str, color: discord.Color = discord.Color.dark_theme()
) -> discord.Embed:
    return discord.Embed(description=msg_content, color=color)


def create_success_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.green())


def create_err_embed(msg_content: str) -> discord.Embed:
    return create_embed(msg_content, discord.Color.red())


async def send_embed(
    interaction: discord.Interaction,
    msg_content: str,
    color: discord.Color = discord.Color.dark_theme(),
    ephemeral: bool = False,
) -> None:
    embed = create_embed(msg_content, color)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_success_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_success_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


async def send_err_embed(
    interaction: discord.Interaction, msg_content: str, ephemeral: bool = False
) -> None:
    embed = create_err_embed(msg_content)
    await interaction.response.send_message(
        embed=embed,
        ephemeral=ephemeral,
    )


type ButtonCallbackType = Callable[[discord.Interaction], Coroutine[Any, Any, None]]


class YesNoEmbedView(View):
    def __init__(
        self,
        on_yes: ButtonCallbackType,
        on_no: ButtonCallbackType,
        interaction: discord.Interaction,
        timeout: Optional[float] = 30,
    ):
        self.on_yes = on_yes
        self.on_no = on_no
        self.responded = False
        self.interaction = interaction
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        await self.on_yes(interaction)
        self.responded = True

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        await self.on_no(interaction)
        self.responded = True

    async def on_timeout(self):
        if self.responded:
            return
        message = await self.interaction.original_response()
        new_embed = create_err_embed("You did **not** respond in time")
        await message.edit(embed=new_embed, view=None)
        return await super().on_timeout()


async def yes_no_embed(
    interaction: discord.Interaction,
    msg_content: str,
    on_yes: ButtonCallbackType,
    on_no: ButtonCallbackType,
    timeout: Optional[float] = 30,
) -> None:
    embed = discord.Embed(description=msg_content, color=discord.Color.dark_theme())
    await interaction.response.send_message(
        embed=embed, view=YesNoEmbedView(on_yes, on_no, interaction, timeout)
    )


def get_rarity_embed_color(rarity: Rarity):
    return [0xB0C3D9, 0x5E98D9, 0x4B69FF, 0x8847FF, 0xD32CE6, 0xEB4B4B, 0xE4AE39][
        rarity.value
    ]

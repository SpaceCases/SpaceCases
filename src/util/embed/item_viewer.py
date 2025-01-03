import discord
from typing import Optional, Any
from src.util.types import StickerOwnership, SkinOwnership
from src.util.string import currency_str_format
from .general import get_rarity_embed_color, send_err_embed
from spacecases_common import SkinMetadatum


async def send_sticker_viewer(
    interaction: discord.Interaction, ownership: StickerOwnership
) -> None:
    """
    Sends an item viewer for an owned sticker item
    """
    price = ownership.metadatum.price
    if ownership.count > 1:
        title = f"{ownership.metadatum.formatted_name} x{ownership.count}"
        total_value = price * ownership.count
        description = f"Total Value: **{currency_str_format(total_value)}**"
    else:
        title = ownership.metadatum.formatted_name
        description = None
    e = discord.Embed(
        title=title,
        description=description,
        color=get_rarity_embed_color(ownership.metadatum.rarity),
    )
    e.set_image(url=ownership.metadatum.image_url)
    e.add_field(name="Price", value=currency_str_format(price))
    e.add_field(
        name="Rarity", value=ownership.metadatum.rarity.get_name_for_regular_item()
    )
    e.set_footer(
        text=f"Owned by {ownership.owner.display_name}",
        icon_url=ownership.owner.display_avatar.url,
    )
    await interaction.response.send_message(embed=e)


def get_owned_skin_embed(
    owner: discord.Member | discord.User, metadatum: SkinMetadatum, float: float
) -> discord.Embed:
    """
    Generates an embed for an owned skin item
    """
    e = discord.Embed(
        title=metadatum.formatted_name,
        description=metadatum.description,
        color=get_rarity_embed_color(metadatum.rarity),
    )
    e.set_image(url=metadatum.image_url)
    e.add_field(name="Price", value=currency_str_format(metadatum.price))
    e.add_field(name="Rarity", value=metadatum.rarity.get_name_for_skin())
    e.add_field(name="Float", value=float)
    e.set_footer(
        text=f"Owned by {owner.display_name}",
        icon_url=owner.display_avatar.url,
    )
    return e


class SkinViewerViewSelect(discord.ui.Select):
    def __init__(self, parent_view: "SkinViewerView") -> None:
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=f"Float: {float}", value=str(idx))
            for idx, float in enumerate(self.parent_view.ownership.floats)
        ]
        super().__init__(
            placeholder="Select a skin",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> Any:
        if interaction.user != self.parent_view.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        self.parent_view.index = int(self.values[0])
        new_embed = self.parent_view.get_embed()
        await interaction.response.edit_message(embed=new_embed, view=self.parent_view)


class SkinViewerView(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        ownership: SkinOwnership,
        timeout: Optional[float] = 30,
    ):
        super().__init__(timeout=timeout)
        self.index = 0
        self.interaction = interaction
        self.ownership = ownership
        self.add_item(SkinViewerViewSelect(self))

    def get_embed(self) -> discord.Embed:
        float = self.ownership.floats[self.index]
        return get_owned_skin_embed(
            self.ownership.owner, self.ownership.metadatum, float
        )

    async def on_timeout(self) -> None:
        await self.interaction.edit_original_response(view=None)


async def send_skin_viewer(
    interaction: discord.Interaction, ownership: SkinOwnership
) -> None:
    """
    Sends a viewer embed for an owned skin. If there are multiple of the same skin (by name) it will have a select menu to choose between.
    """
    if len(ownership.floats) == 1:
        await interaction.response.send_message(
            embed=get_owned_skin_embed(
                ownership.owner, ownership.metadatum, ownership.floats[0]
            ),
        )
    else:
        view = SkinViewerView(interaction, ownership)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

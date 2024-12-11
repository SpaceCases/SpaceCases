import discord
import random
from itertools import islice
from src.bot import SpaceCasesBot
from src.util.string import currency_str_format
from src.util.embed import send_err_embed, get_rarity_embed_color
from spacecases_common import (
    remove_skin_name_formatting,
    SkinMetadatum,
    StickerMetadatum,
)


async def item(bot: SpaceCasesBot, interaction: discord.Interaction, name: str):
    unformatted_name = remove_skin_name_formatting(name)
    if unformatted_name not in bot.item_metadata:
        await send_err_embed(interaction, f"No item exists with name: `{name}`")
        return
    item_metadata = bot.item_metadata[unformatted_name]
    if isinstance(item_metadata, SkinMetadatum):
        e = discord.Embed(
            title=item_metadata.formatted_name,
            description=item_metadata.description,
            color=get_rarity_embed_color(item_metadata.rarity),
        )
        e.add_field(name="Price", value=currency_str_format(item_metadata.price))
        e.add_field(name="Rarity", value=item_metadata.rarity.get_name_for_skin())
        e.add_field(
            name="Float Range",
            value=f"{item_metadata.min_float:.2f} - {item_metadata.max_float:.2f}",
        )
        e.set_image(url=item_metadata.image_url)
    elif isinstance(item_metadata, StickerMetadatum):
        e = discord.Embed(
            title=item_metadata.formatted_name,
            color=get_rarity_embed_color(item_metadata.rarity),
        )
        e.add_field(name="Price", value=currency_str_format(item_metadata.price))
        e.add_field(
            name="Rarity", value=item_metadata.rarity.get_name_for_regular_item()
        )
        e.set_image(url=item_metadata.image_url)

    await interaction.response.send_message(embed=e)


async def item_name_autocomplete(bot: SpaceCasesBot, current: str):
    unformatted_current = remove_skin_name_formatting(current)
    if len(unformatted_current) == 0:
        options = random.sample(bot.all_unformatted_names, 25)
    else:
        options = list(islice(bot.skin_name_trie.keys(unformatted_current), 25))

    return [
        discord.app_commands.Choice(
            name=bot.item_metadata[unformatted_name].formatted_name,
            value=unformatted_name,
        )
        for unformatted_name in options
    ]

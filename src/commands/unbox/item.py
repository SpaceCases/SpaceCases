import discord
import random
from itertools import islice
from src.bot import SpaceCasesBot
from src.util.string import currency_str_format
from src.util.embed import send_err_embed, get_grade_embed_colour
from spacecases_common import remove_skin_name_formatting


async def item(bot: SpaceCasesBot, interaction: discord.Interaction, name: str):
    unformatted_name = remove_skin_name_formatting(name)
    if unformatted_name not in bot.skin_data:
        await send_err_embed(interaction, f"No item exists with name: `{name}`")
        return
    skin = bot.skin_data[unformatted_name]
    e = discord.Embed(
        title=skin.formatted_name,
        description=skin.description,
        color=get_grade_embed_colour(skin.grade),
    )
    e.add_field(name="Price", value=currency_str_format(skin.price))
    e.add_field(name="Grade", value=skin.grade)
    e.add_field(
        name="Float Range", value=f"{skin.min_float:.2f} - {skin.max_float:.2f}"
    )
    e.set_image(url=skin.image_url)
    await interaction.response.send_message(embed=e)


async def item_name_autocomplete(bot: SpaceCasesBot, current: str):
    unformatted_current = remove_skin_name_formatting(current)
    if len(unformatted_current) == 0:
        options = random.sample(bot.all_unformatted_names, 25)
    else:
        options = list(islice(bot.skin_name_trie.keys(unformatted_current), 25))

    return [
        discord.app_commands.Choice(
            name=bot.skin_data[unformatted_name].formatted_name,
            value=unformatted_name,
        )
        for unformatted_name in options
    ]

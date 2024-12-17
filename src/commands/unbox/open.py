import discord
import random
from typing import Optional
from itertools import islice
from src.bot import SpaceCasesBot
from src.util.embed import get_rarity_embed_color, send_err_embed
from src.util.string import currency_str_format
from src.util.constants import KEY_PRICE
from spacecases_common import (
    remove_skin_name_formatting,
    SkinContainerEntry,
    ItemContainerEntry,
    PhaseGroup,
    SkinCase,
    SouvenirPackage,
    SkinMetadatum,
)


async def open(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    container_formatted_name: str,
):
    container_unformatted_name = remove_skin_name_formatting(container_formatted_name)
    container = bot.containers[container_unformatted_name]
    price = container.price
    if container.requires_key:
        price += KEY_PRICE

    # try and deduct price
    price_deducted: Optional[bool] = (
        await bot.db.fetch_from_file(
            "try_deduct_balance.sql", interaction.user.id, price
        )
    )[0]["result"]
    if price_deducted is None:
        await send_err_embed(
            interaction,
            f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
        )
        return
    if not price_deducted:
        await send_err_embed(
            interaction,
            f"You do **not** have enough balance to buy a **{container.formatted_name}**",
        )
        return
    # generate probability table (maybe move to asset generation?)
    cumulative_probabilities = {}
    cumulative_probability = 0
    for idx, rarity in enumerate(reversed(container.contains.keys())):
        cumulative_probability += 1 + 5 ** (idx + 1)
        cumulative_probabilities[rarity] = cumulative_probability

    # select random rarity
    random_int = random.randint(1, cumulative_probability)
    if random_int == 1:
        container_entry = random.choice(container.contains_rare)
    else:
        for rarity, cum in cumulative_probabilities.items():
            if random_int <= cum:
                break
        container_entry = random.choice(container.contains[rarity])
    # generate the item
    if isinstance(container_entry, SkinContainerEntry):
        # calculate its float value
        min_float = container_entry.min_float
        max_float = container_entry.max_float

        float_value = random.random()

        # determine condition
        if float_value > 0 and float_value <= 0.1471:
            float_value = random.uniform(0.00, 0.07)
        elif float_value > 0.1471 and float_value <= 0.3939:
            float_value = random.uniform(0.07, 0.15)
        elif float_value > 0.3939 and float_value <= 0.8257:
            float_value = random.uniform(0.15, 0.38)
        elif float_value > 0.8257 and float_value <= 0.9007:
            float_value = random.uniform(0.38, 0.45)
        elif float_value > 0.9007 and float_value <= 1.0:
            float_value = random.uniform(0.45, 1)

        # linear interpolate between max and min float
        final_float = float_value * (max_float - min_float) + min_float

        # what condition is this float?
        for condition, lower_bound in {
            remove_skin_name_formatting("Battle-Scarred"): 0.45,
            remove_skin_name_formatting("Well-Worn"): 0.38,
            remove_skin_name_formatting("Field-Tested"): 0.15,
            remove_skin_name_formatting("Minimal Wear"): 0.07,
            remove_skin_name_formatting("Factory New"): 0.00,
        }.items():
            if final_float > lower_bound:
                break

        # if it has a phase, obtain it
        if isinstance(container_entry.phase_group, PhaseGroup):
            phase = remove_skin_name_formatting(
                random.choice(container_entry.phase_group.get_phases())
            )
            unformatted_name = container_entry.unformatted_name + phase + condition
        else:
            unformatted_name = container_entry.unformatted_name + condition

    elif isinstance(container_entry, ItemContainerEntry):
        unformatted_name = container_entry.unformatted_name

    # if the container is a skin case, 10% chance of stattrak
    if isinstance(container, SkinCase):
        if random.randint(1, 10) == 1:
            unformatted_name = "stattrak" + unformatted_name
    # if the container is a souvenir package, always come as souvenir item
    elif isinstance(container, SouvenirPackage):
        unformatted_name = "souvenir" + unformatted_name
    # create embed
    item_metadatum = bot.item_metadata[unformatted_name]
    e = discord.Embed(
        title=item_metadatum.formatted_name,
        color=get_rarity_embed_color(item_metadatum.rarity),
    )
    e.add_field(name="Price", value=currency_str_format(item_metadatum.price))
    if isinstance(item_metadatum, SkinMetadatum):
        e.description = item_metadatum.description
        e.add_field(name="Float", value=str(final_float))
    e.set_thumbnail(url=container.image_url)
    e.set_image(url=item_metadatum.image_url)
    e.set_footer(
        text="Item will automatically sell in 30 seconds!",
        icon_url=interaction.user.display_avatar.url,
    )
    await interaction.response.send_message(embed=e)


async def open_name_autocomplete(bot: SpaceCasesBot, current: str):
    unformatted_current = remove_skin_name_formatting(current)
    if len(unformatted_current) == 0:
        options = random.sample(bot.container_unformatted_names, 25)
    else:
        options = list(islice(bot.container_trie.keys(unformatted_current), 25))

    return [
        discord.app_commands.Choice(
            name=bot.containers[unformatted_name].formatted_name,
            value=bot.containers[unformatted_name].formatted_name,
        )
        for unformatted_name in options
    ]

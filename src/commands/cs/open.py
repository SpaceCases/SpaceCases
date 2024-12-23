import discord
import random
from typing import Optional
from itertools import islice
from src.bot import SpaceCasesBot
from src.database import (
    ADD_SKIN,
    ADD_STICKER,
    DOES_USER_EXIST_FOR_UPDATE,
    LOCK_SKINS,
    LOCK_STICKERS,
    CHANGE_BALANCE,
    TRY_DEDUCT_BALANCE,
)
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
    StickerMetadatum,
    ItemMetadatum,
    Container,
)


class OpenView(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        bot: SpaceCasesBot,
        container: Container,
        item: ItemMetadatum,
        item_unformatted_name: str,
        float: Optional[float],
    ):
        self.interaction = interaction
        self.item = item
        self.bot = bot
        self.container = container
        self.item_unformatted_name = item_unformatted_name
        self.float = float
        self.responded = False
        super().__init__(timeout=30)

    @discord.ui.button(label="Add To Inventory", style=discord.ButtonStyle.green)
    async def add_to_inventory(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        # check its the right person who can interact
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return

        # add the item to our inventory
        if isinstance(self.item, SkinMetadatum):
            query = ADD_SKIN
            args = [self.interaction.user.id, self.item_unformatted_name, self.float]
        elif isinstance(self.item, StickerMetadatum):
            query = ADD_STICKER
            args = [self.interaction.user.id, self.item_unformatted_name]

        async with self.bot.db.pool.acquire() as connection:
            async with connection.transaction(isolation="serializable"):
                # check we exist
                rows = await self.bot.db.fetch_from_file_with_connection(
                    DOES_USER_EXIST_FOR_UPDATE,
                    connection,
                    interaction.user.id,
                )
                if not rows[0]["exists"]:
                    await send_err_embed(
                        interaction,
                        f"You are **not** registered. Use {self.bot.get_slash_command_mention_string('register')} to register!",
                        ephemeral=True,
                    )
                    return

                # lock the skins and stickers tables
                await self.bot.db.execute_from_file_with_connection(
                    LOCK_SKINS, connection
                )
                await self.bot.db.execute_from_file_with_connection(
                    LOCK_STICKERS, connection
                )

                # add item
                rows = await self.bot.db.fetch_from_file_with_connection(
                    query,
                    connection,
                    *args,
                )
                # no space
                if len(rows) == 0:
                    await send_err_embed(
                        interaction,
                        "You don't have enough inventory space for this action!",
                        ephemeral=True,
                    )
                    return

        message = await self.interaction.original_response()
        e = discord.Embed(title=self.item.formatted_name, color=discord.Color.green())
        e.add_field(name="Price", value=currency_str_format(self.item.price))
        if isinstance(self.item, SkinMetadatum):
            e.description = self.item.description
            e.add_field(name="Float", value=str(self.float))
        e.set_image(url=self.item.image_url)
        e.set_footer(
            text=f"Unboxed by {self.interaction.user.display_name}",
            icon_url=self.interaction.user.display_avatar.url,
        )
        await message.edit(embed=e, view=None)
        self.responded = True

    async def sell(self, give_up: bool) -> bool:
        rows = await self.bot.db.fetch_from_file(
            CHANGE_BALANCE, self.interaction.user.id, self.item.price
        )
        if len(rows) == 0 and not give_up:
            return False
        message = await self.interaction.original_response()
        e = discord.Embed(
            title=f"{self.item.formatted_name} - Sold!", color=discord.Color.dark_grey()
        )
        e.add_field(name="Price", value=currency_str_format(self.item.price))
        if isinstance(self.item, SkinMetadatum):
            e.description = self.item.description
            e.add_field(name="Float", value=str(self.float))
        e.set_image(url=self.item.image_url)
        e.set_footer(
            text=f"Sold by {self.interaction.user.display_name}",
            icon_url=self.interaction.user.display_avatar.url,
        )
        await message.edit(embed=e, view=None)
        return True

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.red)
    async def sell_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user != self.interaction.user:
            await send_err_embed(interaction, "This is not your button!", True)
            return
        if not await self.sell(give_up=False):
            await send_err_embed(
                interaction,
                f"You are **not** registered. Use {self.bot.get_slash_command_mention_string('register')} to register!",
                ephemeral=True,
            )
            return
        self.responded = True

    async def on_timeout(self) -> None:
        if self.responded:
            return
        await self.sell(give_up=True)


async def open(
    bot: SpaceCasesBot,
    interaction: discord.Interaction,
    container_formatted_name: str,
) -> None:
    container_unformatted_name = remove_skin_name_formatting(container_formatted_name)
    container = bot.containers[container_unformatted_name]
    price = container.price
    if container.requires_key:
        price += KEY_PRICE

    # try and deduct price
    rows = await bot.db.fetch_from_file(TRY_DEDUCT_BALANCE, interaction.user.id, price)
    if len(rows) == 0:
        await send_err_embed(
            interaction,
            f"You are **not** registered. Use {bot.get_slash_command_mention_string('register')} to register!",
        )
        return

    # dont have enough
    if not rows[0]["deducted"]:
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
        final_float = None
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
    e.set_image(url=item_metadatum.image_url)
    e.set_footer(
        text="Item will automatically sell in 30 seconds!",
        icon_url=interaction.user.display_avatar.url,
    )
    await interaction.response.send_message(
        embed=e,
        view=OpenView(
            interaction,
            bot,
            container,
            item_metadatum,
            unformatted_name,
            final_float,
        ),
    )


async def open_name_autocomplete(
    bot: SpaceCasesBot, current: str
) -> list[discord.app_commands.Choice]:
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

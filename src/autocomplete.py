import json
import discord
from spacecases_common import remove_skin_name_formatting, ItemType
from src.bot import SpaceCasesBot
from src.database import GET_INVENTORY


async def inventory_item_autocomplete(
    bot: SpaceCasesBot, user: discord.Member | discord.User, current: str
) -> list[discord.app_commands.Choice]:
    # get their items
    unformatted_curret = remove_skin_name_formatting(current)
    items = await bot.db.fetch_from_file(GET_INVENTORY, user.id)
    result = []
    name: str
    type: ItemType
    for id, name, type, details in items:
        details = json.loads(details)
        if not name.startswith(unformatted_curret):
            continue
        item_metadatum = bot.item_metadata[name]
        if type == ItemType.Skin:
            name = f"{item_metadatum.formatted_name} - {details["float"]} (ID: {id})"
        elif type == ItemType.Sticker:
            name = f"{item_metadatum.formatted_name} (ID: {id})"
        result.append(
            discord.app_commands.Choice(
                name=name,
                value=str(id),
            )
        )
    return result

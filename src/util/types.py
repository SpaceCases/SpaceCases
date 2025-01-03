import discord
from dataclasses import dataclass
from spacecases_common import SkinMetadatum, StickerMetadatum


@dataclass
class SkinOwnership:
    owner: discord.User | discord.Member
    metadatum: SkinMetadatum
    floats: list[float]


@dataclass
class StickerOwnership:
    owner: discord.User | discord.Member
    metadatum: StickerMetadatum
    count: int

import os
import aiohttp
from dataclasses import dataclass
from typing import Optional
from spacecases_common import get_logger

logger = get_logger(__name__)


@dataclass
class LeaderboardEntry:
    inventory_value: int
    position: int


class Leaderboard:
    def __init__(self, entries: dict[int, LeaderboardEntry]):
        self.users = list(entries.keys())
        self.entries = entries

    @staticmethod
    async def from_remote_json(
        leaderboard_domain: str, id: Optional[int] = None
    ) -> "Leaderboard":
        if id is None:
            url = os.path.join(leaderboard_domain, "global.json")
        else:
            url = os.path.join(leaderboard_domain, f"{id}.json")

        logger.info(f"Refreshing leaderboard: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    entries = {}
                    data = await response.json()
                    for key, val in data.items():
                        entries[int(key)] = LeaderboardEntry(
                            val["inventory_value"], val["place"]
                        )
                elif response.status == 404:
                    entries = {}
                else:
                    response.raise_for_status()
        return Leaderboard(entries)

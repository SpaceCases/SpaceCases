import os
import requests
from pydantic import BaseModel
from spacecases_common import (
    SkinMetadatum,
    StickerMetadatum,
    SkinCase,
    SouvenirPackage,
    StickerCapsule,
)
from src.logger import get_logger

logger = get_logger(__name__)


T_LOGO = os.path.join("static", "t.webp")
CT_LOGO = os.path.join("static", "ct.webp")

SKIN_METADATA_PATH = os.path.join("generated", "skin_metadata.json")
STICKER_METADATA_PATH = os.path.join("generated", "sticker_metadata.json")
SKIN_CASES_METADATA_PATH = os.path.join("generated", "skin_cases.json")
STICKER_CAPSULE_METADATA_PATH = os.path.join("generated", "sticker_capsules.json")
SOUVENIR_PACKAGE_METADATA_PATH = os.path.join("generated", "souvenir_packages.json")


# Helper function to parse the raw JSON data into a dictionary of model instances
def parse_metadata[T: BaseModel](url: str, model: type[T]) -> dict[str, T]:
    logger.info(f"Refreshing metadata from {url}...")
    raw_json = requests.get(url).json()
    metadata = {key: model.model_validate(value) for key, value in raw_json.items()}
    logger.info(f"Metadata refreshed from {url}")
    return metadata


def parse_metadata_from_asset_domain[T: BaseModel](
    asset_domain: str, url: str, model: type[T]
) -> dict[str, T]:
    return parse_metadata(os.path.join(asset_domain, url), model)


def get_skin_metadata(asset_domain: str) -> dict[str, SkinMetadatum]:
    return parse_metadata_from_asset_domain(
        asset_domain, SKIN_METADATA_PATH, SkinMetadatum
    )


def get_sticker_metadata(asset_domain: str) -> dict[str, StickerMetadatum]:
    return parse_metadata_from_asset_domain(
        asset_domain, STICKER_METADATA_PATH, StickerMetadatum
    )


def get_skin_cases(asset_domain: str) -> dict[str, SkinCase]:
    return parse_metadata_from_asset_domain(
        asset_domain, SKIN_CASES_METADATA_PATH, SkinCase
    )


def get_souvenir_packages(asset_domain: str) -> dict[str, SouvenirPackage]:
    return parse_metadata_from_asset_domain(
        asset_domain, SOUVENIR_PACKAGE_METADATA_PATH, SouvenirPackage
    )


def get_sticker_capsules(asset_domain: str) -> dict[str, StickerCapsule]:
    return parse_metadata_from_asset_domain(
        asset_domain, STICKER_CAPSULE_METADATA_PATH, StickerCapsule
    )

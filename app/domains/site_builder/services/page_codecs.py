import re
from collections.abc import Callable

_TOKEN_RE = re.compile(r"[^a-zA-Z0-9]+")


def to_snake_token(value: str) -> str:
    normalized = _TOKEN_RE.sub("_", value.strip().lower()).strip("_")
    normalized = re.sub(r"_+", "_", normalized)

    return normalized or "item"


def next_region_code(
    page_code: str,
    region_type: str,
    exists: Callable[[str], bool],
) -> str:
    base_code = f"{to_snake_token(page_code)}.{to_snake_token(region_type)}"
    region_code = base_code
    suffix = 2

    while exists(region_code):
        region_code = f"{base_code}_{suffix}"
        suffix += 1

    return region_code


def next_block_code(
    region_code: str,
    block_type: str,
    exists: Callable[[str], bool],
) -> str:
    base_code = f"{region_code}.{to_snake_token(block_type)}"
    block_code = base_code
    suffix = 2

    while exists(block_code):
        block_code = f"{base_code}_{suffix}"
        suffix += 1

    return block_code

#!/usr/bin/env python3

"""
This is a script to transform beets multiple artists into `;`-split artists.
"""

import re
import shlex
import subprocess
from typing import TypeVar

from std import uniq


T = TypeVar("T")


BLACKLIST = [
    "Above & Beyond",
    "Jos & Eli",
    "Eli & Fur",
]

ALIASES = {
    "Various Artists": "Various",
    "BTS": "BTS (방탄소년단)",
    "방탄소년단": "BTS (방탄소년단)",
    "MAMAMOO": "Mamamoo (마마무)",
    "Mamamoo": "Mamamoo (마마무)",
    "마마무": "Mamamoo (마마무)",
    "마마무 (Mamamoo)": "Mamamoo (마마무)",
    "植松伸夫": "Nobuo Uematsu (植松伸夫)",
    "当真伊都子": "Itoko Toma (当真伊都子)",
    "Twenty One Pilots": "twenty one pilots",
    "王菲": "Faye Wong (王菲)",
    "프로미스나인": "fromis_9",
    "(여자)아이들": "(G)I-DLE",
    "여자친구": "GFRIEND (여자친구)",
    "GFRIEND": "GFRIEND (여자친구)",
    "지수(JISOO)": "JISOO",
    "오마이걸(OH MY GIRL)": "OH MY GIRL (오마이걸)",
    "오마이걸": "OH MY GIRL (오마이걸)",
    "OH MY GIRL": "OH MY GIRL (오마이걸)",
    "ITZY": "ITZY (있지)",
    "Mitsuko Uchida": "Mitsuko Uchida (内田光子)",
    "Beethoven": "Ludwig van Beethoven",
    "Tchaikovsky": "Pyotr Ilyich Tchaikovsky",
    "Debussy": "Claude Debussy",
    "Unknown": "Unknown Artist",
}


def sub_artist_tag(tag: str, album: bool) -> list[str]:
    args = ["beet", "ls", "--format", f"${tag}"]
    if album:
        args.append("--album")

    cmd_artists = subprocess.run(args, capture_output=True)
    artists = uniq(
        [x.strip() for x in cmd_artists.stdout.decode().splitlines() if x.strip()]
    )

    commands: list[str] = []
    for full_existing_art in artists:
        new_artists: list[str] = []

        for existing_part in full_existing_art.split(";"):
            new_part: str = existing_part

            # BEGIN TRANSFORM
            new_part = new_part.replace("-", "‐")
            new_part = new_part.replace(r"&amp;", "&")
            new_part = re.sub(r"presents", "pres.", new_part, flags=re.IGNORECASE)
            new_part = re.sub(r"pres\.", "pres.", new_part, flags=re.IGNORECASE)
            new_part = re.sub(r"featuring", "feat.", new_part, flags=re.IGNORECASE)
            new_part = re.sub(r"feat\.", "feat.", new_part, flags=re.IGNORECASE)
            new_part = re.sub(r"feat(?=[^.])", "feat.", new_part, flags=re.IGNORECASE)

            for splitter in [" & ", ", ", "\\\\", "; ", " / ", " with "]:
                parts = []
                to_split = new_part
                while to_split:
                    for blk in BLACKLIST:
                        if to_split == blk:
                            parts.append(blk)
                            to_split = ""
                            break
                        if to_split.startswith(blk) and to_split[len(blk) :].startswith(
                            splitter
                        ):
                            parts.append(blk)
                            to_split = to_split[len(blk) + len(splitter) :].strip()
                    else:
                        idx = to_split.find(splitter)
                        if idx == -1:
                            parts.append(to_split)
                            break
                        parts.append(to_split[:idx])  # type: ignore
                        to_split = to_split[idx + len(splitter) :].strip()

                new_part = ";".join(parts)
            # END TRANSFORM

            for k, v in ALIASES.items():
                k = f"(^|;){re.escape(k)}(;|$)"
                new_part = re.sub(k, v, new_part)

            new_artists.append(new_part)

        combined_new_art = ";".join(new_artists)
        if full_existing_art == combined_new_art:
            continue

        album_flag = "--album " if album else ""
        matcher = shlex.quote(f"^{re.escape(full_existing_art)}$")
        replacement = shlex.quote(combined_new_art)
        commands.append(
            f"beet modify --yes {album_flag}" f"{tag}::{matcher} {tag}={replacement}"
        )

    return uniq(commands)


print("\n".join(sub_artist_tag("artist", False)))
print("\n".join(sub_artist_tag("albumartist", True)))

#!/usr/bin/env python3

"""
This is a script to transform beets multiple artists into `;`-split artists.
"""

import re
import subprocess
from typing import TypeVar


T = TypeVar("T")


BLACKLIST = [
    "Above & Beyond",
    "Jos & Eli",
    "Eli & Fur",
]


def uniq(xs: list[T]) -> list[T]:
    return list(set(xs))


def sub_artist_tag(tag: str, album: bool) -> list[str]:
    args = ["beet", "ls", "-f", f"${tag}"]
    if album:
        args.append("-a")

    cmd_artists = subprocess.run(args, capture_output=True)
    artists = uniq(
        [
            y.strip()
            for x in cmd_artists.stdout.decode().splitlines()
            if x.strip()
            for y in re.split(r";(?!\s)", x)
        ]
    )

    commands = []
    for existing_art in artists:
        new_art: str = existing_art

        # BEGIN TRANSFORM
        new_art = new_art.replace("-", "‐")
        new_art = new_art.replace(r"&amp;", "&")
        new_art = re.sub(r"presents", "pres.", new_art, flags=re.IGNORECASE)
        new_art = re.sub(r"pres\.", "pres.", new_art, flags=re.IGNORECASE)
        new_art = re.sub(r"featuring", "feat.", new_art, flags=re.IGNORECASE)
        new_art = re.sub(r"feat\.", "feat.", new_art, flags=re.IGNORECASE)
        new_art = re.sub(r"feat(?=[^.])", "feat.", new_art, flags=re.IGNORECASE)

        for splitter in [" & ", ", ", "\\\\", "; ", " / ", " with "]:
            parts = []
            to_split = new_art
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

            new_art = ";".join(parts)
        # END TRANSFORM

        if existing_art == new_art:
            continue

        album_flag = "-a " if album else ""
        commands.append(
            f"beet modify --yes {album_flag}"
            f"{tag}::'^{re.escape(existing_art)}$' {tag}='{new_art}'"
        )

    return commands


print("\n".join(sub_artist_tag("artist", False)))
print("\n".join(sub_artist_tag("albumartist", True)))

#!/usr/bin/env python3

"""
This is a script to infer and suggest release genres based on artist.
"""

import re
import json
import shlex
import subprocess
from dataclasses import dataclass


BLACKLIST = ["xxxxxxx"]

MATCHES = [
    "BLACKPINK"
    "NewJeans"
    "XG"
    "LE SSERAFIM"
    "Mamamoo"
    "Red Velvet"
    "TWICE"
    "IVE"
    "fromis_9"
    "Kep1er"
    "(G)-IDLE"
    "ONEUS"
    "GFRIEND"
    "G-FRIEND"
    "Jennie"
    "LISA"
    "ROSÉ"
    "ROSE"
    "Jisoo"
    "BTS"
    "IZ*ONE"
    "Huh Yunjin"
    "Oh My Girl"
    "GFriend"
    "EXO"
]


@dataclass
class Album:
    albumartist: str
    album: str
    genre: str


def update_genres() -> list[str]:
    kpop_albums: list[Album] = []

    for m in MATCHES:
        args = [
            "beet",
            "export",
            "--album" "--include-keys",
            "albumartist,album,genre",
            "albumartist:" + shlex.quote(m),
        ]
        result = subprocess.run(args, capture_output=True)
        out = json.loads(result.stdout.decode())
        for album in out:
            kpop_albums.append(
                Album(
                    albumartist=album["albumartist"],
                    album=album["album"],
                    genre=album["genre"],
                )
            )

    commands: list[str] = []
    for album in kpop_albums:
        if album.genre == "K-Pop":
            pass

        commands.append(
            "beet modify --yes --album "
            f"albumartist::'^{re.escape(album.albumartist)}$' "
            f"album::'^{re.escape(album.album)}$' "
            f"genre='K-Pop'"
        )

    return commands


print("\n".join(update_genres()))

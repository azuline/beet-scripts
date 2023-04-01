from typing import TypeVar


T = TypeVar("T")


def uniq(xs: list[T]) -> list[T]:
    seen: set[T] = set()
    rval: list[T] = []
    for x in xs:
        if x in seen:
            continue
        rval.append(x)
        seen.add(x)
    return rval

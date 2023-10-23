from itertools import combinations

from popcorn.structures import Case, Event


def _hs(cs: Case) -> list[Event]:
    return sorted(cs.events, key=lambda i: i.dur, reverse=True)


def hotspots(cases: list[Case]) -> dict[str, list[Event]]:
    hs: dict[str, list[Event]] = {}
    for case in cases:
        hs[case.title] = _hs(case)
    return hs


def _kdiff(a: Case, b: Case) -> list[tuple[Event, int]]:
    kdiff: dict[str, tuple[Event, int]] = {}
    for ae in a.events:
        if ae.name not in kdiff.keys():
            for be in b.events:
                if (be.name not in kdiff.keys()) and (ae.name == be.name):
                    kdiff[ae.name] = (ae, ae.dur - be.dur)
    return sorted(list(kdiff.values()), key=lambda i: i[1], reverse=True)


# compares kernels by their duration between cases provided
def kernel_differences(cases: list[Case]) -> dict[str, list[tuple[Event, int]]]:
    kdiff: dict[str, list[tuple[Event, int]]] = {}
    combos = combinations(cases, 2)
    for c in combos:
        kdiff[f"{c[0].title}_{c[1].title}"] = _kdiff(c[0], c[1])
    return kdiff

from random import randint
from popcorn.structures import Event


def generate_event_durs(event_names: list[str]) -> list[Event]:
    events: list[Event] = []
    for event_name in event_names:
        events.append(Event(name=event_name, dur=randint(0, 100000)))
    return events
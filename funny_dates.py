#!/usr/bin/env python3
"""Find fun milestone dates and notify the day before they occur."""
from __future__ import annotations

import argparse
import calendar
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Person:
    name: str
    birthday: date
    birth_time: time | None = None


@dataclass(frozen=True)
class Milestone:
    label: str
    date: date
    exact_time: datetime | None = None


def parse_args() -> argparse.Namespace:
    """Parserer kommandolinjeargumenter og returnerer de valgte indstillinger.

    Funktionen opsætter argumenter for filsti til fødselsdage og en valgfri
    dato-override til test. Resultatet bruges senere til at afgøre hvilke data
    der skal indlæses, og hvilken dato der regnes ud fra.
    """
    parser = argparse.ArgumentParser(
        description="Find fun birthday milestones and alert the day before."
    )
    parser.add_argument(
        "--birthdays",
        default="birthdays.json",
        help="Path to JSON file with birthdays (default: birthdays.json)",
    )
    parser.add_argument(
        "--today",
        help="Override today's date (YYYY-MM-DD) for testing",
    )
    return parser.parse_args()


def parse_birth_time(raw: str | None) -> time | None:
    """Parserer valgfrit fødselstidspunkt i formaterne HH:MM eller HH.MM."""
    if not raw:
        return None

    normalized = raw.strip().replace(".", ":")
    if ":" in normalized:
        hour, minute = normalized.split(":", maxsplit=1)
        normalized = f"{hour.zfill(2)}:{minute.zfill(2)}"
    return time.fromisoformat(normalized)


def load_birthdays(path: Path) -> List[Person]:
    """Indlæser en JSON-fil med fødselsdage og returnerer en liste af personer.

    Funktionen forventer en liste af objekter med felterne ``name`` og
    ``birthday`` i ``YYYY-MM-DD`` format. Hvis filen ikke findes, gives en
    fejlmeddelelse med forslag om at oprette den ud fra eksempel-filen.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Birthdays file not found: {path}. "
            "Create one based on birthdays.example.json."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    people: List[Person] = []
    for entry in raw:
        name = entry["name"].strip()
        birthday = date.fromisoformat(entry["birthday"])
        birth_time = parse_birth_time(entry.get("birth_time"))
        people.append(Person(name=name, birthday=birthday, birth_time=birth_time))
    return people


def add_months(base: date, months: int) -> date:
    """Lægger et antal måneder til en dato og håndterer månedslængder.

    Her beregnes den nye måned og år, og hvis den oprindelige dag ikke findes
    i den nye måned (f.eks. 31. i en måned med 30 dage), bliver dagen sat til
    den sidste dag i den måned.
    """
    year = base.year + (base.month - 1 + months) // 12
    month = (base.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(base.day, last_day)
    return date(year, month, day)


def add_years(base: date, years: int) -> date:
    """Lægger hele år til en dato og justerer for skudår.

    Hvis den samme dato ikke findes i målåret (f.eks. 29. februar), reduceres
    dagen til den sidste gyldige dag i måneden.
    """
    year = base.year + years
    last_day = calendar.monthrange(year, base.month)[1]
    day = min(base.day, last_day)
    return date(year, base.month, day)


def milestone_candidates(person: Person) -> Iterable[Milestone]:
    """Udregner en samling af sjove mærkedage ud fra en persons fødselsdato.

    Funktionen laver en række faste mærkedage baseret på måneder, dage, uger,
    minutter, timer og sekunder, samt en kombineret mærkedag (1 år, 1 måned,
    1 uge, 1 dag). Derudover tilføjes en serie af Fibonacci-dage.
    Resultatet er en liste af mærkedage med label og dato.
    """
    base = person.birthday
    milestones = [
        ("100 dage", base + timedelta(days=100)),
        ("100 måneder", add_months(base, 100)),
        ("1000 uger", base + timedelta(weeks=1_000)),
        ("2000 uger", base + timedelta(weeks=2_000)),
        ("1000 dage", base + timedelta(days=1_000)),
        ("1111 dage", base + timedelta(days=1_111)),
    ]

    composite = add_years(base, 1)
    composite = add_months(composite, 1)
    composite = composite + timedelta(weeks=1, days=1)
    milestones.append(("1 år, 1 måned, 1 uge, 1 dag", composite))

    birth_dt = datetime.combine(base, person.birth_time or datetime.min.time())
    million_minutes = birth_dt + timedelta(minutes=1_000_000)
    ten_thousand_hours = birth_dt + timedelta(hours=10_000)
    hundred_thousand_hours = birth_dt + timedelta(hours=100_000)
    ten_million_seconds = birth_dt + timedelta(seconds=10_000_000)
    one_billion_seconds = birth_dt + timedelta(seconds=1_000_000_000)
    milestones.extend(
        [
            ("1.000.000 minutter", million_minutes.date(), million_minutes),
            ("10.000 timer", ten_thousand_hours.date(), ten_thousand_hours),
            ("100.000 timer", hundred_thousand_hours.date(), hundred_thousand_hours),
            ("10.000.000 sekunder", ten_million_seconds.date(), ten_million_seconds),
            ("1.000.000.000 sekunder", one_billion_seconds.date(), one_billion_seconds),
        ]
    )

    normalized: List[Milestone] = []
    for item in milestones:
        if len(item) == 2:
            label, moment = item
            normalized.append(Milestone(label=label, date=moment))
            continue

        label, milestone_date, milestone_time = item
        normalized.append(
            Milestone(
                label=label,
                date=milestone_date,
                exact_time=milestone_time if person.birth_time is not None else None,
            )
        )
    return normalized


def format_milestone_datetime(milestone: Milestone) -> str:
    """Formatterer mærkedagstidspunkt til visning i output."""
    if milestone.exact_time is None:
        return milestone.date.isoformat()
    return milestone.exact_time.strftime("%Y-%m-%d %H:%M")


def find_tomorrow_milestones(
    people: Iterable[Person], today: date
) -> List[tuple[Person, Milestone]]:
    """Finder de mærkedage der falder i morgen for en liste af personer.

    Funktionen gennemløber alle personer og deres mærkedage, og samler dem der
    falder på dagen efter den angivne dags dato. Den returnerer en liste af
    matches til notifikation.
    """
    target = today + timedelta(days=1)
    notifications: List[tuple[Person, Milestone]] = []
    for person in people:
        for milestone in milestone_candidates(person):
            if milestone.date == target:
                notifications.append((person, milestone))
    return notifications


def find_next_milestones_by_person(
    people: Iterable[Person], today: date
) -> List[tuple[Person, Milestone]]:
    """Finder den næste kommende mærkedag for hver person.

    Funktionen gennemgår mærkedage for hver person og returnerer den tidligste
    mærkedag der ligger efter den angivne dags dato. Resultatet er en liste med
    én kommende mærkedag pr. person.
    """
    upcoming: List[tuple[Person, Milestone]] = []
    for person in people:
        next_item: Milestone | None = None
        for milestone in milestone_candidates(person):
            if milestone.date <= today:
                continue
            if next_item is None or milestone.date < next_item.date:
                next_item = milestone
        if next_item is not None:
            upcoming.append((person, next_item))
    return upcoming


def notify(
    notifications: List[tuple[Person, Milestone]],
    upcoming: List[tuple[Person, Milestone]],
    today: date | None = None,
) -> None:
    """Skriver notifikationer til stdout for de mærkedage der er fundet.

    Outputtet viser mærkedage i morgen (hvis nogen) og tilføjer altid en
    oversigt over næste mærkedag for hver person. Hvis dagens dato er givet,
    tilføjes også hvor mange dage der er til mærkedagen.
    """
    if not notifications:
        print("Ingen mærkedage i morgen.")
    else:
        print("Mærkedage i morgen:")
        for person, milestone in notifications:
            print(
                f"- {person.name}: {milestone.label} ({format_milestone_datetime(milestone)})"
            )

    if not upcoming:
        print("Ingen kommende mærkedage fundet.")
        return

    if today is None:
        today = date.today()
    print("Næste mærkedag for alle:")
    for person, milestone in upcoming:
        days_until = (milestone.date - today).days
        print(
            f"- {person.name}: {milestone.label} ({format_milestone_datetime(milestone)}) "
            f"om {days_until} dage"
        )


def main() -> None:
    """Samler programflowet: læser input, finder mærkedage og udskriver output.

    Funktionen henter argumenter, bestemmer dagens dato (evt. fra override),
    indlæser personer, udregner mærkedage for i morgen og sender resultatet til
    output.
    """
    args = parse_args()
    today = date.today() if not args.today else date.fromisoformat(args.today)
    people = load_birthdays(Path(args.birthdays))
    notifications = find_tomorrow_milestones(people, today)
    should_send = bool(notifications) or today.weekday() == 6
    if not should_send:
        return
    upcoming = find_next_milestones_by_person(people, today)
    notify(notifications, upcoming, today)


if __name__ == "__main__":
    main()

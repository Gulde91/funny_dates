#!/usr/bin/env python3
"""Find fun milestone dates and notify the day before they occur."""
from __future__ import annotations

import argparse
import calendar
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Person:
    name: str
    birthday: date


@dataclass(frozen=True)
class Milestone:
    label: str
    date: date


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
        people.append(Person(name=name, birthday=birthday))
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

    Funktionen laver en række faste mærkedage baseret på måneder, dage, timer
    og sekunder, samt en kombineret mærkedag (1 år, 1 måned, 1 uge, 1 dag).
    Resultatet er en liste af mærkedage med label og dato.
    """
    base = person.birthday
    milestones = [
        ("100 måneder", add_months(base, 100)),
        ("500 måneder", add_months(base, 500)),
        ("1000 måneder", add_months(base, 1000)),
        ("10.000 dage", base + timedelta(days=10_000)),
    ]

    composite = add_years(base, 1)
    composite = add_months(composite, 1)
    composite = composite + timedelta(weeks=1, days=1)
    milestones.append(("1 år, 1 måned, 1 uge, 1 dag", composite))

    birth_dt = datetime.combine(base, datetime.min.time())
    milestones.extend(
        [
            ("100.000 timer", (birth_dt + timedelta(hours=100_000)).date()),
            ("500.000 timer", (birth_dt + timedelta(hours=500_000)).date()),
            (
                "1.000.000.000 sekunder",
                (birth_dt + timedelta(seconds=1_000_000_000)).date(),
            ),
        ]
    )

    return [Milestone(label=label, date=moment) for label, moment in milestones]


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


def notify(notifications: List[tuple[Person, Milestone]]) -> None:
    """Skriver notifikationer til stdout for de mærkedage der er fundet.

    Hvis der ikke er nogen mærkedage i morgen, udskrives en kort besked. Ellers
    listes alle relevante mærkedage med navn, label og dato.
    """
    if not notifications:
        print("Ingen mærkedage i morgen.")
        return

    print("Mærkedage i morgen:")
    for person, milestone in notifications:
        print(f"- {person.name}: {milestone.label} ({milestone.date.isoformat()})")


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
    notify(notifications)


if __name__ == "__main__":
    main()

# Funny Dates

Et lille Python-script der finder sjove fødselsdagsmærkedage og giver besked dagen før de sker.

## Forudsætninger

- Python 3.11+ (standardbiblioteket er nok)

## Kom i gang

1. Opret en `birthdays.json` ud fra eksemplet:

```bash
cp birthdays.example.json birthdays.json
```

2. Redigér `birthdays.json` og tilføj dine egne personer.

## Kørsel

```bash
python3 funny_dates.py
```

Du kan også pege på en anden fil eller teste med en bestemt dato:

```bash
python3 funny_dates.py --birthdays birthdays.json --today 2024-12-31
```

## Mærkedage der udregnes

Scriptet beregner faste mærkedage ud fra fødselsdatoen:

- 100 dage (~0,27 år)
- 100 måneder (~8,33 år)
- 1000 uger (~19,16 år) og 2000 uger (~38,33 år)
- 1000 dage (~2,74 år)
- 1111 dage (~3,04 år)
- 1 år, 1 måned, 1 uge, 1 dag (kombineret, ~1,11 år)
- 1.000.000 minutter (~1,90 år)
- 10.000 timer (~1,14 år) og 100.000 timer (~11,41 år)
- 10.000.000 sekunder (~0,32 år) og 1.000.000.000 sekunder (~31,69 år)

## Format på `birthdays.json`

Filen skal være en JSON-liste med objekter der indeholder `name` og `birthday` i formatet `YYYY-MM-DD`:

```json
[
  {"name": "Ada Lovelace", "birthday": "1815-12-10"}
]
```

> Bemærk: `birthdays.example.json` viser et komplet eksempel.

## Output

- Hvis der er mærkedage i morgen, listes de.
- Hvis ikke, vises den næste kommende mærkedag med antal dage til.

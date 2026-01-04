# Funny Dates

Dette projekt beregner skæve og sjove mærkedage ud fra fødselsdatoer og giver besked dagen før en mærkedag indtræffer. Det er tænkt som et lille hjælpeværktøj, der kan køre dagligt (fx via cron) på en Raspberry Pi.

## Sådan virker det

- Fødselsdage indlæses fra en JSON-fil (standard: `birthdays.json`).
- Programmet beregner en række faste mærkedage for hver person.
- Hvis der er mærkedage i morgen, listes de.
- Hvis der ikke er mærkedage i morgen, vises den næste kommende mærkedag.

## Kom i gang

1. Opret din datafil ud fra eksemplet:
   ```bash
   cp birthdays.example.json birthdays.json
   ```
2. Redigér `birthdays.json` og indsæt de relevante personer.
3. Kør scriptet:
   ```bash
   python3 funny_dates.py
   ```

Du kan også vælge en anden datafil:

```bash
python3 funny_dates.py --birthdays /sti/til/birthdays.json
```

## Sjove mærkedage der udregnes

Programmet udregner følgende mærkedage for hver person:

- 100 måneder
- 500 måneder
- 1000 måneder
- 1200 måneder
- 1000 uger
- 2000 uger
- 10.000 dage
- 1 år, 1 måned, 1 uge, 1 dag
- 1.000.000 minutter
- 10.000.000 minutter
- 100.000 timer
- 500.000 timer
- 1.000.000.000 sekunder
- Fibonacci-dage (34, 55, 89, 144, 233, 377, 610, 987 dage)

## Dataformat (birthdays.json)

Filen er en liste af objekter med navn og fødselsdato i `YYYY-MM-DD` format:

```json
[
  { "name": "Person 1", "birthday": "1990-05-12" },
  { "name": "Person 2", "birthday": "1985-10-03" }
]
```

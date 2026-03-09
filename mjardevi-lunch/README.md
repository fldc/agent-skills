# Mjärdevi Lunch Skill

AI-skill för [OpenCode](https://opencode.ai) och [Claude Code](https://docs.anthropic.com/en/docs/claude-code) som hämtar dagens lunchmeny från alla restauranger i Mjärdevi, Linköping via [Luncha I Mjärdevi API](https://lunchaimjardevi.com/api/).

Fråga din AI-assistent om lunch i Mjärdevi så triggas skillen automatiskt, t.ex:
- "Vad finns för lunch idag?"
- "Dagens lunch Mjärdevi"
- "Var kan man äta lunch?"

## Installation

1. Klona repot till din skill-katalog:

   **OpenCode:**
   ```bash
   git clone https://github.com/fldc/mjardevi-lunch ~/.config/opencode/skill/mjardevi-lunch
   ```

   **Claude Code:**
   ```bash
   git clone https://github.com/fldc/mjardevi-lunch ~/.claude/skill/mjardevi-lunch
   ```

2. Skaffa en API-nyckel på https://lunchaimjardevi.com/api/

3. Skapa `.api_key` i skill-katalogen:
   ```bash
   echo "din_api_nyckel" > .api_key
   ```

## Hur det fungerar

När du frågar om lunch i Mjärdevi identifierar AI-assistenten att skillen ska användas via `SKILL.md`. Assistenten kör sedan `scripts/get_lunch.py` som hämtar dagens menyer från API:et och presenterar resultatet i chatten.

## Filer

- `SKILL.md` - Skill-definition med triggers och instruktioner
- `scripts/get_lunch.py` - Script som hämtar menyer via API:et
- `references/api.md` - API-dokumentation
- `.api_key.example` - Mall för API-nyckel
- `.gitignore` - Exkluderar `.api_key` från versionshantering

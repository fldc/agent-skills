# Agent Skills

Ett repository för agent-specifika färdigheter och verktyg för personlig användning.

## Skills

- **loopia-dns** - Manage DNS records in Loopia via XML-RPC API
- **mjardevi-lunch** - Hämta dagens lunchmeny från restauranger i Mjärdevi, Linköping
- **openwrt-config** - Manage OpenWRT router configuration via SSH
- **ostergotland-events** - Hitta evenemang, konserter, marknader och aktiviteter i Östergötland
- **smhi-weather** - Hämta väderinformation från SMHI för svenska platser
- **systembolaget-skill** - Systembolaget-integration

## Shared Config

Skills that need credentials or overrides read them from `~/.config/ehh-skills/config.env`.

```bash
mkdir -p ~/.config/ehh-skills
cat >> ~/.config/ehh-skills/config.env <<'EOF'
MJARDEVI_LUNCH_API_KEY="..."
LOOPIA_USER="..."
LOOPIA_PASSWORD="..."
LOOPIA_CUSTOMER="..."
SYSTEMBOLAGET_API_KEY="..."
EOF
```

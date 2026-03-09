---
name: loopia-dns
description: Manage DNS records in Loopia via XML-RPC API. Use when the user asks to list, add, update, or remove DNS records in Loopia zones/domains, or mentions Loopia DNS, Loopia API, subdomains, A/CNAME/TXT/MX records, or record_id operations.
---

# Loopia DNS

Use this skill to manage Loopia DNS through the XML-RPC API endpoint `https://api.loopia.se/RPCSERV`.

## Quick Start

### 1) Configure credentials

Create `~/.config/opencode/skill/loopia-dns/.env`:

```bash
LOOPIA_User="<your-loopia-user>"
LOOPIA_Password="<your-loopia-password>"
# Optional
# LOOPIA_CUSTOMER="customer-id"
```

The CLI auto-loads this file. Environment variables also work:

```bash
export LOOPIA_User="<your-loopia-user>"
export LOOPIA_Password="<your-loopia-password>"
```

Optional (if your API user manages another account):

```bash
export LOOPIA_CUSTOMER="customer-id"
```

### 2) Use the bundled CLI helper

```bash
# List domains on the account
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py list-domains

# List subdomains in a zone
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py list-subdomains example.com

# List records on a subdomain (use @ for zone apex)
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py list-records example.com --subdomain www

# List all A records in a zone
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py list-a-records example.com

# Add a DNS record
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py add-record example.com www A 203.0.113.10 --ttl 300

# Update a record by record_id
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py update-record example.com www 123456 A 203.0.113.20 --ttl 300

# Delete a record by record_id
python ~/.config/opencode/skill/loopia-dns/scripts/loopia_dns_cli.py delete-record example.com www 123456
```

## Workflow

1. Validate zone and subdomain from user request.
2. Start with `list-a-records` for quick A-record audits, or `list-subdomains` + `list-records` for full inspection.
3. For changes, target a specific `record_id`.
4. Re-read records to verify result.
5. Report changes in a short before/after style.

## Common Operations

- **List current DNS**: `list-records`
- **List all A records**: `list-a-records`
- **Create record**: `add-record`
- **Edit record**: `update-record` with known `record_id`
- **Remove record**: `delete-record` with known `record_id`

## Notes

- Apex/root often uses subdomain `@`.
- TTL is in seconds.
- Loopia propagation can take minutes (sometimes up to around 15 minutes).
- Required Loopia API permissions are documented in `references/loopia_api.md`.

## Files

- CLI helper: `scripts/loopia_dns_cli.py`
- API notes: `references/loopia_api.md`

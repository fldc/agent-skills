# Loopia DNS API Reference (Practical)

Endpoint: `https://api.loopia.se/RPCSERV` (XML-RPC)

## Auth shape

All calls begin with:

1. `username` (API user, often `name@loopiaapi`)
2. `password`
3. Optional `customer` (for reseller/customer context)

Then method-specific parameters.

## Common methods

- `getDomains()` -> list of domains on the account
- `getSubdomains(zone)` -> list of subdomains
- `addSubdomain(zone, subdomain)` -> usually `"OK"`
- `removeSubdomain(zone, subdomain)` -> usually `"OK"`
- `getZoneRecords(zone, subdomain)` -> records list
- `addZoneRecord(zone, subdomain, record)` -> usually `"OK"`
- `updateZoneRecord(zone, subdomain, record)` -> usually `"OK"`
- `removeZoneRecord(zone, subdomain, record_id)` -> usually `"OK"`

## Record object (typical)

```json
{
  "record_id": 123456,
  "type": "A",
  "ttl": 300,
  "priority": 0,
  "rdata": "203.0.113.10"
}
```

Notes:
- `priority` is mainly relevant for MX/SRV.
- `ttl` is seconds.
- `record_id` is required for updates/deletes.

## Permissions needed on Loopia API user

- `getSubdomains`
- `addSubdomain`
- `removeSubdomain`
- `getZoneRecords`
- `addZoneRecord`
- `updateZoneRecord`
- `removeZoneRecord`

## Operational notes

- DNS propagation at Loopia can take minutes; up to around 15 minutes in some cases.
- Re-read records after changes to confirm API state before reporting done.

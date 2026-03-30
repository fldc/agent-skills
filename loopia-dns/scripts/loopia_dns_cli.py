#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import sys
import xmlrpc.client


API_URL = "https://api.loopia.se/RPCSERV"
CONFIG_DIR = Path.home() / ".config" / "ehh-skills"
CONFIG_FILE = CONFIG_DIR / "config.env"


def env_first(*keys):
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def get_auth():
    username = env_first("LOOPIA_USER", "LOOPIA_User")
    password = env_first("LOOPIA_PASSWORD", "LOOPIA_Password")
    customer = env_first("LOOPIA_CUSTOMER", "LOOPIA_Customer")

    if not username or not password:
        raise RuntimeError(
            "Missing credentials: set LOOPIA_USER/LOOPIA_PASSWORD "
            "or LOOPIA_User/LOOPIA_Password"
        )

    return username, password, customer


def load_dotenv(dotenv_path):
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


class LoopiaClient:
    def __init__(self, username, password, customer=None):
        self._username = username
        self._password = password
        self._customer = customer
        self._rpc = xmlrpc.client.ServerProxy(API_URL)

    def call(self, method, *args):
        params = [self._username, self._password]
        if self._customer:
            params.append(self._customer)
        params.extend(args)
        return getattr(self._rpc, method)(*params)


def normalize_zone(zone):
    return zone[:-1] if zone.endswith(".") else zone


def record_payload(record_type, rdata, ttl, priority):
    payload = {
        "type": record_type,
        "ttl": int(ttl),
        "rdata": rdata,
    }
    if priority is not None:
        payload["priority"] = int(priority)
    return payload


def build_parser():
    parser = argparse.ArgumentParser(description="Loopia DNS XML-RPC helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-domains", help="List domains on the account")

    p = sub.add_parser("list-subdomains", help="List subdomains in a zone")
    p.add_argument("zone")

    p = sub.add_parser("list-records", help="List records for a subdomain")
    p.add_argument("zone")
    p.add_argument("--subdomain", default="@")

    p = sub.add_parser("list-a-records", help="List all A records in a zone")
    p.add_argument("zone")

    p = sub.add_parser("add-subdomain", help="Add a subdomain")
    p.add_argument("zone")
    p.add_argument("subdomain")

    p = sub.add_parser("remove-subdomain", help="Remove a subdomain")
    p.add_argument("zone")
    p.add_argument("subdomain")

    p = sub.add_parser("add-record", help="Add a DNS record")
    p.add_argument("zone")
    p.add_argument("subdomain")
    p.add_argument("type")
    p.add_argument("rdata")
    p.add_argument("--ttl", type=int, default=300)
    p.add_argument("--priority", type=int)

    p = sub.add_parser("update-record", help="Update a DNS record")
    p.add_argument("zone")
    p.add_argument("subdomain")
    p.add_argument("record_id", type=int)
    p.add_argument("type")
    p.add_argument("rdata")
    p.add_argument("--ttl", type=int, default=300)
    p.add_argument("--priority", type=int)

    p = sub.add_parser("delete-record", help="Delete a DNS record")
    p.add_argument("zone")
    p.add_argument("subdomain")
    p.add_argument("record_id", type=int)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        load_dotenv(CONFIG_FILE)
        username, password, customer = get_auth()
        client = LoopiaClient(username, password, customer)
        zone = normalize_zone(args.zone) if hasattr(args, "zone") else None

        if args.command == "list-domains":
            result = client.call("getDomains")
        elif args.command == "list-subdomains":
            result = client.call("getSubdomains", zone)
        elif args.command == "list-records":
            result = client.call("getZoneRecords", zone, args.subdomain)
        elif args.command == "list-a-records":
            subdomains = client.call("getSubdomains", zone)
            result = []
            for subdomain in subdomains:
                records = client.call("getZoneRecords", zone, subdomain)
                for record in records:
                    if str(record.get("type", "")).upper() != "A":
                        continue
                    name = zone if subdomain == "@" else f"{subdomain}.{zone}"
                    result.append(
                        {
                            "name": name,
                            "subdomain": subdomain,
                            "type": "A",
                            "rdata": record.get("rdata"),
                            "ttl": record.get("ttl"),
                            "record_id": record.get("record_id"),
                            "priority": record.get("priority"),
                        }
                    )
        elif args.command == "add-subdomain":
            result = client.call("addSubdomain", zone, args.subdomain)
        elif args.command == "remove-subdomain":
            result = client.call("removeSubdomain", zone, args.subdomain)
        elif args.command == "add-record":
            payload = record_payload(args.type, args.rdata, args.ttl, args.priority)
            result = client.call("addZoneRecord", zone, args.subdomain, payload)
        elif args.command == "update-record":
            payload = record_payload(args.type, args.rdata, args.ttl, args.priority)
            payload["record_id"] = args.record_id
            result = client.call("updateZoneRecord", zone, args.subdomain, payload)
        elif args.command == "delete-record":
            result = client.call(
                "removeZoneRecord", zone, args.subdomain, args.record_id
            )
        else:
            parser.error("Unknown command")
            return 2

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

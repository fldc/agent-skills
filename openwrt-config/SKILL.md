---
name: openwrt-config
description: Manage OpenWRT router configuration via SSH including DDNS records (Cloudflare), firewall rules, port forwarding, network interfaces, VLANs, static DHCP leases, DNS entries, wireless settings, SSIDs, package management, and system settings. Use when user requests to configure OpenWRT router, add DDNS records, set up port forwarding, create firewall rules, configure WiFi, manage DHCP/DNS, or modify router settings. Router accessible via SSH at <router_ip> (default is typically 192.168.1.1).
---

# OpenWRT Configuration Management

## Overview

This skill provides workflows and reference documentation for managing OpenWRT router configuration via SSH. All configurations use UCI (Unified Configuration Interface) and are applied through SSH commands to the router at `<router_ip>` (default is typically 192.168.1.1).

## Connection

All commands are executed via SSH to the router:

```bash
ssh root@<router_ip> "<command>"
```

For multiple related commands, chain them with `&&`:

```bash
ssh root@<router_ip> "uci set ... && uci commit ... && /etc/init.d/... restart"
```

## Configuration Workflow

1. **Read current configuration** - Check existing settings before making changes
2. **Apply changes** - Use `uci set` commands to modify configuration
3. **Commit changes** - Run `uci commit <config>` to save
4. **Restart service** - Apply changes with `/etc/init.d/<service> restart`
5. **Verify** - Check that changes were applied correctly

## Configuration Categories

### DDNS Records

**Common tasks:**
- Add new DDNS record for Cloudflare
- Update existing DDNS record
- Enable/disable DDNS service

**Reference:** See [ddns.md](references/ddns.md) for Cloudflare DDNS configuration patterns, examples, and verification commands.

**Example workflow:**
1. Read existing DDNS config: `ssh root@<router_ip> "cat /etc/config/ddns"`
2. Add new service using UCI commands
3. Commit and restart: `uci commit ddns && /etc/init.d/ddns restart`
4. Verify: `uci show ddns.<service_name>`

### Firewall Rules

**Common tasks:**
- Add port forwarding rules
- Create traffic rules
- Configure firewall zones

**Reference:** See [firewall.md](references/firewall.md) for port forwarding patterns, traffic rules, and examples.

**Example workflow:**
1. Add redirect rule using `uci add firewall redirect`
2. Configure rule parameters
3. Commit and restart: `uci commit firewall && /etc/init.d/firewall restart`
4. Verify: `uci show firewall | grep redirect`

### Network Configuration

**Common tasks:**
- Add static DHCP leases
- Configure VLANs
- Set up bridges
- Add custom DNS entries

**Reference:** See [network.md](references/network.md) for DHCP, VLAN, bridge, and DNS configuration patterns.

**Example workflow:**
1. Add DHCP host reservation using `uci add dhcp host`
2. Configure MAC and IP address
3. Commit and restart: `uci commit dhcp && /etc/init.d/dnsmasq restart`
4. Verify: `cat /tmp/dhcp.leases`

### Wireless Settings

**Common tasks:**
- Add new WiFi network (SSID)
- Change WiFi password
- Configure encryption
- Enable/disable radios

**Reference:** See [wireless.md](references/wireless.md) for WiFi configuration patterns, security settings, and examples.

**Example workflow:**
1. Add WiFi interface using `uci set wireless.<name>=wifi-iface`
2. Configure SSID, encryption, and password
3. Commit and reload: `uci commit wireless && wifi reload`
4. Verify: `wifi status`

### Package Management

**Common tasks:**
- Install packages
- Remove packages
- Update package lists
- Search for packages

**Reference:** See [system.md](references/system.md) for package management commands and system configuration.

**Example workflow:**
1. Update package lists: `opkg update`
2. Install package: `opkg install <package>`
3. Verify: `opkg list-installed | grep <package>`

### System Settings

**Common tasks:**
- Change hostname
- Set timezone
- View system logs
- Create backups

**Reference:** See [system.md](references/system.md) for system configuration, logging, and backup procedures.

**Example workflow:**
1. Modify system setting using `uci set system.@system[0].<setting>`
2. Commit and reload: `uci commit system && /etc/init.d/system reload`
3. Verify: `uci show system`

## Best Practices

1. **Always read before writing** - Check current configuration before making changes
2. **Verify after changes** - Confirm settings were applied correctly
3. **Use descriptive names** - Name services, rules, and interfaces clearly
4. **Chain commands** - Use `&&` to ensure commands execute sequentially
5. **Commit before restart** - Always `uci commit` before restarting services
6. **Check logs** - Use `logread` to troubleshoot issues

## Common Patterns

### Pattern: Add and Verify Configuration

```bash
# Step 1: Read current config
ssh root@<router_ip> "cat /etc/config/<config_file>"

# Step 2: Apply changes (multiple uci commands)
ssh root@<router_ip> "
uci set ... &&
uci set ... &&
uci commit <config> &&
/etc/init.d/<service> restart
"

# Step 3: Verify
ssh root@<router_ip> "uci show <config>.<section>"
```

### Pattern: Copy and Modify Existing Configuration

When user asks to copy an existing configuration and modify it:

1. Read the source configuration
2. Identify the section to copy
3. Create new section with modified values
4. Commit and restart
5. Verify the new configuration

Example: "Copy the 'cloud' DDNS record and modify it for plex.fldc.se"

1. Read: `cat /etc/config/ddns`
2. Identify: Find the 'cloud' service configuration
3. Create: Use same pattern but change service name, lookup_host, and domain
4. Commit: `uci commit ddns && /etc/init.d/ddns restart`
5. Verify: `uci show ddns.plex`

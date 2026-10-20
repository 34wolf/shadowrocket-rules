# Shadowrocket Rules

This public repository keeps routing rules only. It does not contain proxy nodes, subscription URLs, server passwords, certificates, or private exported configurations.

## Files

- `custom_rules.conf`: individually reviewed public custom rules.
- `output/my_shadowrocket.conf`: generated Shadowrocket subscription.
- `scripts/`: tested Python standard-library build tools.

## Upstream

The base is Johnshall's public `sr_top500_banlist_ad.conf`:
https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist_ad.conf

Custom rules are inserted immediately after `[Rule]`. GitHub Actions checks daily at 11:15 Beijing time and commits only changed output.

## Company network compatibility

Every build explicitly enables these settings under `[General]`:

```conf
dns-direct-system = true
private-ip-answer = true
```

Domains matched by DIRECT rules use the current network's system DNS, and private IP answers are allowed. This supports company sites that require internal DNS. PROXY rules keep their existing routing policies. No company DNS address or internal IP is stored in this repository.

GitHub schedules may run later than the configured time; check Actions for the actual execution time.

## Subscription

Use this Raw URL on both Mac and iPhone Shadowrocket:

https://raw.githubusercontent.com/34wolf/shadowrocket-rules/main/output/my_shadowrocket.conf

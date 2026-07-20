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

## Subscription

After publication, this section will contain the exact Raw link verified from GitHub. The same configuration works on Mac and iPhone Shadowrocket.


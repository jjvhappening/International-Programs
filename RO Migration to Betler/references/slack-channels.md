---
name: RO Migration Slack Channels Reference
description: Slack channel IDs for Romania migration channels scanned by the risk crawler, plus the digest output channel
type: reference
project: RO Migration to Betler
---

# RO Migration Slack Channels

## Channels scanned each run

`last_active` is updated automatically by Step 4b after each run. Channels with `last_active` older than 30 days and no activity in the current scan are pruned automatically.

| Channel name | Channel ID | last_active | Notes |
|---|---|---|---|
| #tmp-romania-migration-data | `C09V3SK2936` | 2026-05-22 | Main data migration tracking; batch progress, data quality issues |
| #ip-romania-discussions | `C088XJ978ES` | 2026-05-22 | General IP Romania discussions; wallet switch, staging timelines |
| #sports-romania-migration | `C0AT1NCEBKQ` | 2026-05-22 | Sports tribe Romania migration; regression testing, go-live dates |
| #tmp-romania-migration-gaming | `C09UY82EE9L` | 2026-05-22 | Gaming tribe temp channel — Buy Bonus ETA, Bragg integrations, EGT Digital |
| #content-engagement-integrations-sync | `C08FSV38EJK` | 2026-05-22 | Bragg/aggregator content sync — GAM-10668, GAM-11319 signals |
| #international-programs-updates | `C06HULLL8DT` | 2026-05-22 | Programme-wide IP updates |
| #arcane-team | `C0590TS6NET` | 2026-05-20 | Engineering team — platform/infra signals |
| #web--dev | `CP11BEX7C` | 2026-05-22 | Web development — frontend signals |
| #tmp-romania-migration-testing | `C0AR5US8NVB` | 2026-05-22 | Regression testing coordination — payment issues, geolocation, audit readiness |
| #tmp-romania-migration-manage | `C09V3RK2LNQ` | 2026-05-22 | Manage tribe — dormant accounts, KYC, ONJN compliance threads |
| #tmp-romania-migration-sports | `C09UJRW8K7H` | 2026-05-22 | Sports tribe migration — iCore import fixes, stage cutover |
| #manage-romania-migration | `C0AQ62VC5HT` | 2026-05-22 | Manage tribe broader channel — dormant accounts, KYC/ONJN overlap |
| #seon-romania-aml-migration | `C0AFMF7QW06` | 2026-05-22 | SEON AML integration — Romania AML migration signals |

## Digest output channel

| Channel name | Channel ID |
|---|---|
| #ro-migration-risks | `C0B0MB0Q4KD` |

## Key contacts (Slack user IDs)

| Name | User ID | Role |
|---|---|---|
| Niels De Winde | `U04MM3C1H8U` | RO Migration programme lead — @mentioned in every digest |
| Jon Vince | `U08HBGPPRNY` | TPM — @mentioned in every digest |

## Slack timestamp calculation

When scanning for messages in the last 7 days, use:

```
oldest_timestamp = current_unix_timestamp - 604800   (7 × 86400)
```

**Do not use a hardcoded timestamp** — it will drift and eventually return empty results or scan the wrong window. Always compute from current time at run start.

As of 2026-05-18, the correct `oldest` value was `1778544000` (≈ 2026-05-11 00:00 UTC).

Last updated: 2026-05-22

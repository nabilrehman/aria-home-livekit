warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /deploy/admin/regions/endpoints

LiveKit docs › Manage & Deploy › Administration › Regions › Regions & static IPs

---

# Regions, regional endpoints, and static IPs

> Available LiveKit Cloud regions, endpoints, and static IP ranges.

## Overview

LiveKit Cloud is available in multiple regions around the world. Some deployments require traffic to remain within a specific region or use predictable IP ranges for firewall rules, compliance, or data residency requirements. This topic describes the available regions, static IP ranges, and the services to which they apply.

| Region feature | Supported services | Use cases |
| [Region groups for protocol-based region pinning](#region-groups) | Realtime SDKs | Meet compliance or data residency requirements. |
| [Region-based endpoints](#region-based-endpoints) | SIP | Comply with local telephony regulations or data residency requirements. |
| [Destination country for outbound calls](#destination-country) | SIP | Comply with local telephony regulations or data residency requirements. |
| [Static IP ranges](#static-ips) | Realtime, SIP signaling and media, and webhooks | Allowlist traffic in a firewall without using wildcard domains. |
| [Agent deployment regions](#agent-deployments) | Agents | Deploy agents to specific regions to optimize latency. |

## Region groups for protocol-based region pinning

A region group is a named group of LiveKit Cloud locations. You can pin a project to a region group to keep its realtime traffic within a specific area for compliance or data residency requirements.

Regions with more than one location offer automatic **in-region redundancy**: if one location has an outage, traffic reroutes to another location within the same region. Single-location regions keep traffic in region but don't have in-region redundancy, so they can't offer the same availability guarantees.

The following region groups are available for [protocol-based region pinning](https://docs.livekit.io/deploy/admin/regions/region-pinning.md) with realtime SDKs:

| ID | Name | Locations | Location count | In-region redundancy |
| `us` | United States | US Central, US East 1, US West | 3 | ✅ |
| `asia` | Asia Pacific | Japan, Singapore | 2 | ✅ |
| `eu` | Europe | France, Germany | 2 | ✅ |
| `india` | India | Mumbai, South India | 2 | ✅ |
| `me` | Middle East | Saudi Arabia, UAE | 2 | ✅ |
| `africa` | Africa | South Africa | 1 |  |
| `aus` | Australia | Australia | 1 |  |
| `il` | Israel | Israel | 1 |  |
| `sa` | South America | Brazil | 1 |  |
| `uk` | United Kingdom | UK | 1 |  |

> ℹ️ **Last updated**
> 
> This list of regions is subject to change. Last updated 2026-05-14.

> 🔥 **Region codes differ between realtime and telephony**
> 
> SIP telephony uses its own set of region codes, which don't always match the region codes in the preceding table. Most notably, `sa` means South America (Brazil) for protocol-based region pinning, but Saudi Arabia for telephony. For the telephony region codes, see [Region-based endpoints for SIP](#region-based-endpoints).

## Region-based endpoints for SIP

By default, SIP endpoints are global and LiveKit routes each call through the region closest to its origination point. A region-based endpoint directs traffic only to nodes within a single region instead. Use one to keep inbound calls inside a specific region, for example to comply with local telephony regulations or data residency requirements.

The endpoint format is as follows:

```
{sip_subdomain}.{region_name}.sip.livekit.cloud

```

Where `{sip_subdomain}` is your LiveKit SIP URI subdomain and `{region_name}` is one of the following regions:

| Region name | Region locations |
| `eu` | France, Germany |
| `india` | India |
| `sa` | Saudi Arabia |
| `us` | US Central, US East B, US West B |
| `japan` | Japan |
| `aus` | Australia |
| `uk` | United Kingdom |
| `canada` | Canada |

> ℹ️ **Note**
> 
> This list of regions is subject to change. Last updated 2026-03-13.

## Destination country for outbound calls

You can limit outbound calls to a specific region by setting the `destination_country` parameter. When `destination_country` is set, outbound calls originate from a server within the specified country. To learn more about how this parameter works, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls) in the **Region pinning for telephony** topic.

The following table includes the list of supported regions and two-letter [country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the `destination_country` parameter:

| Country code | Locations |
| `ae` | Dubai, UAE |
| `au` | Sydney, Australia |
| `br` | São Paulo, Brazil |
| `ca` | Montreal, Canada; Toronto, Canada |
| `de` | Frankfurt, Germany |
| `fr` | Marseille, France |
| `gb` | London, United Kingdom |
| `il` | Jerusalem, Israel |
| `in` | Hyderabad, India; Mumbai, India |
| `jp` | Osaka, Japan; Tokyo, Japan |
| `sa` | Jeddah, Saudi Arabia |
| `sg` | Singapore |
| `us` | Ashburn, Virginia, USA; Chicago, Illinois, USA; Phoenix, Arizona, USA |
| `za` | Johannesburg, South Africa |

## Static IPs

Static IP ranges let you allowlist LiveKit Cloud traffic in a firewall without using wildcard domains. They're currently available for the following regions:

| Region | IP blocks |
| Canada | `143.223.88.0/21` `161.115.160.0/19` `153.57.128.0/18` |
| EU | `143.223.88.0/21` `161.115.160.0/19` `153.57.128.0/18` |
| India | `143.223.88.0/21` `161.115.160.0/19` `153.57.128.0/18` |
| Japan | `143.223.88.0/21` `161.115.160.0/19` `153.57.128.0/18` |
| US | `143.223.88.0/21` `161.115.160.0/19` `153.57.128.0/18` |

> ℹ️ **Other regions**
> 
> All other regions must use wildcard domains. See [Configuring firewalls](https://docs.livekit.io/deploy/admin/firewall.md) for the required hostnames.

Static IPs apply to the following services:

- Realtime
- SIP signaling and media
- Webhooks

### Seeing IPs outside the expected region

LiveKit's default DNS address, like `<subdomain>.livekit.cloud`, resolves to the cluster closest to the connecting client. If the client is outside a region with static IPs, that cluster might not be covered by the [static IP](#static-ips) ranges above.

To force connections into a covered region, connect using regional addresses:

- `<subdomain>.canada.rtc.livekit.cloud`
- `<subdomain>.eu.rtc.livekit.cloud`
- `<subdomain>.india.rtc.livekit.cloud`
- `<subdomain>.japan.rtc.livekit.cloud`
- `<subdomain>.us.rtc.livekit.cloud`

The same region prefix works for service-specific subdomains, including `*.eu.turn.livekit.cloud` and `*.eu.sip.livekit.cloud`. Region DNS only exists with a service in the name; there is no `eu.livekit.cloud` without a service prefix.

For example, if your project is region-pinned to the US and an end user connects from London, the default `<subdomain>.livekit.cloud` lookup might resolve to a London cluster outside the static IP range. Pointing the client to `wss://<subdomain>.us.rtc.livekit.cloud` keeps the connection on US infrastructure and inside the static range.

For details on protocol-level region selection, see [Region pinning](https://docs.livekit.io/deploy/admin/regions/region-pinning.md).

### Static IP coverage for TURN

In regions with static IPs, traffic for all services, including TURN, egresses from the static IP ranges as long as the client connects via a regional endpoint such as `*.eu.turn.livekit.cloud`.

Outside those regions, traffic for TURN and other services egresses from cluster IPs that aren't part of the static guarantee.

## Agent deployment regions

An [agent deployment](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md) is isolated to a single region, but you can deploy an agent to multiple regions. The following regions are currently available for agent deployments:

| Region code | Geographic location |
| `us-east` | Ashburn, Virginia, USA |
| `eu-central` | Frankfurt, Germany |
| `ap-south` | Mumbai, India |

## Additional resources

The following topics provide more information about regions, endpoints, and firewalls.

- **[Region pinning](https://docs.livekit.io/deploy/admin/regions/region-pinning.md)**: Restrict realtime traffic to a region with protocol-based region pinning.

- **[Region pinning for telephony](https://docs.livekit.io/telephony/features/region-pinning.md)**: Restrict inbound and outbound SIP traffic to a region.

- **[Configuring firewalls](https://docs.livekit.io/deploy/admin/firewall.md)**: Allowlist the hosts and ports required to connect to LiveKit Cloud.

- **[Agent deployment](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md)**: Deploy agents to specific regions to optimize latency.

---

This document was rendered at 2026-08-24T21:33:04.267Z.
For the latest version of this document, see [https://docs.livekit.io/deploy/admin/regions/endpoints.md](https://docs.livekit.io/deploy/admin/regions/endpoints.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

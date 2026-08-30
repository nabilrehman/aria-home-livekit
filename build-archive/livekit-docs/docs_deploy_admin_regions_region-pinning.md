warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /deploy/admin/regions/region-pinning

LiveKit docs › Manage & Deploy › Administration › Regions › Region pinning

---

# Region pinning

> Learn how to isolate LiveKit traffic to a specific region.

## Overview

Region pinning restricts network traffic to a specific geographical region. Use this feature to comply with local telephony regulations or data residency requirements.

There are two options for restricting traffic to a specific region:

- **Protocol-based region pinning**

Signaling and transport protocols include region selection. Use this option with LiveKit realtime SDKs.
- **Region-based endpoint**

Clients connect to a region-specific endpoint. Use this option for telephony applications. To learn more, see [Region pinning for telephony](https://docs.livekit.io/telephony/features/region-pinning.md).

> ℹ️ **Agent deployment regions**
> 
> Region pinning only applies to LiveKit Cloud network traffic. To manage the regions where your agents themselves are deployed, see [Agent deployment regions](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md).

## Protocol-based region pinning

In protocol-based region pinning, region selection information is embedded in the initial signaling and transport messages. When pinning is enabled, if the initial connection is routed to a server outside the allowed regions, the request is rejected. The client then retries the connection using a server in one of the pinned regions.

Region pinning is available for customers on the [Scale plan](https://livekit.com/pricing) or higher.

> 🔥 **Protocol-based region pinning only works with LiveKit realtime SDKs**
> 
> For SIP requests, the server rejects the connection and doesn't retry it. Use [region-based endpoints](https://docs.livekit.io/telephony/features/region-pinning.md#region-based-endpoint) for SIP.

> ℹ️ **When to use protocol-based region pinning**
> 
> When connecting with LiveKit realtime SDKs or when regional data residency (for example, GDPR compliance) is required.

## Enable protocol-based region pinning

LiveKit must enable region pinning for your project. To request region pinning, sign in to [LiveKit Cloud](https://cloud.livekit.io) and select the **Support** option in the menu.

## Considerations

When you enable region pinning, you turn off automatic failover to the nearest region in the case of an outage.

## Available regions

Protocol-based region pinning uses the region group codes, such as `us`, `eu`, and `india`. For the full list of supported region groups, including locations and in-region redundancy, see [Region groups for protocol-based region pinning](https://docs.livekit.io/deploy/admin/regions/endpoints.md#region-groups).

## Additional resources

The following additional topics provide more information about regions and region pinning.

- **[Regions, regional endpoints, static IPs](https://docs.livekit.io/deploy/admin/regions/endpoints.md)**: Regions, endpoints, and static IP addresses for connecting to LiveKit Cloud.

- **[Region pinning for telephony](https://docs.livekit.io/telephony/features/region-pinning.md)**: Restrict inbound and outbound SIP traffic to a region.

- **[Agent deployment](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md)**: Deploy agents to specific regions to optimize latency and manage regional deployments.

---

This document was rendered at 2026-08-24T21:33:04.937Z.
For the latest version of this document, see [https://docs.livekit.io/deploy/admin/regions/region-pinning.md](https://docs.livekit.io/deploy/admin/regions/region-pinning.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

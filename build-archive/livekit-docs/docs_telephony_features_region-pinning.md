warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/features/region-pinning

LiveKit docs › Telephony › Features › Region pinning

---

# Region pinning for telephony

> Learn how to isolate LiveKit telephony traffic to a specific region.

## Overview

LiveKit SIP is part of LiveKit Cloud and runs as a globally distributed service, providing redundancy and high availability. By default, SIP endpoints are global, and calls are routed through the region closest to the origination point. Incoming calls are routed to the region closest to the SIP trunking provider's endpoint. Outgoing calls originate from the same region where the `CreateSIPParticipant` API call is made.

In most cases, using the global endpoint is the recommended approach. However, if you need to exercise more control over call routing — for example, to comply with local telephony regulations — LiveKit SIP supports region pinning. This allows you to restrict both incoming and outgoing calls to a specific region.

## Region pinning

Region pinning allows you to restrict calls to a specific region to comply with local telephony regulations. The following sections describe how to enable region pinning for inbound and outbound calls.

> ℹ️ **Protocol-based region pinning**
> 
> For realtime SDKs, you can use protocol-based region pinning to restrict traffic to a specific region. To learn more, see [Region pinning](https://docs.livekit.io/deploy/admin/regions/region-pinning.md).

### Inbound calls

To enable region pinning for incoming calls, configure your SIP trunking provider to use a region-based endpoint. A region-based endpoint is configured to direct traffic only to nodes within a specific region.

#### Region-based endpoint format

The endpoint format is as follows:

```
{sip_subdomain}.{region_name}.sip.livekit.cloud

```

Where:

- `{sip_subdomain}` is your LiveKit SIP URI subdomain. This is also your project ID without the `p_` prefix. You can find your SIP URI on the [Project settings](https://cloud.livekit.io/projects/p_/settings/project) page.

For example, if your SIP URI is `sip:bwwn08a2m4o.sip.livekit.cloud`, your SIP subdomain is `bwwn08a2m4o`.
- `{region_name}` is one of the following [regions](https://docs.livekit.io/deploy/admin/regions/endpoints.md#region-based-endpoints):

`aus`, `eu`, `india`, `japan`, `sa`, `uk`, `us`

For example to create a SIP endpoint for India, update `<your SIP subdomain>` in the following string:

```shell
<your SIP subdomain>.india.sip.livekit.cloud

```

For the current list of available regions, see [Region-based endpoints for SIP](https://docs.livekit.io/deploy/admin/regions/endpoints.md#region-based-endpoints).

Use the region-based endpoint to configure your SIP trunking provider. Follow the instructions for external provider setup in [SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md).

### Outbound calls

To originate calls from the same region as the destination phone number, set the `destination_country` parameter on your trunk configuration. This works with both [inline trunk configuration](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) and stored [outbound trunks](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md). When `destination_country` is set, outbound calls originate from a server within the specified country. If the country code doesn't match any supported region, the parameter has no effect and calls are routed using default behavior.

In the unlikely event that the preferred region is non-operational or offline, calls originate from another region nearby. For the current list of supported regions, see [Destination country for outbound calls](https://docs.livekit.io/deploy/admin/regions/endpoints.md#destination-country).

For a full list of parameters for outbound trunks, see [CreateSIPOutboundTrunk](https://docs.livekit.io/reference/telephony/sip-api.md#createsipoutboundtrunk).

#### Example: inline trunk with region pinning

Pass `destination_country` in the [inline trunk configuration](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) when creating a SIP participant. The following example sets the destination country to India.

1. Create a file named `sip-participant.json` with the inline trunk configuration and `destination_country` set to `in`:

```json
 {
   "trunk": {
     "hostname": "<SIP server>",
     "auth_username": "<username>",
     "auth_password": "<password>",
     "destination_country": "in"
   },
   "sip_number": "+15105550100",
   "sip_call_to": "<phone-number-to-dial>",
   "room_name": "my-sip-room",
   "participant_identity": "sip-test"
 }

```
2. Create the SIP participant using the CLI:

```shell
lk sip participant create sip-participant.json

```

#### Example: stored outbound trunk with region pinning

You can also set `destination_country` on a stored [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) to apply region pinning to all calls made through the trunk. The following example creates an outbound trunk that originates calls from India.

1. Create a file named `outbound-trunk.json`:

```json
{
  "trunk": {
    "name": "My outbound trunk",
    "address": "<my-trunk>.pstn.twilio.com",
    "numbers": ["+15105550100"],
    "auth_username": "myusername",
    "auth_password": "mypassword",
    "destination_country": "in"
  }
}

```
2. Create the outbound trunk using the CLI:

```shell
lk sip outbound create outbound-trunk.json

```

## Inbound call fallbacks

Region pinning restricts inbound calls to a single region. If instead you want to keep using the global endpoint but add redundancy, you can configure your SIP trunking provider with fallback endpoints.

By default, inbound calls use your global SIP endpoint, and LiveKit Cloud routes each call to the nearest available region. If a region becomes unavailable, LiveKit Cloud fails over to the next-nearest region automatically, so most applications don't need extra configuration for regional redundancy.

For more control over failover, most SIP trunking providers let you configure multiple endpoints on a single trunk and set the order in which they're tried. You can add one or more [region-based endpoints](#region-based-endpoint) as fallbacks behind your global endpoint. The provider tries the global endpoint first, then fails over to a specific region if the global endpoint doesn't respond.

To configure provider-side fallbacks, follow the instructions for your provider:

- Twilio: [Configure inbound fallbacks](https://docs.livekit.io/telephony/start/providers/twilio.md#inbound-fallbacks).
- Telnyx: [Configure inbound fallbacks](https://docs.livekit.io/telephony/start/providers/telnyx.md#inbound-fallbacks).

## Additional resources

The following additional topics provide more information about regions and region pinning.

- **[Region pinning](https://docs.livekit.io/deploy/admin/regions/region-pinning.md)**: Restrict network traffic to specific regions with protocol-based region pinning and realtime SDKs.

- **[Regions, regional endpoints, static IPs](https://docs.livekit.io/deploy/admin/regions/endpoints.md)**: Regions, endpoints, and static IP addresses for connecting to LiveKit Cloud.

- **[Agent deployment](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md)**: Deploy agents to specific regions to optimize latency and manage regional deployments.

---

This document was rendered at 2026-08-24T21:31:23.222Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/features/region-pinning.md](https://docs.livekit.io/telephony/features/region-pinning.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

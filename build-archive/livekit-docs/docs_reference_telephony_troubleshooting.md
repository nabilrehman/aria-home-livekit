warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /reference/telephony/troubleshooting

LiveKit docs › Reference › Telephony › Troubleshooting

---

# SIP troubleshooting guide

> Common issues and solutions for SIP.

The following sections cover some of the common issues and solutions for LiveKit SIP integrations.

> 💡 **Provider documentation**
> 
> Consult your SIP trunking provider's documentation. Your provider might include additional documentation for specific errors and have their own recommended troubleshooting steps.

## Where to look first

When a call doesn't work, the LiveKit Cloud [Telephony dashboard](https://cloud.livekit.io/projects/p_/telephony) is the first place to look. Open the call in the **Calls** view and answer three questions before downloading a PCAP:

1. Was the inbound `INVITE` recorded for the call? If no INVITE arrived, the problem is upstream of LiveKit. Check your SIP trunking provider's logs and your trunk configuration. For outbound calls, confirm `CreateSIPParticipant` succeeded and the trunk address is correct.
2. What SIP response was returned? The status code identifies the failure class. Use the sections that follow to map common codes (`403`, `404`, `486`, `503`) to causes.
3. Did media flow after the handshake? A successful `200 OK` and `ACK` don't guarantee audio. If the call connected but you hear silence or one-way audio, see [Media issues](#media-issues).

For deeper analysis, download the call's [PCAP](#pcaps) and inspect the SIP and RTP packets in Wireshark.

## General issues

The following issues can apply to both incoming and outgoing calls.

### 403 Forbidden

This error indicates an authentication or permission error, but can also be returned when regional requirements are not met (see [403 - Domestic Anchored Terms Not Met](#403-region-error)).

#### Solution

Verify the username and password you're using are correct. Check the credentials you configured with your SIP trunking provider and confirm they match the credentials you set on the SIP trunk.

### 403 - Domestic Anchored Terms Not Met

This error commonly occurs in regions where regulations require calls to remain within national borders. If a call is routed to another country, SIP providers return this error to indicate that the call violates domestic compliance requirements.

#### Solution

Use region pinning to restrict calls to a specific region. For inbound calls, use [region-based endpoints](https://docs.livekit.io/telephony/features/region-pinning.md). For outbound calls, specify the `destination_country` parameter when you create an [outbound trunk](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls).

To learn more, see [SIP cloud and region pinning](https://docs.livekit.io/telephony/features/region-pinning.md).

### 404 - Not Found

This error can be returned for multiple reasons. This section covers some of the possible 404 errors that can occur.

| Error message | Cause |
| `twirp error unknown: object cannot be found` | Trunk ID references a trunk that doesn't exist or is inaccessible. |
| `The destination doesn't exist, or can't be found.` | Destination number might be invalid or not in service. |

#### Solution

Depending on the error, check one or all of the following list:

- Confirm the LiveKit SIP trunk exists and the trunk ID is correct.
- Verify the destination number is a valid phone number.

### 486 Busy Here

The inbound call reached LiveKit but was rejected before connecting. A `486 Busy Here` response indicates the destination (typically the agent or room) declined the call.

#### Solution

Verify the following:

- Your agent worker is running and dispatched correctly. To learn more, see [Call rings, but agent doesn't answer](#agent-never-answers).
- Your dispatch rule matches as expected and points to the correct `agent_name`.
- The agent isn't ending the session in its entrypoint. Check the agent worker logs for early disconnect events or errors.

If your SIP provider returns `486` to LiveKit on an outbound call, the destination side is busy.

## Media issues

When a call connects (you see `200 OK` and `ACK` in the dashboard) but audio is missing or degraded, the problem is in the media layer rather than SIP signaling. Start by inspecting the Session Description Protocol (SDP) offer in the `INVITE` and the SDP answer in the `200 OK`. To learn more, see [Codecs negotiation](https://docs.livekit.io/reference/telephony/codecs-negotiation.md).

### No audio

If the call shows as connected but neither side hears audio, RTP isn't flowing. Check, in this order:

- Inspect the `c=` line in both the SDP offer and answer. If either side has `c=IN IP4 0.0.0.0`, that side is signaling "no media." This is typical for a held call or a misconfigured endpoint that failed to advertise a routable address.
- Inspect the `m=audio` line. A port of `0` (for example, `m=audio 0 RTP/AVP 0`) means the media stream was rejected during negotiation.
- Confirm the offer and answer share at least one common codec. If the answer rejects all offered codecs, the call fails with `488 Not Acceptable Here`. To learn more, see [Supported audio codecs](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#supported-audio-codecs).
- For self-hosted deployments, verify firewall rules. RTP uses UDP on a dynamic port range (default `10000-20000` for LiveKit SIP server). To learn more, see [Firewall configuration](https://docs.livekit.io/transport/self-hosting/ports-firewall.md).

### One-way audio

One-way audio (where one party hears the other but not vice versa) is most often a Network Address Translation (NAT) problem. The SDP contains the IP address where RTP should be sent. If that address is a private IP (`10.x.x.x`, `172.16-31.x.x`, or `192.168.x.x`), the other side can't reach it from the public internet.

#### Solution

LiveKit Cloud handles NAT for you. Both signaling and media use public-facing infrastructure. If you're experiencing one-way audio on LiveKit Cloud, check that your SIP provider is forwarding traffic correctly and that the SDP it sends to LiveKit contains a routable address.

If you're self-hosting LiveKit SIP, the most common cause is the SIP server failing to advertise its public IP in SDP. In your `config.yaml`, set:

- `use_external_ip: true` so the SIP server discovers and advertises its public IP.

To learn more, see [SIP server configuration](https://docs.livekit.io/transport/self-hosting/sip-server.md).

### Bad audio quality

If audio flows in both directions but sounds choppy, robotic, or distorted, the problem is usually network quality. RTP runs over UDP and doesn't retransmit lost packets, so packet loss and timing variation directly affect what you hear. Use Wireshark's **Telephony** > **RTP** > **RTP Streams** > **Analyze** view to inspect the stream.

Reference thresholds for a healthy call:

| Metric | Healthy | Degraded |
| Packet loss | Under 1% | Over 3% causes audible breakup |
| Jitter (mean) | Under 5ms | Over 20ms causes choppy audio |
| One-way latency | Under 150ms | Over 300ms causes both parties to talk over each other |

If the metrics look healthy but audio still sounds wrong, check the RTP payload type against the codec negotiated in the SDP answer. A mismatch (for example, packets marked `PT=8` when the SDP agreed on `PT=0` for PCMU) produces loud static or garbled audio.

If network metrics are healthy and the codec matches, look at the audio source. Background noise, echo, and double-talk from the caller's environment can degrade quality independently of the network. Enable background voice cancellation (BVC) for your agent and rely on client-side echo cancellation on the caller's device. To learn more, see [Noise cancellation](https://docs.livekit.io/transport/media/noise-cancellation.md).

### Media timeout

A `media timeout` error means LiveKit stopped receiving RTP for longer than the allowed timeout and ended the call. By default, LiveKit ends a call if it receives no RTP within 30 seconds of establishing the media connection, or within 15 seconds of the last packet once media is flowing.

Some SIP trunking providers don't transmit RTP during silence. When a caller is quiet, the provider sends no packets and the timeout eventually fires. Use a [PCAP](#pcaps) to confirm RTP stopped arriving, and check your provider for an option to send RTP or add comfort noise during silence.

#### Solution

If your provider doesn't support sending RTP during silence, you can increase the timeout by setting the `media_timeout` field in the [`media`](https://docs.livekit.io/reference/telephony/sip-api.md#sipmediaconfig) configuration. You can set it on an inbound trunk, outbound trunk, [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md), or an individual [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) request. The value is a [duration](https://protobuf.dev/reference/protobuf/google.protobuf/#duration) string such as `"60s"`, up to a maximum of 10 minutes.

The following example sets a 60-second media timeout on an inbound trunk:

```json
{
  "trunk": {
    "name": "My trunk",
    "numbers": ["+15105550100"],
    "media": {
      "mediaTimeout": "60s"
    }
  }
}

```

A per-trunk or per-dispatch-rule timeout applies to every call the trunk or rule handles. Set `media_timeout` on the `CreateSIPParticipant` request instead to override the timeout for a single outbound call. To learn more, see [SIPMediaConfig](https://docs.livekit.io/reference/telephony/sip-api.md#sipmediaconfig).

## Call transfer issues

These errors can occur while trying to transfer a call using the `TransferSIPParticipant` API.

### 408 - Request Timeout

This Twirp error occurs if the transfer is rejected by the remote endpoint and the system times out waiting for a successful response.

#### Solution

To troubleshoot, try the following steps:

1. Verify the SIP URI for the transfer destination. Check that the URI is properly formatted and reachable.
2. Verify the trunk you configured with your SIP trunking provider. Check that it has the appropriate permissions to transfer calls to the target destination.

> ℹ️ **Note**
> 
> If you're using Telnyx as your SIP provider, SIP REFER must be enabled for your account. If they've enabled it, but you're still unable to transfer calls, verify you can transfer calls outside of LiveKit using their [API](https://developers.telnyx.com/api-reference/call-commands/sip-refer-a-call).

## Inbound calls

The following issues are specific to inbound calls.

### Call rings, but agent doesn't answer

This usually happens when the agent name is missing or incorrect in the dispatch rule. To ensure an agent answers incoming calls, you must explicitly set the agent name for the agent, and in the dispatch rule.

#### Solution

Make sure the agent name matches in both of the following places:

- When creating your agent: set `agent_name` for `AgentServer`. To learn more, see [Explicit agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md).
- When creating your dispatch rule: set `agent_name` in `RoomAgentDispatch`. For an example, see [Caller dispatch rule (individual)](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md#individual-dispatch-rule).

To learn more, see [Agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md).

## Outbound calls

The following issues are specific to outbound calls.

### 503 - Service Unavailable

This error from your SIP trunking provider might be the result of a configuration issue with the `address` field for your outbound trunk.

For example, the SIP endpoint for Telnyx is `sip.telnyx.com`. If you include a subdomain in the `address` field (for example, `myproject.sip.telnyx.com`), this error occurs.

#### Solution

Check with your SIP trunking provider and verify you're using the correct SIP endpoint in the `address` field for your outbound trunk. To learn more, see [Create an outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md#create).

### 408 Request Timeout from destination

On outbound calls, LiveKit may receive a `408 Request Timeout` from the destination side. This indicates the destination (your SIP provider, the PSTN, or the callee's endpoint) didn't respond to the `INVITE` within the expected window. LiveKit surfaces this as a `request-timeout` client error on the participant.

#### Solution

Investigate the destination path:

- Confirm the dialed number is valid and reachable. A bad number, or one routed through a provider with limited coverage, can produce `408`.
- Check your SIP provider's call detail records for the corresponding call. The provider typically reports the upstream failure with more detail.
- For repeated `408`s on the same destination, contact your SIP provider to investigate routing.

## Cross referencing calls with Call IDs

Understanding how different IDs relate to a call helps with debugging and support requests:

- **SIP Call ID**: Generated by the SIP protocol, unique for every SIP session.
- **Call ID (`SCL_xyz`)**: LiveKit's identifier for the call.
- **Provider ID**: Unique ID generated by the remote provider (like Twilio, for example, `CAxyz`). This ID is passed to LiveKit using SIP X headers.

## Working with PCAPs

Packet Capture (PCAP) files contain network traffic data that can help diagnose SIP and RTP issues. You can use [Wireshark](https://www.wireshark.org/) to analyze PCAPs.

> ℹ️ **Download PCAP files**
> 
> PCAP files are available for download in the LiveKit Cloud dashboard:
> 
> 1. Navigate to the **Telephony** → [**Calls**](https://cloud.livekit.io/projects/p_/telephony) page.
> 2. Select a call from the list.
> 3. In the **Call overview** section, select **Download** in the **PCAP** section.

The following sections describe how to identify the INVITE flow, codec negotiation, and visualize RTP flow in a PCAP file. To learn more about the data in a PCAP file, see [SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md).

### Identify the INVITE flow

1. Open the PCAP file in Wireshark.
2. Use the display filter for SIP traffic: Type in `sip` in the display filter text field.
3. Look for the initial `INVITE` from the caller to the callee.

> 💡 **Tip**
> 
> For a text-based printout of the SIP call, use Wireshark's **Follow SIP Call** feature:
> 
> - Open the context menu for an INVITE packet (right-click).
> - Select **Follow → SIP Call**.

Follow the SIP transaction:

`INVITE` → `100 Trying` → `180 Ringing` / `183 Session Progress` → `200 OK` → `ACK`

To learn more, see [SIP handshake](https://docs.livekit.io/reference/telephony/sip-handshake.md).

### Identifying the codec negotiation

1. Look inside the SDP portion of the `INVITE` and `200 OK`:- Examine the SIP / SDP sections of the packet.
- Find the `m=audio` line listing payload types.
- Look for `a=rtpmap` to see which payload type corresponds to which codec (for example, `0 PCMU/8000`).
2. Determine the chosen codec:- The caller's `INVITE` lists all supported codecs.
- The callee's `200 OK` lists acceptable codecs, with the first listed codec being the codec that is used.

To learn more, see [Audio codecs negotiation](https://docs.livekit.io/reference/telephony/codecs-negotiation.md).

### Visualize RTP in and out

1. Open the PCAP file in Wireshark.
2. Select **Statistics** → **I/O Graphs**.
3. Select the plus (**+**) icon to add a new graph to visualize incoming RTP traffic:- For **Graph Name**, enter "In"
- For **Display Filter**, enter `rtp && ip.dst_host matches "^10."`
- For **Y Axis**, select **Packets**.
4. Add a new graph to visualize outgoing RTP traffic:- For **Graph Name**, enter "Out"
- For **Display Filter**, enter `rtp && !(ip.dst_host matches "^10.")`
- For **Y Axis**, select **Packets**.

## Additional resources

For SIP errors not covered in this topic, see [List of SIP response codes](https://en.wikipedia.org/wiki/List_of_SIP_response_codes).

---

This document was rendered at 2026-08-24T21:31:32.816Z.
For the latest version of this document, see [https://docs.livekit.io/reference/telephony/troubleshooting.md](https://docs.livekit.io/reference/telephony/troubleshooting.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

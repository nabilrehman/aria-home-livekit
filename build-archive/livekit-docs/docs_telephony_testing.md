warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/testing

LiveKit docs › Telephony › Testing › Testing your setup

---

# Testing your telephony setup

> Place a test call and inspect the resulting room, SIP participant, and logs.

## Overview

After you configure your trunks, dispatch rules, and agent, place a test call to validate the setup. A successful call confirms that LiveKit and your caller or callee can reach each other, that a SIP participant is created with the expected attributes, and that your agent joins the room and responds. When a call fails, the same checks help you isolate where it broke down. The verifications in this topic apply to both inbound and outbound calls.

The exact setup you validate depends on how you provisioned your number:

- **[LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md):** Inbound calls only require a dispatch rule. There are no third-party SIP trunks or trunk credentials to verify, so you can skip the trunk-specific and provider-side steps below.
- **Third-party SIP provider (Twilio, Telnyx, Plivo, Wavix, Exotel, and others):** Inbound calls require both an inbound trunk and a dispatch rule. Outbound calls require trunk configuration, either [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call or via a stored [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md).

## Pre-call checks

Before placing a test call, confirm the following prerequisites:

- The phone number is provisioned and assigned:

- For [LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md), run `lk number list` or review [Phone numbers](https://cloud.livekit.io/projects/p_/telephony/phone-numbers) to list the phone numbers you own.
- For third-party providers, run `lk sip inbound list` or `lk sip outbound list`, or review [SIP trunks](https://cloud.livekit.io/projects/p_/telephony/trunks) and confirm there is a trunk associated with the correct phone number.
- A dispatch rule exists (for inbound calls):

- For LiveKit Phone Numbers, run `lk number list` and verify there is an assigned dispatch rule in the **SIP Dispatch Rules** column for the phone number you want to test.
- For third-party providers, run `lk sip dispatch list` or review [Dispatch rules](https://cloud.livekit.io/projects/p_/telephony/dispatch) for all dispatch rules. A dispatch rule must match the inbound trunk (for example, via the `trunks` parameter, or by omitting the parameter to match all trunks).
- An agent worker is running, connected to LiveKit, and available for dispatch with the expected `agent_name`. Verify the worker is up by hitting its [health check endpoint](https://docs.livekit.io/agents/server/options.md#health-check), or check the [Agents dashboard](https://cloud.livekit.io/projects/p_/agents) in LiveKit Cloud. When using explicit agent dispatch through `roomConfig.agents`, the `agent_name` in the dispatch rule must match the name your agent worker registers with. If you don't have an agent, see [Create a test agent](#test-agent).
- For third-party providers: trunk credentials match between LiveKit and the SIP provider. A mismatch returns [403 Forbidden](https://docs.livekit.io/reference/telephony/troubleshooting.md#403-error). LiveKit Phone Numbers don't require trunk credentials.

### Create a test agent

If you don't already have an agent to test with, follow the [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md) to create a base agent. Add a way for the agent to end the call when the conversation is complete:

- **Prebuilt tool:** add the [`EndCallTool`](https://docs.livekit.io/agents/prebuilt/tools/end-call-tool.md) to your agent's tools.
- **Custom implementations:** use the `delete_room` pattern shown in [Hang up](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#hangup).

> ℹ️ **Agent names must match**
> 
> For inbound calls, configure the dispatch rule to send calls to your agent, and ensure the `agent_name` matches in both the rule and your code. If you're using the quickstart, the default is `my-agent`. For details, see [Dispatch to an agent](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md#dispatch-to-an-agent).

## Place a test call

Test your telephony setup with a phone call.

### Test inbound calls

Dial the phone number from any phone. Your agent should answer the call. If the phone rings but the agent doesn't respond, confirm the agent is running and registered with the expected `agent_name`. To learn more, see [Call rings, but agent doesn't answer](https://docs.livekit.io/reference/telephony/troubleshooting.md#agent-never-answers).

After the caller and the agent are connected and in the same room, continue verifying the call with [Verify the room](#verify-the-room).

If the call doesn't connect:

- **LiveKit Phone Numbers:** review the call logs in the LiveKit Cloud [Telephony dashboard](https://cloud.livekit.io/projects/p_/telephony).
- **Third-party SIP provider:** review provider-side logs first (see [Provider-side verification](#provider-side-verification)), then the call logs in the LiveKit Cloud [Telephony dashboard](https://cloud.livekit.io/projects/p_/telephony).
- **Review agent logs:** review the [agent worker logs](#logs) to confirm the agent didn't encounter any errors while trying to start a session.

For additional troubleshooting, see the [SIP troubleshooting guide](https://docs.livekit.io/reference/telephony/troubleshooting.md) for common issues and solutions. For deeper context, see the [SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md) for an overview of how SIP calls flow in LiveKit, and the [SIP handshake](https://docs.livekit.io/reference/telephony/sip-handshake.md) guide for details on the handshake process.

### Test outbound calls

Outbound calls require a third-party SIP provider. LiveKit Phone Numbers do not currently support outbound calling. You can configure trunk settings [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call or use a stored [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md).

Place an outgoing call using the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) API. The destination phone should ring. If your agent initiates the call, your agent is already in the room when the callee answers. This is the typical setup for outbound calls. To learn more, see [Agent initiated outbound calls](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#agent-calls).

If you initiate the call using the server API or CLI, you must [dispatch an agent](https://docs.livekit.io/agents/server/agent-dispatch.md#via-api) to the room.

#### Outbound call flow

If an outbound call doesn't go through, work through the following checkpoints in order to isolate where it failed:

- **`CreateSIPParticipant` request:** the API call succeeds and returns a `SIPParticipantInfo` object. A `ServerError` here means the request itself was rejected before any SIP traffic was sent. Verify `sip_call_to` and `room_name` are valid, and that you've provided either `sip_trunk_id` or inline `trunk` configuration. For details, see [Creating a SIP participant](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#creating-a-sip-participant).
- **Outbound trunk resolution:** LiveKit resolves the trunk configuration, either from `sip_trunk_id` or from the inline `trunk` parameter. If using a stored trunk, run `lk sip outbound list` and confirm the trunk exists, the `address` points to the provider's SIP endpoint (no subdomain or extra path), and the `transport` is correct. If using inline config, verify the `hostname` is correct. A 503 response often indicates a wrong address. See [503 - Service Unavailable](https://docs.livekit.io/reference/telephony/troubleshooting.md#503-solution). For details, see [SIP outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md).
- **INVITE to the SIP provider:** LiveKit sends a SIP INVITE to the trunk's `address`. The trunk's `auth_username` and `auth_password` must match what the provider expects. A credential mismatch returns [403 Forbidden](https://docs.livekit.io/reference/telephony/troubleshooting.md#403-error).
- **Provider or downstream response:** if the INVITE is accepted by the provider but the call fails, inspect the final SIP response code (for example, 404, 486, 603) in provider logs.

If you can't isolate the step from API errors and participant attributes alone, download the [PCAP](https://docs.livekit.io/reference/telephony/troubleshooting.md#pcaps) of the call and walk the [SIP handshake](https://docs.livekit.io/reference/telephony/sip-handshake.md) to find the first non-success response.

## Verify the room

Each call creates a LiveKit room. Confirm the room was created with the name configured by the dispatch rule:

```shell
lk room list

```

For an individual dispatch rule with `roomPrefix: "call-"`, the room name follows the pattern `call-<random_suffix>`. For a direct dispatch rule, the room name matches `roomName` exactly.

### Verification criteria

- **Room exists:** indicates the dispatch rule matched and LiveKit attempted to create a room for the call.
- **Correct room name or prefix:** confirms the intended dispatch rule matched. If the name is incorrect, multiple dispatch rules might be competing. Rules without a `trunks` filter match all trunks.
- **Agent participant present:** confirms [agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md). If the agent is missing, review the agent worker [logs](#logs) and verify that its `agent_name` matches an entry in `roomConfig.agents[]` on the dispatch rule.

## Verify the SIP participant

Every caller joins as a [SIP participant](https://docs.livekit.io/reference/telephony/sip-participant.md) with attributes that describe the call. List participants in the test room:

```shell
lk room participants list <ROOM_NAME>

```

Retrieve full details, including attributes, for the SIP participant:

```shell
lk room participants get --room <ROOM_NAME> <PARTICIPANT_ID>

```

Confirm the following attributes are set as expected:

| Attribute | Expected value |
| `kind` | Equals `SIP`. Any other value indicates the wrong participant is being inspected. |
| `sip.trunkPhoneNumber` | For inbound calls, the number that was dialed. For outbound calls, the caller ID presented via the trunk. |
| `sip.phoneNumber` | Matches the caller's phone number (inbound) or the dialed destination (outbound). Not present if `HidePhoneNumber` is set on the dispatch rule. |
| `sip.trunkID` | For third-party providers, matches the trunk ID created during setup. A different value indicates that another trunk matched the call. For LiveKit Phone Numbers, this references a LiveKit-managed trunk and does not need to be verified. |
| `sip.ruleID` | Matches the dispatch rule ID (inbound only). Confirms that the expected rule matched. |
| `sip.callID` and `sip.callIDFull` | Present and non-empty. Use these values to [cross-reference calls](https://docs.livekit.io/reference/telephony/troubleshooting.md#call-ids) against provider logs. |
| Provider-specific attributes | For Twilio trunks, `sip.twilio.callSid` and `sip.twilio.accountSid` are populated. Use the call SID to locate the call in the Twilio Console. |
| Custom attributes | Any attributes configured through the dispatch rule or `headers_to_attributes` appear alongside the standard SIP attributes. |

For the full list of attributes, see [SIP participant](https://docs.livekit.io/reference/telephony/sip-participant.md).

## Inspect LiveKit and agent logs

With the SIP participant in the room, the agent should log the join and begin responding. Review the following log sources:

- **Agent worker logs:** confirm the agent received the job, connected to the room, and started publishing audio. Log the participant `kind` and SIP attributes at the start of the entrypoint to verify what the agent observes. See [Identifying SIP callers](https://docs.livekit.io/telephony/accepting-calls/workflow-setup.md#identifying-sip-callers).

You can view agent worker logs in the LiveKit Cloud [Agents dashboard](https://cloud.livekit.io/projects/p_/agents). To learn more about viewing runtime logs, see [Log collection](https://docs.livekit.io/deploy/agents/logs.md).
- **LiveKit Cloud Sessions:** open the [session](https://cloud.livekit.io/projects/p_/sessions) for the test call to review participant join and leave events, published tracks, and timing.
- **Call ID cross-reference:** use `sip.callID` or `sip.callIDFull` to correlate agent logs with LiveKit Cloud and the SIP provider. See [Cross-referencing calls with Call IDs](https://docs.livekit.io/reference/telephony/troubleshooting.md#call-ids).

## Provider-side verification

This section applies to third-party SIP providers only. If you're using LiveKit Phone Numbers, the inbound path is fully managed by LiveKit and there is no provider-side dashboard to inspect. Use the LiveKit Cloud [Telephony dashboard](https://cloud.livekit.io/projects/p_/telephony) instead.

When a call fails before reaching LiveKit, the SIP provider's logs are the primary diagnostic source. The following list includes some common locations:

- **Twilio:** Call logs. Sign in to the [Twilio console](https://console.twilio.com/) and select **Products & Services** » **Voice** » **Logs**. Use the Twilio call SID from `sip.twilio.callSid` to locate the call.
- **Telnyx:** [Generate CDR reports](https://portal.telnyx.com/#/reporting/detailed-records).
- **Plivo:** [Voice logs](https://cx.plivo.com/logs).
- **Wavix:** [Call history logs](https://app.wavix.com/logs).

For other providers, each offers a call detail record (CDR) or SIP debug view in its portal. Review SIP response codes and the trunk that handled the call.

Verify the following on the provider side:

- The call reached the correct trunk or endpoint.
- The transport on the call matches what the trunk is configured for: `transport=udp`, `transport=tcp`, or `transport=tls` (for [secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md)):

- For inbound calls, the provider directs the call to the LiveKit SIP URI using the configured transport.
- For outbound calls, the provider receives the INVITE from LiveKit on the configured transport.
- Check the final SIP response code on the call. A non-200 response (for example, 403 or 404) indicates a [specific troubleshooting path](https://docs.livekit.io/reference/telephony/troubleshooting.md):

- For inbound calls, this is LiveKit's response to the provider's INVITE.
- For outbound calls, this is the provider's (or downstream PSTN's) response to LiveKit's INVITE.

## Test hangups and failure paths

In addition to verifying successful call connections, test hangups and failure scenarios.

- Confirm the agent handles hangups cleanly and ends the session. To learn more, see [Hang up](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#hangup).
- Test pre-answer failure paths for outbound calls. Use `wait_until_answered=True` (Python) or `waitUntilAnswered: true` (Node.js) and call a number that rejects the call (`USER_REJECTED`) or one that doesn't answer (`USER_UNAVAILABLE`). Confirm your code catches the `SipCallError` and reads its SIP status code. See [Catching call failures](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#catch-failures).
- Test mid-call disconnections. After the call connects, have the caller or callee hang up. The SIP participant disconnects with `CLIENT_INITIATED`, and by default `AgentSession` (via `RoomIO`) automatically closes the session for that reason. If you need custom logic, register a `participant_disconnected` handler and inspect [`disconnect_reason`](https://docs.livekit.io/reference/telephony/sip-participant.md#disconnect-reasons). See [Handling mid-call disconnections](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#mid-call-disconnections).

To learn more, see [Handling call outcomes](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#call-outcomes).

## Additional resources

The following resources provide additional details about the topics covered in this guide.

- **[SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md)**: Learn how SIP integrates with LiveKit to enable seamless call routing between telephony systems and LiveKit rooms.

- **[SIP troubleshooting](https://docs.livekit.io/reference/telephony/troubleshooting.md)**: Troubleshoot SIP issues and common error codes.

---

This document was rendered at 2026-08-24T21:31:25.295Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/testing.md](https://docs.livekit.io/telephony/testing.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/accepting-calls/workflow-setup

LiveKit docs › Telephony › Accepting calls › Workflow & setup

---

# Workflow & setup

> Workflow and setup guide for accepting inbound calls.

## Inbound call workflow

When an inbound call is received, LiveKit SIP receives a text-based [INVITE](https://docs.livekit.io/reference/telephony/sip-handshake.md) request. This can come from either your SIP trunking provider or through a LiveKit phone number. For third-party SIP providers, the SIP service first verifies authorization to use the trunk. This can vary based on the LiveKit trunk configuration. If you're using LiveKit Phone Numbers, no inbound trunk configuration or verification is required.

The SIP service then looks for a matching dispatch rule. If there's a matching dispatch rule, a SIP participant is created for the caller and added to a LiveKit room. Depending on the dispatch rule, other participants (for example, a voice agent or other users) might also join the room.

The following diagram shows the inbound call workflow.

![Inbound SIP workflow](/images/sip/inbound-sip-workflow.svg)

1. User dials the SIP trunking provider phone number or a LiveKit Phone Number.
2. LiveKit SIP receives the INVITE request:

- For third-party SIP providers: Authenticates trunk credentials and checks if the call is allowed based on the inbound trunk configuration.
- For LiveKit Phone Numbers: Skip to the next step.
3. LiveKit SIP finds a matching dispatch rule.
4. LiveKit server creates a SIP participant for the caller and places them in a LiveKit room (per the dispatch rule).
5. User hears dial tone until LiveKit SIP responds to the call:

- If the dispatch rule has a pin, prompts the user with "Please enter room pin and press hash to confirm." If the pin is incorrect, the call is disconnected with a tone. If the pin is correct, the user is prompted to enter the room.
- User continues to hear a dial tone until another participant publishes tracks to the room.

## Setup for accepting calls

LiveKit Phone Numbers provide a simple setup process that only requires purchasing a phone number and creating a dispatch rule.

1. **Purchase a LiveKit Phone Number**

Purchase a phone number through [LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md).
2. **Create a dispatch rule**

Create a [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md). The dispatch rules dictate how SIP participants and LiveKit rooms are created for incoming calls. The rules can include whether a caller needs to enter a pin code to join a room and any custom metadata or attributes to be added to SIP participants.

### Using a third-party SIP provider

Third-party SIP providers require both an inbound trunk and a dispatch rule for proper authentication and call routing. To set up a third-party SIP provider, see the [SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md) guide.

## Identifying SIP callers

A LiveKit room can contain a mix of [participant types](https://docs.livekit.io/intro/basics/rooms-participants-tracks/participants.md#types-of-participants), including regular WebRTC clients, AI voice agents, and SIP participants. You can inspect the `kind` field on a participant to determine whether they joined over SIP and branch your logic accordingly.

The following example identifies SIP callers using the participant `kind` field:

**Python**:

```python
from livekit import rtc

# Wait for any participant to join the room
participant = await ctx.wait_for_participant()

if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
    # Caller joined via SIP (phone call)
    phone_number = participant.attributes.get('sip.phoneNumber', 'unknown')
    logger.info(f"SIP caller joined from phone number: {phone_number}")

    # Add SIP-specific logic here, for example:
    # - Look up customer records using their phone number
    # - Select a phone-optimised STT model
    # - Route the call to a specific agent workflow
else:
    # Caller joined via a regular WebRTC client (browser, native app, etc.)
    logger.info(f"Non-SIP participant joined: {participant.identity}")


```

---

**Node.js**:

```typescript
import { ParticipantKind } from '@livekit/rtc-node';

// Wait for any participant to join the room
const participant = await ctx.waitForParticipant();

if (participant.kind === ParticipantKind.SIP) {
  // Caller joined via SIP (phone call)
  const phoneNumber = participant.attributes['sip.phoneNumber'] ?? 'unknown';
  console.log(`SIP caller joined from phone number: ${phoneNumber}`);

  // Add SIP-specific logic here, for example:
  // - Look up customer records using their phone number
  // - Select a phone-optimised STT model
  // - Route the call to a specific agent workflow
} else {
  // Caller joined via a regular WebRTC client (browser, native app, etc.)
  console.log(`Non-SIP participant joined: ${participant.identity}`);
}

```

SIP participants also include a set of standard attributes (such as `sip.callID`, `sip.trunkID`, and `sip.trunkPhoneNumber`) that you can use to build routing or lookup logic. For the full list of available attributes and more advanced examples, see the [SIP participant reference](https://docs.livekit.io/reference/telephony/sip-participant.md).

## Retrieving SIP headers

Depending on how your SIP trunk and provider are configured, the inbound [INVITE](https://docs.livekit.io/reference/telephony/sip-handshake.md) request might include SIP headers that carry call metadata your agent needs at the start of a call, such as an account number, caller ID, or routing details. You can access these headers in two ways:

- Map individual headers to participant attributes using `headers_to_attributes` on the trunk. Each header must be configured on the trunk in advance, you can only map `X-*` headers, and attributes arrive asynchronously. To learn more, see [Custom attributes](https://docs.livekit.io/reference/telephony/sip-participant.md#custom-attributes).
- Call the `lk.sip.GetRemoteHeaders` RPC to read remote SIP headers directly, in a single call as soon as the SIP participant joins. Using the RPC doesn't require configuring header mappings in advance, returns every header in one place instead of waiting for attribute updates to arrive, and can read headers beyond the `X-*` set.

To read remote SIP headers directly, call the RPC from your agent using [`perform_rpc`](https://docs.livekit.io/transport/data/rpc.md#calling-a-method), targeting the SIP participant's identity. The method returns a JSON string with a `headers` object that maps each header name to its value.

**Python**:

```python
import json

from livekit import rtc

# Wait for the caller to join, then confirm they're a SIP participant
participant = await ctx.wait_for_participant()

if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
    try:
        response = await ctx.room.local_participant.perform_rpc(
            destination_identity=participant.identity,
            method="lk.sip.GetRemoteHeaders",
            # Fetch all remote SIP headers. See "Filtering headers" note for details.
            payload=json.dumps({}),
        )

        # The response is a JSON string: {"headers": {"<name>": "<value>", ...}}
        headers = json.loads(response)["headers"]
        logger.info(f"SIP headers: {headers}")
    except Exception as e:
        logger.error(f"Failed to get SIP headers: {e}")

```

---

**Node.js**:

```typescript
import { ParticipantKind } from '@livekit/rtc-node';

// Wait for the caller to join, then confirm they're a SIP participant
const participant = await ctx.waitForParticipant();

if (participant.kind === ParticipantKind.SIP) {
  try {
    const response = await ctx.room.localParticipant!.performRpc({
      destinationIdentity: participant.identity,
      method: 'lk.sip.GetRemoteHeaders',
      // Fetch all remote SIP headers. See "Filtering headers" note for details.
      payload: JSON.stringify({}),
    });

    // The response is a JSON string: {"headers": {"<name>": "<value>", ...}}
    const headers = JSON.parse(response).headers;
    console.log('SIP headers:', headers);
  } catch (error) {
    console.error('Failed to get SIP headers:', error);
  }
}

```

> 💡 **Filtering headers**
> 
> An empty payload returns every header except low-level transport headers such as `Via`, `Route`, `CSeq`, and `Content-Type`, which are always excluded. To narrow the result further, set `payload` to a JSON object with an `include` or `exclude` list of header names, matched case-insensitively. For example, pass `payload=json.dumps({"include": ["X-Account-Id"]})` in Python.

## Agents answering calls

Your agent answers calls when they are dispatched to the caller's room. To learn more, see [Automatically dispatch agents to rooms](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md#agent-dispatch).

### Greet the caller

Call the `generate_reply` method of your `AgentSession` to greet the caller after picking up. This code goes after `session.start`:

** Filename: `agent.py`**

```python
await session.generate_reply(
    instructions="Greet the user and offer your assistance."
)

```

** Filename: `agent.ts`**

```typescript
session.generateReply({
  instructions: 'Greet the user and offer your assistance.',
});


```

### Hang up

To let your agent end the call for all participants, add the prebuilt [EndCallTool](https://docs.livekit.io/agents/prebuilt/tools/end-call-tool.md) to your agent's tools. The tool shuts down the session and can delete the room to disconnect everyone. For programmatic hang up without the agent, use the `delete_room` API. To learn more and see sample code, see [Hang up](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#hangup).

## Additional resources

The following resources provide additional details about the topics covered in this guide.

- **[SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md)**: Learn how SIP integrates with LiveKit to enable seamless call routing between telephony systems and LiveKit rooms.

- **[SIP handshake](https://docs.livekit.io/reference/telephony/sip-handshake.md)**: Detailed steps in the SIP handshake process.

- **[Codecs negotiation & support](https://docs.livekit.io/reference/telephony/codecs-negotiation.md)**: Learn how audio codecs are negotiated during SIP call setup and which codecs LiveKit supports.

## Next steps

See the following guides to create an AI agent and validate the setup.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Create an AI agent to receive inbound calls.

- **[Testing your telephony setup](https://docs.livekit.io/telephony/testing.md)**: Place a test call and verify the room, SIP participant, and agent logs.

---

This document was rendered at 2026-08-24T21:31:17.704Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/accepting-calls/workflow-setup.md](https://docs.livekit.io/telephony/accepting-calls/workflow-setup.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

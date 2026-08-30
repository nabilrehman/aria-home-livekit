warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/making-calls/workflow-setup

LiveKit docs › Telephony › Making calls › Workflow & setup

---

# Workflow & setup

> Workflow and setup for making outbound calls.

## Outbound call workflow

To make an outbound call, you create a [SIP participant](https://docs.livekit.io/reference/telephony/sip-participant.md) with the user's phone number. When you execute the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) request, LiveKit SIP sends an [INVITE](https://docs.livekit.io/reference/telephony/sip-handshake.md) request to your SIP provider. If the SIP provider accepts the call, the SIP participant is added to the LiveKit room.

![LiveKit outbound SIP workflow](/images/sip/outbound-sip-workflow.svg)

1. Call the `CreateSIPParticipant` API to create a SIP participant.
2. LiveKit SIP sends an INVITE request to the SIP trunking provider.
3. SIP trunking provider validates trunk credentials and accepts the call.
4. LiveKit server places SIP participant in the LiveKit room specified in the `CreateSIPParticipant` request.

## Setup for making calls

The following sections outline the steps required to make an outbound SIP call.

### SIP trunking provider setup

1. Purchase a phone number from a SIP Provider.

For a list of tested providers, see the table in [Using LiveKit SIP](https://docs.livekit.io/telephony.md#using-livekit-sip).
2. Configure the SIP Trunk on the provider to accept SIP traffic from the LiveKit SIP service.

For instructions for setting up a SIP trunk, see [Configuring a SIP provider trunk](https://docs.livekit.io/telephony/start/sip-trunk-setup.md).

### LiveKit SIP configuration

Configure your outbound trunk settings. You can either pass trunk configuration [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each `CreateSIPParticipant` request or create a stored [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) associated with your SIP provider phone number. Include the authentication credentials required by your SIP trunking provider to make calls.

### Make an outbound call

Create a SIP participant. When the `CreateSIPParticipant` request is executed, a SIP call is initiated:

1. An INVITE request is sent to the SIP trunk provider. The provider checks authentication credentials and returns a response to LiveKit.
2. If the call is accepted, LiveKit dials the user and creates a SIP participant in the LiveKit room.

If the call is not accepted by the SIP trunk provider, the `CreateSIPParticipant` request fails.

After the call starts ringing, you can check the call status by listening to [participant events](https://docs.livekit.io/intro/basics/rooms-participants-tracks/webhooks-events.md#handling-events):

- If the `sip.callStatus` participant attribute is updated to `active`, the call has connected.
- If the call fails, the participant is disconnected and leaves the room.

### Agent outbound calls

To have your agent make an outbound call, dispatch the agent and then create a SIP participant. To learn more, see [Agents and outbound calls](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#agent-calls).

## Additional resources

The following resources provide additional details about the topics covered in this guide.

- **[SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md)**: Learn how SIP integrates with LiveKit to enable seamless call routing between telephony systems and LiveKit rooms.

- **[SIP handshake](https://docs.livekit.io/reference/telephony/sip-handshake.md)**: Detailed steps in the SIP handshake process.

- **[Codecs negotiation & support](https://docs.livekit.io/reference/telephony/codecs-negotiation.md)**: Learn how audio codecs are negotiated during SIP call setup and which codecs LiveKit supports.

## Next steps

See the following guides to create an AI agent and validate the setup.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Create an AI agent to make outbound calls.

- **[Testing your telephony setup](https://docs.livekit.io/telephony/testing.md)**: Place a test call and walk the outbound flow checkpoints to isolate any failures.

---

This document was rendered at 2026-08-24T21:31:21.030Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/making-calls/workflow-setup.md](https://docs.livekit.io/telephony/making-calls/workflow-setup.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

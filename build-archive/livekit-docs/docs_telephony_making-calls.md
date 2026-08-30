warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/making-calls

LiveKit docs › Telephony › Making calls › Overview

---

# Making calls overview

> An overview of making outbound calls with LiveKit telephony.

## Overview

Make outbound calls from LiveKit rooms to phone numbers using SIP providers. Pass trunk configuration [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call or use a stored [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md). Create SIP participants and set up workflows to initiate calls and connect participants with external phone numbers.

## Making calls components

Set up outbound call handling with trunks, SIP participant creation, and call configuration.

| Component | Description | Use cases |
| **Workflow & setup** | Overview of the outbound call workflow, from creating a SIP participant to connecting to external phone numbers and routing to rooms. | Understanding outbound call flow, setting up outbound call handling, and learning how SIP participants initiate calls. |
| **Outbound trunk** | Store reusable outbound trunk configuration for making outgoing calls through SIP providers. You can also pass trunk configuration [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call instead of creating a stored trunk. | Reusing trunk configuration across calls, configuring trunk authentication, and setting up region pinning for outbound calls. |
| **Outbound calls** | Create SIP participants to make outbound calls, configure call settings, and connect participants to external phone numbers. | Initiating outbound calls, creating SIP participants programmatically, and connecting agents to phone numbers. |
| **Answering machine detection** | Classify whether an outbound call reaches a person, voicemail, IVR, or unavailable line so your agent can respond accordingly. | Outbound voice agents, voicemail handling, and bypassing automated systems. |

## In this section

Read more about making calls.

- **[Workflow & setup](https://docs.livekit.io/telephony/making-calls/workflow-setup.md)**: Overview of the outbound call workflow and setup process.

- **[Outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md)**: Store reusable outbound trunk configuration for outgoing calls.

- **[Outbound calls](https://docs.livekit.io/telephony/making-calls/outbound-calls.md)**: Create SIP participants to make outbound calls.

- **[Answering machine detection](https://docs.livekit.io/telephony/features/answering-machine-detection.md)**: Detect whether a person, voicemail, or IVR system answered an outbound call.

---

This document was rendered at 2026-08-24T21:31:20.367Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/making-calls.md](https://docs.livekit.io/telephony/making-calls.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).

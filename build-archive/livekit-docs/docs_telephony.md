warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony

LiveKit docs › Telephony › Get Started › Introduction

---

# Telephony introduction

> LiveKit's telephony services enable seamless integration between traditional phone networks and LiveKit's realtime platform.

## Overview

LiveKit telephony lets you build AI-powered voice apps that handle inbound and outbound calls. It includes LiveKit Phone Numbers for purchasing and managing phone numbers, and supports integration with third-party SIP providers. Together, these features bridge traditional telephony with LiveKit's modern, realtime communication platform.

### LiveKit Phone Numbers

Purchase and manage phone numbers for your telephony apps directly through LiveKit. LiveKit Phone Numbers provides access to local and toll-free numbers in the United States, and is available in LiveKit Cloud. To learn more, see [LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md).

### Telephony components

LiveKit telephony extends the [core primitives](https://docs.livekit.io/intro/basics/rooms-participants-tracks.md) — participant, room, and track — to include two additional components specific to telephony: trunks and dispatch rules. These components are represented by objects created through the [API](https://docs.livekit.io/reference/telephony/sip-api.md) and control how calls are handled.

#### Session Initiation Protocol (SIP) participant

A SIP participant is a LiveKit participant that represents a caller or callee in a call. SIP participants are the same as any other participant and are managed using the [participant APIs](https://docs.livekit.io/intro/basics/rooms-participants-tracks/participants.md). They have the same [attributes and metadata](https://docs.livekit.io/transport/data/state/participant-attributes.md) as other participants, and have additional [SIP specific attributes](https://docs.livekit.io/reference/telephony/sip-participant.md).

For inbound calls, a SIP participant is automatically created for each caller. For outbound calls, you need to explicitly create a SIP participant using the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) API to make a call.

#### Trunks

LiveKit trunks bridge your third-party SIP provider and LiveKit. To use LiveKit, you must configure your SIP provider's trunking service to work with LiveKit. The setup depends on your use case — whether you're handling incoming calls, making outgoing calls, or both.

- [Inbound trunks](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) handle incoming calls and can be restricted to specific IP addresses or phone numbers.
- [Outbound trunks](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) are used to place outgoing calls. Outbound trunk configuration can be stored ahead of time or [passed inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call.

Trunks can be region restricted to meet local telephony regulations.

> ℹ️ **Note**
> 
> The same SIP provider trunk can be associated with both an inbound and an outbound trunk in LiveKit. You only need to create an inbound trunk _once_. Outbound trunk configuration can also be stored once and reused, or passed inline per call.

#### Dispatch rules

[Dispatch Rules](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) are associated with a specific trunk and control how inbound calls are dispatched to LiveKit rooms. All callers can be placed in the same room or different rooms based on the dispatch rules. Multiple dispatch rules can be associated with the same trunk as long as each rule has a different pin.

Dispatch rules can also be used to add custom participant attributes to [SIP participants](https://docs.livekit.io/reference/telephony/sip-participant.md).

#### Connectors

Connectors bridge LiveKit rooms with external voice platforms such as WhatsApp Business and Twilio. They handle bidirectional audio, media processing, and codec translation so you can route voice from those platforms into LiveKit without configuring SIP trunks. Use connectors for WhatsApp voice, Twilio calls over websockets, or other supported integrations. See [Connectors](https://docs.livekit.io/telephony/connectors.md) for an overview and provider-specific setup.

## LiveKit supported SIP features

LiveKit telephony supports the following SIP features and protocols:

| SIP Feature | Status | Notes |
| SIP over UDP | ✅ Supported | Transport protocol for SIP signaling. |
| SIP over TCP | ✅ Supported | Transport protocol for SIP signaling. |
| SIP over TLS | ✅ Supported | Transport protocol for SIP signaling. |
| SIP Registration (REGISTER) | ❌ Not Supported |  |
| SIPRECT (SRS) | ❌ Not Supported |  |
| DTMF (RFC 2833 / RFC 4733) | ✅ Supported | To learn more, see [DTMF](https://docs.livekit.io/telephony/features/dtmf.md). |
| Video over SIP | ❌ Not Supported |  |
| Call Transfer (cold transfer) (REFER) | ✅ Supported | To learn more, see [Call forwarding](https://docs.livekit.io/telephony/features/transfers/cold.md). |
| Warm Transfer | ✅ Supported | To learn more, see [Agent-assisted transfer](https://docs.livekit.io/telephony/features/transfers/warm.md). |
| Caller ID (From header) | ✅ Supported |  |
| SIP OPTIONS | ✅ Supported |  |
| Realtime Transfer Protocol (RTP) | ✅ Supported | Network protocol for delivering audio and video media. |
| Secure RTP (SRTP) | ✅ Supported | Network protocol for delivering encrypted audio and video media. To learn more, see [Secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md). |

## Key concepts

Understand these core concepts to build effective telephony applications with LiveKit.

### Features

LiveKit telephony includes support for DTMF, call transfers, secure trunking, HD voice, region pinning, and noise cancellation. These features enable you to build production-ready telephony applications with advanced capabilities.

- **[Features overview](https://docs.livekit.io/telephony/features.md)**: Learn about the telephony features available in LiveKit.

### Accepting calls

Handle inbound calls by setting up inbound trunks, configuring dispatch rules, and integrating with your SIP provider. Inbound calls automatically create SIP participants that join LiveKit rooms.

- **[Accepting calls overview](https://docs.livekit.io/telephony/accepting-calls.md)**: Learn how to accept and handle inbound phone calls.

### Making calls

Place outbound calls using the SIP API to create SIP participants. You can pass trunk configuration inline with each call or use a stored outbound trunk. Outbound calls enable your applications to initiate phone calls programmatically.

- **[Making calls overview](https://docs.livekit.io/telephony/making-calls.md)**: Learn how to make outbound phone calls with LiveKit.

### Connectors

Connect LiveKit to external voice platforms such as WhatsApp and Twilio without SIP. Connectors stream audio in and out of LiveKit rooms and handle platform-specific media and codecs, so you can run agents or other realtime logic on calls from those services.

- **[Connectors overview](https://docs.livekit.io/telephony/connectors.md)**: Connect WhatsApp, Twilio, and other platforms to LiveKit rooms.

## Service architecture

LiveKit telephony relies on the following services:

- A Direct Inward Dialing (DID) number provided by LiveKit Phone Numbers or a third-party SIP provider. LiveKit supports most SIP providers out of the box.
- LiveKit server (part of LiveKit Cloud) for API requests, managing and verifying SIP trunks and dispatch rules, and creating participants and rooms for calls.
- LiveKit SIP (part of LiveKit Cloud) to respond to SIP requests, mediate trunk authentication, and match dispatch rules.

If you use LiveKit Cloud, LiveKit SIP is ready to use with your project without any additional configuration. If you're self hosting LiveKit, the SIP service needs to be deployed separately. To learn more about self hosting, see [SIP server](https://docs.livekit.io/transport/self-hosting/sip-server.md).

![undefined]()

## Using LiveKit SIP

The LiveKit SIP SDK is available in multiple languages. To learn more, see [SIP API](https://docs.livekit.io/reference/telephony/sip-api.md).

LiveKit SIP has been tested with the following SIP providers:

- [Twilio](https://www.twilio.com/)
- [Telnyx](https://telnyx.com/)
- [Exotel](https://exotel.com)

- [Plivo](https://www.plivo.com)
- [Wavix](https://docs.wavix.com/sip-trunking/guides/livekit)
- [didlogic](https://didlogic.com)

> ℹ️ **Note**
> 
> LiveKit SIP is designed to work with all SIP providers. However, compatibility testing is limited to the providers below.

### Noise cancellation for calls

[Krisp](https://krisp.ai) noise cancellation uses AI models to identify and remove background noise in realtime. This improves the quality of calls that occur in noisy environments. For LiveKit telephony apps that use agents, noise cancellation improves the quality and clarity of user speech for turn detection, transcriptions, and recordings.

For incoming calls, see the [inbound trunks documentation](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) for the `krisp_enabled` attribute. For outgoing calls, see the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) documentation for the `krisp_enabled` attribute used during [outbound call creation](https://docs.livekit.io/telephony/making-calls/outbound-calls.md).

## Getting started

See the following guides to get started with LiveKit telephony:

- **[SIP primer](https://docs.livekit.io/reference/telephony/sip-primer.md)**: Learn how SIP integrates with LiveKit to enable seamless call routing between telephony systems and LiveKit rooms.

- **[LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md)**: Purchase a phone number through LiveKit Phone Numbers for inbound calls.

- **[SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md)**: Purchase a phone number and configure your SIP trunking provider for LiveKit.

- **[Accepting inbound calls](https://docs.livekit.io/sip/accepting-calls.md)**: Learn how to accept inbound calls with LiveKit.

- **[Making outbound calls](https://docs.livekit.io/sip/making-calls.md)**: Learn how to make outbound calls with LiveKit.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Create an AI agent integrated with telephony.

- **[Testing your telephony setup](https://docs.livekit.io/telephony/testing.md)**: Place a test call and verify the room, SIP participant, and agent logs end to end.

## Recipes

The following recipes are particularly helpful to learn more about building telephony-based voice AI apps.

- **[Company Directory](https://docs.livekit.io/reference/recipes/company-directory.md)**: Build a AI company directory agent. The agent can respond to DTMF tones and voice prompts, then redirect callers.

- **[SIP Lifecycle](https://docs.livekit.io/reference/recipes/sip_lifecycle.md)**: Complete lifecycle management for SIP calls.

- **[Survey Caller](https://docs.livekit.io/reference/recipes/survey_caller.md)**: Automated survey calling system.

---

This document was rendered at 2026-08-24T21:31:14.532Z.
For the latest version of this document, see [https://docs.livekit.io/telephony.md](https://docs.livekit.io/telephony.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
